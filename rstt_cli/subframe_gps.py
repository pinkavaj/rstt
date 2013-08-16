
from conv_tools import conv_fract
from struct import unpack


class SubframeGPS:
    class Satelite:
        def __init__(self, prn, status, meas):
            self.prn = prn
            self.sig_strength = status >> 4
            self.time_ok = bool(status & 0x08)
            self.prange_ok = bool(status & 0x04)
            self.prange_lock = bool(status & 0x02)
            self.doppler_lock = bool(status & 0x01)

            self.prange = conv_fract(meas[:4])
            self.doppler = conv_fract(meas[4:7])
            self.x = unpack('b', meas[7:8])[0]


    def __init__(self, data):
        time, d76, prn_data, status, meas = \
                data[0:4], data[4:6], data[6:14], data[14:26], data[26:]
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

        #dmin = min([s.doppler for s in stats if s.doppler not None])
        #for s in satelites:
        #    if s.prange is not None:
        #        s.prange -= dmin
