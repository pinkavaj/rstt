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

            self._gps_log.write('T;GPS_BLOB_0;' + 'status;PRN;SNR;P range;doppler;?(x);' * 12 + '\n')

    def _bin(self, num):
      #if num is 0:
      #      return bin(num)
        return '0b' + bin(num)[2:].zfill(8)

    def _bin4(self, num):
        return '0b' + bin(num)[2:].zfill(4)

    def loop(self):
        calibration = Calibration()
        while True:
            frame = Frame(self._src.get_frame())
            print("frame: %s" % repr(frame.get_frame_num()))
            self._dump_frame(frame)
            c = frame.get_calibration()
            if not c is None:
                if calibration.addFragment(c[0], c[1]):
                    break
        "Recieve until calibration data are completed"

        print("calibration complete")
        calibration.parse()
        self._dump_calibration(calibration)

        while True:
            data = self._src.get_frame()
            frame = Frame(data)
            print("frame: %s" % repr(frame.get_frame_num()))
            self._dump_frame(frame)

    def _dump_calibration(self, calibration):
        if self._calib_bin:
            self._calib_bin.write(calibration.data)
        if not self._calib_log:
            return
        #self._calib_log.write('0x08: %7d\t' % calibration._d_8)
        #self._calib_log.write('0x0A: %7d\n' % calibration._d_10)
        for i in range(0x20, 0x40, 2):
            self._calib_log.write('%7d\t' % unpack('h', calibration.data[i:i+2]))
        self._calib_log.write('\n')

    def _dump_frame(self, frame):
        if self._meas_log:
            self._dump_meas(frame)
        if self._test_log:
            self._dump_frame_test(frame)
        if self._gps_log:
          self._dump_gps(frame)

    def _dump_meas(self, frame):
        if frame.meas is None:
            s = "\n"
        else:
            meas = frame.meas
            s = "%s;%d;%d;%d;%d;%d;%d;%d;%d\n" % (
                    str(
                        frame.get_frame_num()),
                        meas._d_temp,
                        meas._d_hum_up,
                        meas._d_hum_down,
                        meas._d_ch4,
                        meas._d_ch5,
                        meas._d_pressure,
                        meas._d_ch7,
                        meas._d_ch8)
            s = s.replace('.', ',')
        self._meas_log.write(s)

    def _dump_gps(self, frame):
        if frame.gps is None:
            self._gps_log.write("\n")
            return
        s = ""

        gps = frame.gps
        s += "%11.3f;" % gps.time
        s += "%s;" % self._bin(unpack('<H', gps.d76)[0])
        for sat in gps.satelites:
            stat = 1 if sat.doppler_lock else 0
            stat |= 2 if sat.prange_lock else 0
            stat |= 4 if sat.prange_ok else 0
            stat |= 8 if sat.time_ok else 0
            s += "%s;%d;%d;" % (self._bin4(stat), sat.prn, sat.sig_strength, )
            s += "%.1f;%s;%s;" % (sat.prange, sat.doppler, sat.x)

        self._gps_log.write(s.replace('.', ',') + "\n")

    def _dump_frame_test(self, frame):
        s = ""
        if frame.config is None:
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

