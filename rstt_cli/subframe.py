import crcmod
from struct import unpack
from conv_tools import conv_fract, conv_int


SF_TYPE_CONFIG = 0x65
SF_TYPE_GPS = 0x67
SF_TYPE_MEASUREMENTS = 0x69
SF_TYPE_PADDING = 0xff
SF_TYPE_WTF1 = 0x68


class SubframeError(ValueError):
    """Report error on subframe parsing etc."""
    pass


class SubframeErrorLen(SubframeError):
    """Invalid data lenght (too short)."""
    pass


class SubframeErrorCorruptedData(SubframeError):
    """Subframe contains corrupted data byte."""
    pass


class SubframeErrorCRC(SubframeError):
    """Invalid subframe CRC."""
    pass


class Subframe(object):
    """General subframe routines, get data, length, check CRC."""

    _crc_fun = crcmod.mkCrcFun(0x11021, rev=False)

    def __init__(self, sf_type, sf_bytes, sf_status, _dbg):
        """sf_type - subframe type, sf_bytes - data bytes of subframe,
        sf_status - byte status (data reception errors."""
        self._dbg = _dbg
        if len(sf_bytes) != self.exp_len:
            _dbg("Unexpected subframe length: sf_type 0x%x, len: %d" %
                    (sf_type, len(sf_bytes), ))
        self.sf_type = sf_type
        self.sf_bytes = sf_bytes

    def __len__(self):
        if self.sf_type == 0xff:
            return len(self.sf_bytes) + 2
        else:
            return len(self.sf_bytes) + 4

    @classmethod
    def parse(self, data, sf_status, _dbg = lambda msg: None):
        if len(data) <= 2:
            raise SubframeErrorLen()
        if sf_status[0] or sf_status[1]:
            raise SubframeErrorCorruptedData()
        sf_type = data[0]
        flen = data[1] * 2
        if len(data) < flen + 2:
            raise SubframeErrorLen()
        if sum(sf_status[2:flen+2]):
            raise SubframeErrorCorruptedData()
        sf_bytes = data[2:flen+2]
        if sf_type != 0xff:
            if len(data) < 2 + flen + 2:
                raise SubframeErrorLen()
            if sf_status[flen+2] or sf_status[flen+3]:
                raise SubframeErrorCorruptedData()
            exp_crc = unpack('<H', data[flen+2:flen+4])[0]
            if not Subframe._check(sf_bytes, exp_crc):
                raise SubframeErrorCRC()
        subframe = {
            SubframeConfig.sf_type: SubframeConfig,
            SubframeGPS.sf_type: SubframeGPS,
            SubframeMeas.sf_type: SubframeMeas,
            SubframePadding.sf_type: SubframePadding,
            SubframeWTF1.sf_type: SubframeWTF1,
        }.get(sf_type, SubframeUnknown)
        return subframe(sf_type, sf_bytes, sf_status, _dbg)

    def _anounceInterest(self, msg):
        """Called when unexpected data arives (undecoded data).
        This function can be oweriden by superslass in order to debug data.
        Msg should be anything convertible to one line of text."""
        pass

    @classmethod
    def _check(self, sf_bytes, exp_crc):
        return self._crc_fun(sf_bytes) == exp_crc


class SubframePadding(Subframe):
    sf_type = SF_TYPE_PADDING
    exp_len = 4

    def __init__(self, sf_type, sf_bytes, sf_status, _dbg):
        Subframe.__init__(self, sf_type, sf_bytes, sf_status, _dbg)
        if sf_bytes != b'\x02\x00\x02\x00':
            _dbg("Unexpected padding: %s" % sf_bytes)


