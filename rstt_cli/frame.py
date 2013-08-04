#/usr/bin/python3

import crcmod
import struct

class GPSInfo:
  """GPS informations recieved for one channel."""
  def __init__(self, id, pseudorange, doppler, x):
    self.doppler = doppler
    self.id = id
    self.pseudorange = pseudorange
    self.x = x

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

    def _int24(self, data):
        """Convert 3 bytes into int."""
        return struct.unpack('<i', data + b'\x00')[0]

    def _parse(self):
        self._data,  self._status = self._data[::2],  self._data[1::2]
        self._reed_solomon()
        self._check_crc()

        if self._crc1_ok:
            self._d_hdr = self._data[:8]
            self._d_frame_num = struct.unpack('<H', self._data[8:10])[0]
            self._d_id = struct.unpack('10s',  self._data[10:20])[0]
            self._d_15 = int(self._data[20]) # TODO
            self._d_hum_ch = (self._data[21] & 0x08) >> 3
            self._d_hum_heat = (self._data[21] & 0x04) >> 2
            self._d_16 = int(self._data[21]) & 0xF3 # TODO
            self._d_17 = int(self._data[22]) # TODO
            self._d_callibration_num = int(self._data[23])
            self._d_callibration_data = self._data[24:24+16]

        if self._crc2_ok:
            self._d_37 = int(self._data[42])
            self._d_38 = int(self._data[43])
            self._d_temp = self._int24(self._data[44:47])
            self._d_hum_up = self._int24(self._data[47:50])
            self._d_hum_down = self._int24(self._data[50:53])
            self._d_ch4 = self._int24(self._data[53:56])
            self._d_ch5 = self._int24(self._data[56:59])
            self._d_pressure = self._int24(self._data[59:62])
            self._d_ch7 = self._int24(self._data[62:65])
            self._d_ch8 = self._int24(self._data[65:68])

        if self._crc3_ok:
            self._d_gps_t = struct.unpack("<I", self._data[72:76])[0]
            self._d_76 = self._data[76:78] # TODO
            sat_num = self._data[78:86]
            gps_sat_num = []
            while sat_num:
                lo, hi, sat_num = sat_num[0], sat_num[1], sat_num[2:]
                a = (lo & 0x1F) + 1
                b = ((lo >> 5) | ((hi & 0x3) << 3)) + 1
                c = (hi >> 2) + 1
                gps_sat_num.extend((a, b, c, ))
            self._d_gps_status = struct.unpack("12B", self._data[86:98])

            gps_pos = self._data[98:194]
            self._d_gps = []
            for i in range(0, 12):
                d = gps_pos[i*8:(i+1)*8]
                self._d_gps.append(
                        GPSInfo(gps_sat_num[i],
                            struct.unpack('<i', d[:4])[0],
                            self._int24(d[4:7]),
                            struct.unpack('b', d[7:8])[0]))

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

