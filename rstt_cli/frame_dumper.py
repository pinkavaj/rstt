#!/usr/bin/python3

import source

from calibration import Calibration
from frame import Frame
from math import isfinite
from struct import unpack
from subframe import SF_TYPE_CONFIG, SF_TYPE_MEASUREMENTS, SF_TYPE_GPS, SF_TYPE_PADDING, SF_TYPE_WTF1
from sys import argv

class Client:
    """UDP client for reversing data from meteosonde."""

    def __init__(self, src_url, log_prefix=None):
        self._src = source.open(src_url)
        self._calib_log = None
        self._cfg_log = None
        self._gps_log = None
        self._meas_log = None
        self._test_log = None
        self._calib_bin = None
        if log_prefix is not None:
            self._calib_log = open(log_prefix + '.calib.txt', 'w')
            self._calib_bin = open(log_prefix + '.calib.bin', 'wb')
            self._cfg_log = open(log_prefix + '.cfg.csv', 'w')
            self._gps_log = open(log_prefix + '.gps.csv', 'w')
            self._meas_log = open(log_prefix + '.meas.csv', 'w')
# may contain anything
            self._test_log = open(log_prefix + '.test.13O', 'w')

            self._gps_log.write('T;GPS_BLOB_0;' + 'status;PRN;SNR;P range;doppler;?(x);' * 12 + '\n')

    def _bin(self, num):
      #if num is 0:
      #      return bin(num)
        return '0b' + bin(num)[2:].zfill(8)

    def _bin4(self, num):
        return '0b' + bin(num)[2:].zfill(4)

    def loop(self):
        self._test_write_header()
        calibration = Calibration()
        frame_prev = None
        while True:
            data = self._src.get_frame()
            if not data:
                return
            frame = Frame(data, frame_prev)
            if not frame:
                continue
            if not frame.is_broken():
                frame_prev = frame
            conf = frame.get(SF_TYPE_CONFIG)
            if conf is not None:
                frame_num = conf.frame_num
            else:
                frame_num = 'N/A'
            self._dump_frame(frame, frame_num)
            if conf is not None:
                if calibration.addFragment(conf.callibration_num, conf.callibration_data):
                    break
            print("frame: %s %s" % (frame_num, not frame.is_broken(), ))

        print("calibration complete at frame %s" % frame_num)
        calibration.parse()
        self._dump_calibration(calibration)

        while True:
            data = self._src.get_frame()
            if not data:
                break
            frame = Frame(data, frame_prev)
            if not frame:
                continue
            if not frame.is_broken():
                frame_prev = frame
            conf = frame.get(SF_TYPE_CONFIG)
            if conf is not None:
                frame_num = conf.frame_num
            else:
                frame_num = 'N/A'
            self._dump_frame(frame, frame_num)
            print("frame: %s %s" % (frame_num, not frame.is_broken(), ))

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

    def _dump_frame(self, frame, frame_num):
        if self._cfg_log:
            self._dump_cfg(frame, frame_num)
        if self._gps_log:
            self._dump_gps(frame, frame_num)
        if self._meas_log:
            self._dump_meas(frame, frame_num)
        self._dump_test(frame, frame_num)

    def _dump_cfg(self, frame, frame_num):
        cfg = frame.get(SF_TYPE_CONFIG)
        if cfg is None:
            self._cfg_log.write('\n')
            return
        s = "%s,%s,0x%02X,0x%02X,0x%02X,%s,%s,%s,%s,%s,%s,%s\n" % (
                cfg.frame_num,
                cfg.id,
                cfg.d12,
                cfg.d13,
                cfg.d14,
                cfg.battery_low,
                cfg.battery_killer_countdown,
                cfg.hum_channel,
                cfg.hum_heat,
                cfg.start_detected,
                cfg.callibration_num,
                cfg.callibration_data,
                )
        self._cfg_log.write(s)

    def _dump_gps(self, frame, frame_num):
        gps = frame.get(SF_TYPE_GPS)
        if gps is None:
            self._gps_log.write("\n")
            return
        s = ""
        s += "%11.3f;" % gps.time
        s += "%s;" % self._bin(unpack('<H', gps.d76)[0])
        for sat in gps.satelites:
            stat = 1 if sat.doppler_lock else 0
            stat |= 2 if sat.prange_lock else 0
            stat |= 4 if sat.prange_ok else 0
            stat |= 8 if sat.time_ok else 0
            s += "%s;%d;%d;" % (self._bin4(stat), sat.prn, sat.sig_strength, )
            s += "%.1f;%s;%s;" % (sat.prange, sat.doppler, sat.x, )

        self._gps_log.write(s.replace('.', ',') + "\n")

    def _dump_meas(self, frame, frame_num):
        meas = frame.get(SF_TYPE_MEASUREMENTS)
        if meas is None:
            self._meas_log.write("\n")
            return
        s = "%s;%d;%d;%d;%d;%d;%d;%d;%d\n" % (
                    frame_num,
                    meas.ch1,
                    meas.ch2,
                    meas.ch3,
                    meas.ch4,
                    meas.ch5,
                    meas.ch6,
                    meas.ch7,
                    meas.ch8)
        s = s.replace('.', ',')
        self._meas_log.write(s)

    def _dump_test(self, frame, frame_num):
        """Anny testing code belongs here. Code may write to file or just print."""
        # add anny test/debug print here
        if not self._test_log:
            return
        # add print to file here
        #if frame.gps is None:
        #    return
        s = ""
        #td, t = divmod(frame.gps.time, (3600 * 24))
        #th, t = divmod(t, 3600)
        #tm, ts = divmod(t, 60)

        ## "EPOCH/SAT"
        #sats = [s for s in frame.gps.satelites if s.stat_ok() and isfinite(s.prange)]
        #nsat = len(sats)
        #prns = "".join(["G%2i" % s.prn for s in sats]) + (12 - nsat) * "   "
        #s = " %02i  %2i %2i %2i %2i %11.7f  0   %3i%s" % (self._date + (th, tm, ts, nsat, prns))

        #s = s.replace('.', ',')
        self._test_log.write(s + "\r\n")

        #for sat in sats:
        #    s = "%14.3f" % (sat.prange, )
        #    self._test_log.write(s + "\r\n")

    def _test_write_header(self):
        if not self._test_log:
            return
        log = self._test_log
        self._date = (2013, 7, 23, )
        l = ("%9.2f           " % 2.10, "OBSERVATION DATA".ljust(20), "GPS".ljust(20), )
        log.write(''.join(l).ljust(60) + "RINEX VERSION / TYPE\r\n")
        l = ("RSTT test dump".ljust(20), "My".ljust(20), "now".ljust(20))
        log.write(''.join(l).ljust(60) + "PGM / RUN BY / DATE\r\n")
        log.write("Vaisala".ljust(60) + "MARKER NAME\r\n")
        l = ("My".ljust(20), "My".ljust(40))
        log.write(''.join(l).ljust(60) + "OBSERVER / AGENCY\r\n")
        l = ("1".ljust(20), "meteosonde RS98".ljust(20), "unknown".ljust(20), )
        log.write(''.join(l).ljust(60) + "REC # / TYPE / VERS\r\n")
        l = ("1".ljust(20), "unknown".ljust(20), )
        log.write(''.join(l).ljust(60) + "ANT # / TYPE\r\n")
        l = ("1".ljust(20), "unknown".ljust(20), )
        log.write(''.join(l).ljust(60) + "ANT # / TYPE\r\n")
        l = ("%14.4f" % 3977581.,"%14.4f" % 1021269.,"%14.4f" % 4864164.,)
        log.write(''.join(l).ljust(60) + "APPROX POSITION XYZ\r\n")
        l = ("%14.4f" % 0., "%14.4f" % 0., "%14.4f" % 0., )
        log.write(''.join(l).ljust(60) + "ANTENNA: DELTA H/E/N\r\n")
        l = ("%6i" % 1, "%6i" % 0, )
        log.write(''.join(l).ljust(60) + "WAVELENGTH FACT L1/2\r\n")
        #l = ("%6i" % 2, "    C1", "    S1",)
        l = ("%6i" % 1, "    C1",)
        log.write(''.join(l).ljust(60) + "# / TYPES OF OBSERV\r\n")
        l = ("%6i%6i%6i%6i%6i%13.7f" % (self._date + (12, 00, 0.,)), ) # FIXME
        log.write(''.join(l).ljust(60) + "TIME OF FIRST OBS\r\n")
        self._date = (self._date[0] % 100, ) + self._date[1:]

        log.write("".ljust(60) + "END OF HEADER\r\n")


if __name__ == '__main__':
    if len(argv) < 2:
        raise ValueError("Missing parameter: source URL")
    log_prefix = None if len(argv) < 3 else argv[2]
    client = Client(argv[1], log_prefix=log_prefix)
    client.loop()

