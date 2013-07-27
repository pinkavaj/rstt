#!/bin/sh/python3

import socket
from frame import Frame
from calibration import Calibration
from sys import argv

class UdpClient:
    """UDP client for reversing data from meteosonde."""

    def __init__(self, addr='127.0.0.1', port=5003, data_log=None, calib_log=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((addr, port))
        self._calib_log = None
        self._data_log = None
        if data_log:
            self._data_log = open(data_log, 'w')
        if calib_log:
            self._calib_log = open(calib_log, 'w')

    def loop(self):
        calibration = Calibration()
        while True:
            data, server = self.sock.recvfrom(1024)
            frame = Frame(data)
            print("frame: %s" % repr(frame.get_frame_num()))
            self._dump_frame(frame)
            c = frame.get_calibration()
            if not c is None:
                if calibration.addFragment(c[0], c[1]):
                    break
        "Recieve until calibration data are completed"

        print("calibration complete")
        self._dump_calibration(calibration)

        while True:
            data,  server = self.sock.recvfrom(1024)
            frame = Frame(data)
            print("frame: %s" % repr(frame.get_frame_num()))
            self._dump_frame(frame)

    def _dump_calibration(self, calibration):
        pass

    def _dump_frame(self, frame):
        if not self._data_log:
            return
        self._dump_frame_gps(frame)
        #self._dump_frame_channels(frame)

    def _dump_frame_channels(self, frame):
        if not frame._crc1_ok:
            s = "\n"
        else:
            s = "%d;%d;%d;%d;%d;%d;%d;%d\n" % (
                    frame._d_temp,
                    frame._d_hum_up,
                    frame._d_hum_down,
                    frame._d_ch4,
                    frame._d_ch5,
                    frame._d_pressure,
                    frame._d_ch7,
                    frame._d_ch8)
            s = s.replace('.', ',')
        self._data_log.write(s)

    def _dump_frame_gps(self, frame):
        if not frame._crc3_ok:
            self._data_log.write("\n")
            return
        s = ""
        for i in range(0, 10):
            s += "%d;" % frame._d_78[i]
        for i in range(0, 12):
          gps = frame._d_gps[i]
          s += "%.6e;%.6e;%x;%o;%d;" % (gps.pseudorange, gps.doppler, gps.status, gps.status, gps.status)

        self._data_log.write(s.replace('.', ',') + "\n")


if __name__ == '__main__':
    data_log = None if len(argv) < 2 else argv[1]
    calib_log = None if len(argv) < 3 else argv[2]
    client = UdpClient(data_log=data_log, calib_log=calib_log)
    client.loop()

