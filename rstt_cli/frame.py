#/usr/bin/python3

import crcmod
from struct import unpack

from subframe_config import SubframeConfig
from subframe_gps import SubframeGPS
from subframe_meas import SubframeMeas


class Frame:
    """Parse one frame from sonde."""
    def __init__(self, frame_data):
        self._crc_fun = crcmod.mkCrcFun(0x11021, rev=False)
        self._parse(frame_data)

    def get_calibration(self):
        if self.config is not None:
            return (self.config.callibration_num, self.config.callibration_data, )

    def get_frame_num(self):
        if self.config is not None:
            return self.config.frame_num

    def _parse(self, data):
        data,  self._status = data[::2],  data[1::2]
        self._data = data
        self._reed_solomon()
        subframe1, subframe2, subframe3, subframe4 = \
                data[8:42], data[44:70], data[72:196], data[198:210]

        self.config = None
        if self._check_crc(subframe1):
            self.config = SubframeConfig(subframe1)

        self.meas = None
        if self._check_crc(subframe2):
            self.meas = SubframeMeas(subframe2)
        else:
            print("xxx")

        self.gps = None
        if self._check_crc(subframe3):
            self.gps = SubframeGPS(subframe3)

        self.subframe4 = None
        if self._check_crc(subframe4):
            self.subframe4 = subframe4[:-2] # TODO

    def _reed_solomon(self):
        # TODO
        pass

    def _check_crc(self, data):
        crc = unpack('<H', data[-2:])[0]
        return self._crc_fun(data[:-2]) == crc

