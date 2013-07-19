#/usr/bin/python3

import crcmod
import struct

class Frame:
    def __init__(self, frame_data):
        self._data = frame_data
        self._crc = crcmod.mkCrcFun(0x11021, rev=False)
        self._parse()

    def get_calibration(self):
        if not self._crc1_ok:
            return None
        return (self._d_callibration_num, self._d_callibration_data, )

    def get_frame_num(self):
        if self._crc1_ok:
            return self._d_frame_num

    def _parse(self):
        self._data,  self._status = self._data[::2],  self._data[1::2]
        self._reed_solomon()
        self._check_crc()

        if self._crc1_ok:
            self._d_hdr = self._data[:8]
            self._d_frame_num = struct.unpack('<H',  self._data[8:10])[0]
            self._d_id = struct.unpack('10s',  self._data[10:20])[0]
            self._d_15 = int(self._data[20]) # TODO
            self._d_16 = int(self._data[21]) # TODO
            self._d_17 = int(self._data[22]) # TODO
            self._d_callibration_num = int(self._data[23])
            self._d_callibration_data = self._data[24:24+16]

        if self._crc2_ok:
            self._d_37 = int(self._data[42])
            self._d_38 = int(self._data[43])
            self._d_temp = struct.unpack('I',  self._data[44:47] + b'\x00')[0]
            self._d_hum_up = struct.unpack('I',  self._data[47:50] + b'\x00')[0]
            self._d_hum_down = struct.unpack('I',  self._data[50:53] + b'\x00')[0]
            self._d_ch4 = struct.unpack('I',  self._data[53:56] + b'\x00')[0]
            self._d_ch5 = struct.unpack('I',  self._data[56:59] + b'\x00')[0]
            self._d_pressure = struct.unpack('I',  self._data[59:62] + b'\x00')[0] # pressupre
            self._d_ch7 = struct.unpack('I',  self._data[62:65] + b'\x00')[0]
            self._d_ch8 = struct.unpack('I',  self._data[65:68] + b'\x00')[0]

        if self._crc3_ok:
            self._d_74 = self._data[74:98] # TODO
            self._d_gps_pseudorange = struct.unpack("<12d", self._data[98:194])

        if self._crc4_ok:
            self._d_198 = self._data[198:208] # TODO

    def _reed_solomon(self):
        # TODO
        pass

    def _check_crc(self):
        crc = struct.unpack('<H',  self._data[40:42])[0]
        self._crc1_ok = (self._crc(self._data[8:40]) == crc)

        crc = struct.unpack('<H',  self._data[68:70])[0]
        self._crc2_ok = (self._crc(self._data[44:68]) == crc)

        crc = struct.unpack('<H',  self._data[194:196])[0]
        self._crc3_ok = (self._crc(self._data[72:194]) == crc)

        crc = struct.unpack('<H',  self._data[208:210])[0]
        self._crc4_ok = (self._crc(self._data[198:208]) == crc)

