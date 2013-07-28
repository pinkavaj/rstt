#!/usr/bin/python3

import source

from frame import Frame
from calibration import Calibration
from sys import argv

class UdpClient:
    """UDP client for reversing data from meteosonde."""

    def __init__(self, src_url, log_prefix=None):
        self._src = source.open(src_url)
        self._calib_log = None
        self._meas_log = None
        if log_prefix is not None:
            self._meas_log = open(log_prefix + '.meas.csv', 'w')
            self._calib_log = open(log_prefix + '.calib.txt', 'w')
# may contain anything
            self._test_log = open(log_prefix + '.test.csv', 'w')

    def loop(self):
        calibration = Calibration()
        while True:
            data = self._src.get_frame()
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
            data = self._src.get_frame()
            frame = Frame(data)
            print("frame: %s" % repr(frame.get_frame_num()))
            self._dump_frame(frame)

    def _dump_calibration(self, calibration):
        pass

    def _dump_frame(self, frame):
        if self._meas_log:
            self._dump_frame_channels(frame)
        if self._test_log:
            self._dump_frame_test(frame)
        #self._dump_frame_gps(frame)

    def _dump_frame_channels(self, frame):
        if not frame._crc2_ok:
            s = "\n"
        else:
            s = "%s;%d;%d;%d;%d;%d;%d;%d;%d\n" % (
                    str(frame.get_frame_num()),
                    frame._d_temp,
                    frame._d_hum_up,
                    frame._d_hum_down,
                    frame._d_ch4,
                    frame._d_ch5,
                    frame._d_pressure,
                    frame._d_ch7,
                    frame._d_ch8)
            s = s.replace('.', ',')
        self._meas_log.write(s)

    def _dump_frame_gps(self, frame):
        if not frame._crc3_ok:
            self._gps_log.write("\n")
            return
        s = ""
        for i in range(0, 10):
            s += "%d;" % frame._d_78[i]
        for i in range(0, 12):
          gps = frame._d_gps[i]
          s += "%.6e;%.6e;%x;%o;%d;" % (gps.pseudorange, gps.doppler, gps.status, gps.status, gps.status)

        self._gps_log.write(s.replace('.', ',') + "\n")

    def _dump_frame_test(self, frame):
        s = ""
        if frame._crc1_ok:
            s = "%d;%s;%s;%s;" % (frame.get_frame_num(),
                bin(frame._d_15), bin(frame._d_16), bin(frame._d_17) )
        else:
            s = ";;;;"

        if frame._crc2_ok:
            s += "%d;%d;" % (
                    frame._d_hum_up,
                    frame._d_hum_down,
                    )
            s = s.replace('.', ',')
        else:
          s += ";;"
        self._test_log.write(s + "\n")


if __name__ == '__main__':
    if len(argv) < 2:
        raise ValueError("Missing parameter: source URL")
    log_prefix = None if len(argv) < 3 else argv[2]
    client = UdpClient(argv[1], log_prefix=log_prefix)
    client.loop()

