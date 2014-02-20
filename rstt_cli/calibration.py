import struct

class CalibrationCollector(object):
    """Collect calibration data from fragments."""

    def __init__(self):
        self._missing = [True,  ] * 32
        self._fragments = [None, ] * 32
        self._data = None

    def addFragment(self, idx, data):
        """Process one subframe, with calibration data."""
        self._fragments[idx] = data
        self._missing[idx] = False
        return self.completed()

    def calibration(self):
        """Return processed calibration data."""
        return Calibration(self.data())

    def completed(self):
        """Return True if all fragments are collected."""
        if [x for x in self._missing if x]:
            return False
        return True

    def data(self):
        return b''.join(self._fragments)

class Calibration(object):
    """Parse calibration data."""
    def __init__(self, data):
        self._d_0 = data[0:2] # TODO
        self._d_freq = struct.unpack('<H', data[2:4])
        self._d_count_1 = struct.unpack('<H', data[4:6])
        self._d_6 = struct.unpack('<H', data[6:8]) # TODO
        self._d_8 = struct.unpack('<h', data[8:10]) # TODO
        self._d_10 = struct.unpack('<h', data[10:12]) # TODO
        self._d_id = struct.unpack('10c', data[22:32])[0].decode('ascii')
        self._d_block_32 = data[32:36] # TODO
        self._d_36 = struct.unpack('<7h', data[0x24:0x32]) # TODO
        self._d_50 = struct.unpack('<3h', data[0x32:0x38]) # TODO
        self._d_56 = data[56:64]
        self._d_f = {}
        for idx in range(64, 511-4, 5):
            ch, f = struct.unpack('<Bf', data[idx:idx+5])
            if ch:
                ch, k = ch // 10, ch % 10
                v = self._d_f.get(ch, [None, ]*8)
                v[k] = f
                self._d_f[ch] = v

    def __repr__(self):
        s = 'calibration = {\n'
        c = ['        %s: %s,\n' % (x, self._d_f[x]) for x in self._d_f]
        s += '    "calib": {\n%s    },\n' % ''.join(c)
        s += '}'
        return s

    def _poly(self, x, n):
        """Pass x trought calibration polynom with index n."""
        p = [v or 0. for v in self._d_f[n]]
        return p[0] + x*(p[1] + x*(p[2] + x*(p[3] + x*(p[4] + x*p[5]))))
        return x

    def evalMeas(self, measData):
        meas = {}
        r_lo = (measData.ch7+measData.ch8) / 2
        r_hi1 = measData.ch4 - r_lo
        r_hi2 = measData.ch5 - r_lo
        u1 = self._poly(r_hi2 / (measData.ch2 - r_lo), 4)
        u2 = self._poly(r_hi2 / (measData.ch3 - r_lo), 5)

        meas['U'] = max(u1, u2)
        meas['P'] = float('NAN')
        meas['T'] = float('NAN')

        return meas


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
      print("%s <INPUT FILE>")
      sys.exit(1)
    data = open(sys.argv[1], 'rb').read()
    c = Calibration(data)
    print(c)

