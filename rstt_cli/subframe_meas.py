
from conv_tools import conv_int


class SubframeMeas:
    def __init__(self, data):
        self._d_temp = conv_int(data[0:3])
        self._d_hum_up = conv_int(data[3:6])
        self._d_hum_down = conv_int(data[6:9])
        self._d_ch4 = conv_int(data[9:12])
        self._d_ch5 = conv_int(data[12:15])
        self._d_pressure = conv_int(data[15:18])
        self._d_ch7 = conv_int(data[18:21])
        self._d_ch8 = conv_int(data[21:24])
