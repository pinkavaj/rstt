
class PrintRow:
    def __init__(self, fmt):
        self._fmt = fmt
        self._fmt_idx = 0

    def print(self, items):
        for i in items:
            self._print_item(i)

    def _print_item(self,  s):
        s = s + ' '
        if len(self._fmt) <= self._fmt_idx :
            self._fmt.append(0)
        l = len(s) - self._fmt[self._fmt_idx]
        if l > 0:
            self._fmt[self._fmt_idx] = len(s)
        else:
            s = ' ' *  l + s

        print(s,  end='')
        self._fmt_idx += 1


    def print_(self):
        if self._crc1_ok:
            self._print('%6d' % self._d_frame_num)
            self._print(self._d_id.decode('ascii'))
            self._print('0x%02x' % self._d_15)
            self._print('0x%02x' % self._d_16)
            self._print('0x%02x' % self._d_17)
            self._print('%2d' % self._d_callibration_num)

            self._print('0x%02x' % self._d_37)
            self._print('0x%02x' % self._d_38)
            self._print('%6d' % self._d_wire)
            self._print('%6d' % self._d_hum_up)
            self._print('%6d' % self._d_hum_down)
#            self._print('%6d' % self._d_int4)
#            self._print('%6d' % self._d_int5)
            self._print('%6d' % self._d_pressure)
#            self._print('%6d' % self._d_int7)
#            self._print('%6d' % self._d_int8)
        print()

