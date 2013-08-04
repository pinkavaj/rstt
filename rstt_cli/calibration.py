import struct

class Calibration(object):
    """Acumulates calibration data fragments, and parse if all data are avaliable."""

    def __init__(self, data = b''):
        self._have_fragments = [False,  ] * 32
        self._fragments = {}
        if data:
            if len(data) != 512:
                raise ValueError('Unsupported lenght of data: %d != 512' % len(data))
        self.data = data

    def addFragment(self, fragment_idx, fragment_data):
        """Process one subframe, with calibration data."""
        self._fragments[fragment_idx] = fragment_data
        self._have_fragments[fragment_idx] = True
        if self.completed():
            for idx in range(0,  32):
                self.data  += self._fragments[idx]
            return True
        return False

    def completed(self):
        """Return True if all fragments are collected."""
        if self.data:
            return True
        if [x for x in self._have_fragments if x == False]:
            return False
        return True

    def parse(self):
        self._d_0_2 = self.data[0:2] # TODO
        self._d_freq = struct.unpack('<H', self.data[2:4])
        self._d_count_1 = struct.unpack('<H', self.data[4:6])
        self._d_6_8 =  struct.unpack('<H', self.data[6:8]) # TODO
        # TODO 8:22
        self._d_id = struct.unpack('10c', self.data[22:32])[0].decode('ascii')
        self._d_block_32_36 = struct.unpack('<16h', self.data[32:64]) # TODO
        self._d_f = {}
        for idx in range(64, 511-4, 5):
            ch, f = struct.unpack('<Bf', self.data[idx:idx+5])
            if ch:
                self._d_f[ch] = f


if __name__ == '__main__':
    data = open('calibration.bytes', 'rb').read()
    c = Calibration(data)
    c.parse()
    c.print_()
