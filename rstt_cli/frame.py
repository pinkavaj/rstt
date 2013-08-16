#/usr/bin/python3

import crcmod
import struct


_int_min = -0x1400000
_int_max = (0x1400000-1)


def _int(data):
    """Convert 3/4 bytes in fract24 format into int."""
    if len(data) == 3:
        data = data + b'\x00'
    val = struct.unpack('<i', data)[0]
    if val > _int_max or val < _int_min:
        return None
    return val


def _fract(data):
    """Convert 3 or 4 byte in fract24 format to float."""
    val = _int(data)
    if val is None:
        return float('NAN')
    return float(val)


class GPS:
    class Sat:
        def __init__(self, prn, data_stat, data):
            self.prn = prn
            self.sig_strength = data_stat >> 4
            self.time_ok = bool(data_stat & 0x08)
            self.prange_ok = bool(data_stat & 0x04)
            self.prange_lock = bool(data_stat & 0x02)
            self.doppler_lock = bool(data_stat & 0x01)

            self.prange = _fract(data[:4])
            self.doppler = _fract(data[4:7])
            self.x = struct.unpack('b', data[7:8])[0]


    def __init__(self, data):
        self.time = struct.unpack("<i", data[0:4])[0]
        self.time = self.time / 1000. if self.time >= 0 else float('NAN')
        self.d76 = data[4:6] # TODO
        sat_prn_ = data[6:14]
        sat_prn = []
        while sat_prn_:
            lo, hi, sat_prn_ = sat_prn_[0], sat_prn_[1], sat_prn_[2:]
            sat_prn.append(lo & 0x1F)
            sat_prn.append((lo >> 5) | ((hi & 0x3) << 3))
            sat_prn.append(hi >> 2)

        self.sats = []
        for i in range(0, 12):
            sd = data[26+8*i:26+8*(i+1)]
            self.sats.append(self.Sat(sat_prn[i], data[14+i], sd))

        #dmin = min([s.doppler for s in stats if s.doppler not None])
        #for s in sats:
        #    if s.prange is not None:
        #        s.prange -= dmin


class Frame:
    def __init__(self, frame_data):
        self._data = frame_data
        self._crc = crcmod.mkCrcFun(0x11021, rev=False)
        self._parse()

    def get_calibration(self):
        if not self._crc1_ok:
            return None
        return (self._d_callibration_num, self._d_callibration_data, )

    def get_frame_num(self):
        if self._crc1_ok:
            return self._d_frame_num

    def _parse(self):
        self._data,  self._status = self._data[::2],  self._data[1::2]
        self._reed_solomon()
        self._check_crc()

        if self._crc1_ok:
            self._d_hdr = self._data[:8]
            self._d_frame_num = struct.unpack('<H', self._data[8:10])[0]
            self._d_id = struct.unpack('10s',  self._data[10:20])[0]
            self._d_15 = int(self._data[20]) # TODO
            self._d_hum_ch = (self._data[21] & 0x08) >> 3
            self._d_hum_heat = (self._data[21] & 0x04) >> 2
            self._d_16 = int(self._data[21]) & 0xF3 # TODO
            self._d_17 = int(self._data[22]) # TODO
            self._d_callibration_num = int(self._data[23])
            self._d_callibration_data = self._data[24:24+16]

        if self._crc2_ok:
            self._d_37 = int(self._data[42])
            self._d_38 = int(self._data[43])
            self._d_temp = _int(self._data[44:47])
            self._d_hum_up = _int(self._data[47:50])
            self._d_hum_down = _int(self._data[50:53])
            self._d_ch4 = _int(self._data[53:56])
            self._d_ch5 = _int(self._data[56:59])
            self._d_pressure = _int(self._data[59:62])
            self._d_ch7 = _int(self._data[62:65])
            self._d_ch8 = _int(self._data[65:68])

        if self._crc3_ok:
            self._d_gps = GPS(self._data[72:194])
        else:
            self._d_gps = None

        if self._crc4_ok:
            self._d_198 = self._data[198:208] # TODO

    def _reed_solomon(self):
        # TODO
        pass

    def _check_crc(self):
        crc = struct.unpack('<H',  self._data[40:42])[0]
        self._crc1_ok = (self._crc(self._data[8:40]) == crc)

        crc = struct.unpack('<H',  self._data[68:70])[0]
        self._crc2_ok = (self._crc(self._data[44:68]) == crc)

        crc = struct.unpack('<H',  self._data[194:196])[0]
        self._crc3_ok = (self._crc(self._data[72:194]) == crc)

        crc = struct.unpack('<H',  self._data[208:210])[0]
        self._crc4_ok = (self._crc(self._data[198:208]) == crc)

