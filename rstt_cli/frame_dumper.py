#!/usr/bin/python3

import source

from calibration import Calibration
from frame import Frame
from struct import unpack
from sys import argv

class UdpClient:
    """UDP client for reversing data from meteosonde."""

    def __init__(self, src_url, log_prefix=None):
        self._src = source.open(src_url)
        self._calib_log = None
        self._meas_log = None
        if log_prefix is not None:
            self._gps_log = open(log_prefix + '.gps.csv', 'w')
            self._meas_log = open(log_prefix + '.meas.csv', 'w')
            self._calib_log = open(log_prefix + '.calib.txt', 'w')
            self._calib_bin = open(log_prefix + '.calib.bin', 'wb')
# may contain anything
            self._test_log = open(log_prefix + '.test.csv', 'w')

            self._gps_log.write('T;GPS_BLOB_0;' + 'ID;P range;doppler;?(x);?(status);?(status);' * 12 + '\n')

    def _bin(self, num):
      #if num is 0:
      #      return bin(num)
        return '0b' + bin(num)[2:].zfill(8)

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
        if self._calib_bin:
            self._calib_bin.write(calibration.data)
        pass

    def _dump_frame(self, frame):
        if self._meas_log:
            self._dump_frame_channels(frame)
        if self._test_log:
            self._dump_frame_test(frame)
        if self._gps_log:
          self._dump_frame_gps(frame)

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

        s += "%11.3f;" % (frame._d_gps_t / 1000.)
        s += "%s;" % self._bin(unpack('<H', frame._d_76)[0])
        for i in range(0, 12):
          gps = frame._d_gps[i]
          s += "%d;%d;%d;%d;" % \
                  (gps.id, gps.pseudorange, gps.doppler, gps.x)
          s += "%d;%s;" % (frame._d_gps_status[i], self._bin(frame._d_gps_status[i]), )

        self._gps_log.write(s.replace('.', ',') + "\n")

    def _dump_frame_test(self, frame):
        s = ""
        if not frame._crc1_ok:
            return
        s = "%6d;" % (frame.get_frame_num(), )

        s = s.replace('.', ',')
        self._test_log.write(s + "\n")


if __name__ == '__main__':
    if len(argv) < 2:
        raise ValueError("Missing parameter: source URL")
    log_prefix = None if len(argv) < 3 else argv[2]
    client = UdpClient(argv[1], log_prefix=log_prefix)
    client.loop()

