
from struct import unpack


class SubframeConfig:
    def __init__(self, data):
        self.frame_num = unpack('<H', data[0:2])[0]
        self.id = unpack('10s',  data[2:12])[0]
        self.d15 = int(data[12]) # TODO
        self.hum_channel = (data[13] & 0x08) >> 3
        self.hum_heat = (data[13] & 0x04) >> 2
        self.d16 = int(data[13]) & 0xF3 # TODO
        self.d17 = int(data[14]) # TODO
        self.callibration_num = int(data[15])
        self.callibration_data = data[16:32]
