
from gnuradio import gr, blocks
import numpy

class bites2bytes(gr.basic_block):
    """Recieves bites, one (bite at a time), sends bytes (one byte at a time).
    Returns byte (0-255) if returned value is out of this range it indicates
    (possible) error. Possible error states (can be ORed)
    0x100 - invalid start bite 
    0x200 - invalid data bite(s)
    0x400 - invalid stop bite
    """

    STATUS_INVALID_START = 0x100
    STATUS_INVALID_BYTE = 0x200
    STATUS_INVALID_STOP = 0x400

    _SYNC_OFFS_INVALID = 42

    def __init__(self, sync_nbytes):
        gr.basic_block.__init__(
                self,
                name = "bites2bytes",
                in_sig = [numpy.int8],
                out_sig = [numpy.int16],
                )
        self._in_idx = 0
        self._in_idx2 = 0
        self._sync = numpy.zeros(10, dtype=numpy.int32)
        """Value proporional to number of found synchronization sequences."""
        self._sync_idx = 0
        self._sync_offs = self._SYNC_OFFS_INVALID
        self._sync_len = sync_nbytes * 10
        self._send_bytes_remain = 0
        self._fill_bites_remain = self._sync_len
        self._work = self._work_fill
        self._shit = 0
        """Increases whenewer output length is zero,
        resets back to 0 when output length is nonzero.
        This increases number of bites requested from input mainly to broke
        otherwise inifinite loop in tests."""

    def forecast(self, noutput_items, ninput_items_required):
        ninput_items_required[0] = noutput_items * 10 + \
                self._sync_len + 20 + self._shit

    def general_work(self, input_items, output_items):
        self._in = input_items[0]
        self._in_idx = 0
        self._in_len = len(self._in) - 20
        """Simplifies _in_idx2 < _in_len, We process 10 bites at a time
        and for each do [idx + 10]."""
        self._out = output_items[0]
        self._out_idx = 0
        self._out_len = len(self._out)

        self._work()
        self.consume(0, self._in_idx)
        self._in_idx2 -= self._in_idx
        self._shit = 0 if self._out_idx else self._shit + 1
        return self._out_idx

    def _shift_bites(self, nbites=10):
        """Roll bites, replace processed bites at _in_idx by new at _in_idx2."""
        for n in range(0, nbites):
            b0 = self._in[self._in_idx + n]
            b9 = self._in[self._in_idx + n + 9]
            if b0 == 0 and b9 == 1:
                self._sync[self._sync_idx + n] -= 1

            b0 = self._in[self._in_idx2 + n]
            b9 = self._in[self._in_idx2 + n + 9]
            if b0 == 0 and b9 == 1:
                self._sync[self._sync_idx + n] += 1

        self._in_idx += nbites
        self._in_idx2 += nbites
        self._sync_idx = (self._sync_idx + nbites) % 10 - 10

    def _shift_bites_in(self, nbites=10):
        """Shift nbites into process, used only for initilization."""
        for n in range(0, nbites):
            b0 = self._in[self._in_idx2 + n]
            b9 = self._in[self._in_idx2 + n + 9]
            if b0 == 0 and b9 == 1:
                self._sync[self._sync_idx + n] += 1
        self._in_idx2 += nbites
        self._sync_idx = (self._sync_idx + nbites) % 10 - 10

    def _get_byte_sync_status(self, has_start=True):
        """Return status of synchronization bites in current buffer position.
        Set has_start=False if start bit missing,"""
        status = self.STATUS_INVALID_START
        if has_start:
            if self._in[self._in_idx] == 0:
                status = 0
            self._shift_bites(1)
        if self._in[self._in_idx + 8] != 1:
            status |= self.STATUS_INVALID_STOP
        return status

    def _get_sync_offs(self):
        """Evaluate sync offset from _sync statistics."""
        idx = 0
        sync = 0
# sync with offset -1, 0, or 1 from current sync is preffered
        start = (self._sync_idx - 1) % 10 - 10
        for i in range(start, start + 10):
            if self._sync[i] > sync or \
                    (self._sync[i] == sync and (i % 10) == (self._sync_idx % 10)):
                idx = i
                sync = self._sync[i]
        return idx % 10 - 10

    def _resync(self, sync_offs):
        """Shift data out to get sync again, or send byte of shift is -1."""
        shift = (sync_offs - self._sync_offs) % 10
        self._sync_offs = sync_offs
        if shift == 9:
            self._send_byte(True)
            return
        self._shift_bites(shift)

    def _send_bytes(self, nbytes=0):
        """Send N bytes to output, return True if succes, False if not."""
        self._send_bytes_remain += nbytes
        if not self._send_bytes_remain:
            return True
        for n in range(0, self._send_bytes_remain):
# _resync migh requre few more bites
            if self._out_idx >= (self._out_len - 1) or self._in_idx2 >= (self._in_len - 9):
                self._send_bytes_remain -= n
                return False
            self._send_byte()
        self._send_bytes_remain = 0
        self._resync(self._get_sync_offs())
        return True

    def _send_byte(self, start_missing=False):
        """Convert 10bit (9 ifstart_missing == True) from input to 1B at output.
        Drops processed bites from input."""
        idx = self._in_idx
        status = self.STATUS_INVALID_START
        if not start_missing:
            if self._in[idx] == 0:
                status = 0
            idx += 1

        if self._in[idx + 8] != 1:
            status |= self.STATUS_INVALID_STOP

        B = 0
        for i in range(idx, idx + 8):
            b = self._in[i]
            B = B << 1
            if b == -1:
                status |= self.STATUS_INVALID_BYTE
                continue
            B |= b

        self._out[self._out_idx] = B | status
        self._out_idx += 1
        self._shift_bites(10 if not start_missing else 9)
        #return self._out_idx < self._out_len

    def _work_fill(self):
        """Initial buffer filling."""
        if self._fill_bites_remain > 0:
            for n in range(0, self._fill_bites_remain / 10):
                if self._in_idx2 >= self._in_len:
                    return
                self._shift_bites_in()
            if self._in_idx2 >= self._in_len:
                return
            fract = self._fill_bites_remain % 10
            self._shift_bites_in(fract)
            self._fill_bites_remain = 0

        if self._in_idx2 > self._in_len:
            return

        self._sync_offs = self._get_sync_offs()
        self._shift_bites(self._sync_offs % 10)
        self._work = self._work_process
        self._work()

    def _work_process(self):
        """Process recieved bites."""
        if not self._send_bytes():
            return
        while self._in_idx2 < self._in_len and self._out_idx < self._out_len:
            sync_offs = self._get_sync_offs()
            if sync_offs != self._sync_offs:
                if not self._send_bytes(self._sync_len / 10 / 2 - 1):
                    return
            self._send_byte()

