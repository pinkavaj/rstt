
from gnuradio import gr, blocks
import numpy

class symbols2bites(gr.basic_block):
    """Vaisala radio sonde reception chain.
    Convert demodulated data (symbol stream) into bite stream

    At input expects one symbol at a time, converts in into bites
    (2 symbols => 1 bite) and returns one bite at a time.
    Result is stream of bites where 1 => 1; 0 => 0; -1 => error in reception.
    """
    _symbols2bite = {
            0: -1,
            1: 1,
            -1: 0,
            }
    """Converts computed bite into real value."""

    def __init__(self, sync_nbites):
        gr.basic_block.__init__(
                self,
                name = "Symbols to bites convertor",
                in_sig = [numpy.int8],
                out_sig = [numpy.int8],
                )
        self._err = numpy.zeros(2, dtype=numpy.int)
        """Number of bit errors for even/odd synchronization."""
        self._roll_out_remain = 0
        """Bites to put in output before anny other work."""
        self._win_len_b = sync_nbites
        self._win_len = 2 * sync_nbites
        self._win = numpy.ones(self._win_len, dtype=numpy.int8)
        """Precomputed bite values/errors (-1 => 0, 1 => 1, 0 = error) for sync."""
        self._win_idx = 0
        self._win_missing = self._win_len
        self._work = self._work_fill

    def forecast(self, noutput_items, ninput_items_required):
        ninput_items_required[0] = 2 * noutput_items + self._win_missing + 1

    def general_work(self, input_items, output_items):
        self._in = input_items[0]
        self._in_len = len(self._in) - 2
        self._in_idx = 0
        """reserve, _in_len must be odd, and we need to do _in[idx + 1] ..."""
        self._out = output_items[0]
        self._out_idx = 0
        self._out_len = len(self._out)
        self._work()
        self.consume(0, self._in_idx)
        return self._out_idx

    def _is_out_of_sync(self):
        """Return True if _sync_offs need to bee switched."""
        return (self._err[0] > self._err[1] and self._sync_offs == 0) or \
                (self._err[0] < self._err[1] and self._sync_offs == 1)

    def _put_symbol(self):
        """Put one symbol into synchronization window, returns current bite."""
        new = self._in[self._in_idx + 1] - self._in[self._in_idx]
        old, self._win[self._win_idx] = self._win[self._win_idx], new
        self._err[self._win_idx % 2] += abs(old) - abs(new)
        """num of errors += 1 - abs(new) - (1 - abs(old))"""
        self._in_idx += 1
        self._win_idx = (self._win_idx + 1) % self._win_len
        return old

    def _roll_out(self, nbites=0):
        """Roll nbites from window into output (input is not read)."""
        self._roll_out_remain += nbites
        roll = min(self._roll_out_remain, \
                self._out_len - self._out_idx, \
                (self._in_len - self._in_idx) / 2)
        for n in range(0, roll):
            self._shift_bite()
        self._roll_out_remain -= roll
        if self._roll_out_remain != 0:
            return False
        if self._is_out_of_sync():
            self._sync_offs = 1 - self._sync_offs
        return True

    def _shift_bite(self):
        """Read 2 symbols from input, put one bite to output."""
        out0 = self._put_symbol()
        out1 = self._put_symbol()
        out = out0 if self._sync_offs == 0 else out1
        self._out[self._out_idx] = self._symbols2bite[out]
        self._out_idx += 1

    def _work_fill(self):
        """Initial buffer filling."""
        in_len = len(self._in) - 1
        while self._win_missing > 0 and self._in_idx < in_len:
            self._put_symbol()
            self._win_missing -= 1

        if self._win_missing != 0:
            return
        self._sync_offs = 0 if self._err[0] <= self._err[1] else 1
        self._work = self._work_convert
        self._work()

    def _work_convert(self):
        if not self._roll_out():
            return

        while self._in_idx < self._in_len and self._out_idx < self._out_len:
            if self._is_out_of_sync():
                if not self._roll_out(self._win_len_b - max(self._err)):
                    return
                continue
            self._shift_bite()
