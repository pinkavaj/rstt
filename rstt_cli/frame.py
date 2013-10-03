#!/usr/bin/python3

from subframe import Subframe, SubframeError


class Frame(dict):
    """Parse one frame from sonde."""

    def __init__(self, data, frame_prev = None):
        """Parse frame from data. Data sould be byte array where
        data an data_status values are interleaved eg.
        bytes(data0, status0, data1, status1, ...), nonzero status indicate invalid data.
        If frame_prev is set, its structure is used to current frame if
        some invalid/broken values are found."""
        dict.__init__(self)
        self._parse(data, frame_prev)

    def is_broken(self):
        return self._broken

    def _parse(self, data, frame_prev):
        data = data[2*6:2*-24]
        data, status = data[::2], data[1::2]
        idx = 0
        self._sf_len = ()
        self._broken = False
        while data:
            try:
                subframe = Subframe.parse(data, status)
                self[subframe.sf_type] = subframe
                sf_len = len(subframe)
            except SubframeError:
                if frame_prev is None:
                    return
                self._broken = True
                sf_len = frame_prev._sf_len[idx]
            data = data[sf_len:]
            status = status[sf_len:]
            self._sf_len = self._sf_len + (sf_len, )
            idx += 1

