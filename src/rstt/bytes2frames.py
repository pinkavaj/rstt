
from gnuradio import gr, blocks
import numpy

class bytes2frames(gr.basic_block):
    """Recieve stream of bytes with decoding status flags (stored upper half of short)
    and split it into frames 240B long.
    Returns vector(240) of shorts with data."""

    # "This is copy from bites2bytes.py, blah."
    STATUS_ERR_START = 0x100
    STATUS_ERR_BYTE = 0x200
    STATUS_ERR_STOP = 0x400
    STATUS_ERR_SYN = 0x800
    """Invalid synchronization byte."""

    _sync_bytes = (
            (0, 0x10),
            (1, 0x65),
            (2, 0x10),
            (37, 0x69),
            (38, 0x0C),
            (65, 0x3D),
            (66, 0x94),
            (191, 0x68),
            (192, 0x05),
            (205, 0xff),
            (206, 0x02),
            (235, 0x2A),
            (236, 0x2A),
            (237, 0x2A),
            (238, 0x2A),
            (239, 0x2A),
            )

    def __init__(self):
        gr.basic_block.__init__(
                self,
                name = "rstt_bytes2frames",
                in_sig = [numpy.int16],
                out_sig = [numpy.dtype((numpy.int16, 240, ))],
                )
        self._in_idx = 0
        self._in_idx2 = 0
        self._resync_threshold = 5
        """Minimal number of correct sync bytes for packet start resynchronization."""
        self._offs = 0
        """Synchronization offset for incomplete sync. search round."""
        self._nsync = 0
        """Synchronization level for incomplete sync. search round."""

    def forecast(self, noutput_items, ninput_items_required):
        nout = 240 - self._in_idx2 if self._in_idx2 else 0
        ninput_items_required[0] = noutput_items * 240 + nout

    def general_work(self, input_items, output_items):
        self._in = input_items[0]
        self._in_idx = 0
        self._in_len = len(self._in) - 239
        """Simplifies _in_idx2 < _in_len, We process 10 bites at a time
        and for each do [idx + 10]."""
        self._out = output_items[0]
        self._out_idx = 0
        self._out_len = len(self._out)

        self._work()
        self.consume(0, self._in_idx)
        self._in_idx2 -= self._in_idx
        return self._out_idx

    def _check_byte(self, value, expected):
        """Check byte for value, return 1 if equals 0 otherwise."""
        if not value & self.STATUS_ERR_BYTE:
            if value & 0xff == expected:
                return 1
        return 0

    def _is_frame(self, idx):
        """Return number of bytes correlating with frame synchronization bytes."""
        sync_count = 0
        for sync_byte in self._sync_bytes:
            value = self._in[idx + sync_byte[0]]
            sync_count += self._check_byte(value, sync_byte[1])
        return sync_count

    def _send_packet(self, length=240):
        """Send packed, if length != 240 suppose start of packet is lost."""
        if length < 240:
            missing = 240 - length
            self._out[self._out_idx][:missing] = \
                    [self.STATUS_ERR_START | self.STATUS_ERR_BYTE | self.STATUS_ERR_STOP, ] * missing
        self._out[self._out_idx][-length:] = self._in[self._in_idx:self._in_idx+length]

        for sync_byte in self._sync_bytes:
            value = self._out[self._out_idx][sync_byte[0]]
            if not self._check_byte(value, sync_byte[1]):
                self._out[self._out_idx][sync_byte[0]] |= self.STATUS_ERR_SYN
        self._in_idx += length
        self._out_idx += 1
        self._in_idx2 = self._in_idx

    def _work(self):
        while self._in_idx2 < self._in_len and self._out_idx < self._out_len:
            for idx in range(0, 238 - (self._in_idx2 - self._in_idx)):
                if self._in_idx2 + idx >= self._in_len:
                    self._in_idx2 += idx
                    return
                sync = self._is_frame(self._in_idx2 + idx)
                if sync > self._nsync:
                    self._nsync = sync
                    self._offs = idx
                if sync == len(self._sync_bytes):
                    break
            if self._nsync >= self._resync_threshold:
                if self._offs > 0:
                    self._send_packet(self._offs)
            self._offs = 0
            self._nsync = 0
            if self._out_idx >= self._out_len:
                return
            self._send_packet()