class SubframeConfig(Subframe):
    sf_type = SF_TYPE_CONFIG
    exp_len = 32

    def __init__(self, sf_type, sf_bytes, sf_status, _dbg):
        Subframe.__init__(self, sf_type, sf_bytes, sf_status, _dbg)
        self.frame_num, self.id, self.d12, self.d13, self.d14, \
                self.callibration_num, self.callibration_data = \
                unpack('<H10sBBBB16s', self.sf_bytes)
        self.battery_low = bool(self.d12 & 0x08)
        self.battery_killer_countdown = bool(self.d12 & 0x02)
        self.hum_channel = bool(self.d13 & 0x08)
        self.hum_heat = bool(self.d13 & 0x04)
        self.start_detected = ((self.d13 & 0x21) == 0x21)
        if self.start_detected:
            self.d13 = self.d13 & ~0x21

        self.d12 = self.d12 & ~0x0A
        self.d13 = self.d13 & ~0x0C
        if self.d12 or self.d13 or self.d14:
            self._dbg("Unexpected d12/d13/d14 value in subframe: %s" % sf_bytes)


class SubframeGPS(Subframe):
    sf_type = SF_TYPE_GPS
    exp_len = 122

    class Satelite:
        def __init__(self, prn, status, meas):
            self.prn = prn
            self.sig_strength = status >> 4
            self.time_ok = bool(status & 0x08)
            self.prange_ok = bool(status & 0x04)
            self.prange_lock = bool(status & 0x02)
            self.doppler_lock = bool(status & 0x01)

            self.prange = conv_fract(meas[:4]) / 1000. * 300
            """Apriximete conversion from chips to meters."""
            self.doppler = conv_fract(meas[4:7])
            self.x = unpack('b', meas[7:8])[0]

        def stat_ok(self):
            return self.time_ok and self.prange_ok and self.prange_lock and \
                    self.doppler_lock and self.prn

    def __init__(self, sf_type, sf_bytes, sf_status, _dbg):
        Subframe.__init__(self, sf_type, sf_bytes, sf_status, _dbg)
        time, d76, prn_data, status, meas = \
                self.sf_bytes[0:4], self.sf_bytes[4:6], self.sf_bytes[6:14], \
                self.sf_bytes[14:26], self.sf_bytes[26:]
        time = unpack("<i", time)[0] / 1000.
        self.time = time if time >= 0 else float('NAN')
        self.d76 = d76 # TODO
        prn = []
        while prn_data:
            lo, hi, prn_data = prn_data[0], prn_data[1], prn_data[2:]
            prn.append(lo & 0x1F)
            prn.append((lo >> 5) | ((hi & 0x3) << 3))
            prn.append(hi >> 2)

        self.satelites = []
        for i in range(0, 12):
            self.satelites.append(
                self.Satelite(prn[i], status[i], meas[8*i:8*(i+1)]))


class SubframeMeas(Subframe):
    sf_type = SF_TYPE_MEASUREMENTS
    exp_len = 24

    def __init__(self, sf_type, sf_bytes, sf_status, _dbg):
        Subframe.__init__(self, sf_type, sf_bytes, sf_status, _dbg)
        self.ch1 = self.temp = conv_int(self.sf_bytes[0:3])
        self.ch2 = self.hum_up = conv_int(self.sf_bytes[3:6])
        self.ch3 = self.hum_down = conv_int(self.sf_bytes[6:9])
        self.ch4 = conv_int(self.sf_bytes[9:12])
        self.ch5 = conv_int(self.sf_bytes[12:15])
        self.ch6 = self.pressure = conv_int(self.sf_bytes[15:18])
        self.ch7 = conv_int(self.sf_bytes[18:21])
        self.ch8 = conv_int(self.sf_bytes[21:24])

class SubframeUnknown(Subframe):
    sf_type = None
    exp_len = None
    def __init__(self, sf_type, sf_bytes, sf_status, _dbg):
        Subframe.__init__(self, sf_type, sf_bytes, sf_status, _dbg)
        _dbg("Unknown subframe type: 0x%x %s" % (sf_type, sf_bytes, ))


class SubframeWTF1(Subframe):
    sf_type = SF_TYPE_WTF1
    exp_len = 10

    def __init__(self, sf_type, sf_bytes, sf_status, _dbg):
        Subframe.__init__(self, sf_type, sf_bytes, sf_status, _dbg)
        if sf_bytes != b'\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00':
            _dbg("Unexpected contend in subframe 0x%x %s" % (sf_type, sf_bytes, ))

