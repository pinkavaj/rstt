from subframe import Subframe, SubframeErrorCorruptedData
from subframe import SF_TYPE_CONFIG, SF_TYPE_GPS, SF_TYPE_MEASUREMENTS, \
    SF_TYPE_PADDING, SF_TYPE_WTF1
import unittest


class TestSubframe(unittest.TestCase):
    def test_ok_t0x01_00(self):
        data = b'\x01\x04\x01\x02\x03\x04\x05\x06\x07\x08\x92\x47'
        subframe = Subframe.parse(data, (0, ) * len(data))
        self.assertEqual(subframe.sf_type, 0x01)
        self.assertEqual(subframe.sf_bytes, data[2:-2])

    def test_broken_t0x01_00(self):
        data = b'\x01\x04\x01\x02\x03\x04\x05\x06\x07\x08\x92\x47'
        self.assertRaises(SubframeErrorCorruptedData,
            Subframe.parse, data, (0, ) * 6 + (1, ) + (0, ) * 5 )

    def test_ok_t0x65_00(self):
        data = b'e\x10\xf1   J1553020\x00q\x00\x11P\xbez|\x9a\x13<{&\x87t\xb8|!\x96\x8b\xf5\xfa'
        subframe = Subframe.parse(data, (0, ) * len(data))
        self.assertEqual(subframe.sf_type, SF_TYPE_CONFIG)
        self.assertEqual(subframe.sf_bytes, data[2:-2])

    def test_ok_t0x67_00(self):
        data = b'g=\xc1\xbd\xf0\xff\x99\xaa\n\x00\x00\x00\x00\x00\x00\x00\xf0\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xdcx\xf2\x00\xf4cJ\x00w\xd1\x17\x01)\xb8\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\x19\xf7\x16\x00\xe9p\x94\x00\xaek'
        subframe = Subframe.parse(data, (0, ) * len(data))
        self.assertEqual(subframe.sf_type, SF_TYPE_GPS)
        self.assertEqual(subframe.sf_bytes, data[2:-2])

    def test_ok_t0x68_00(self):
        data = b'h\x05\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\xb2}'
        subframe = Subframe.parse(data, (0, ) * len(data))
        self.assertEqual(subframe.sf_type, SF_TYPE_WTF1)
        self.assertEqual(subframe.sf_bytes, data[2:-2])

    def test_ok_t0x69_00(self):
        data = b'i\x0c\xa2e\r#\xb8\x0f\xde\xb6\x0f\xb32\x11\xf04\x11w\xcc\x0e#c\r\xb5d\r3g'
        subframe = Subframe.parse(data, (0, ) * len(data))
        self.assertEqual(subframe.sf_type, SF_TYPE_MEASUREMENTS)
        self.assertEqual(subframe.sf_bytes, data[2:-2])
        self.assertEqual(subframe.ch1, 0x0d65a2)
        self.assertEqual(subframe.ch2, 0x0fb823)
        self.assertEqual(subframe.ch3, 0x0fb6de)
        self.assertEqual(subframe.ch4, 0x1132b3)
        self.assertEqual(subframe.ch5, 0x1134f0)
        self.assertEqual(subframe.ch6, 0x0ecc77)
        self.assertEqual(subframe.ch7, 0x0d6323)
        self.assertEqual(subframe.ch8, 0x0d64b5)

    def test_ok_t0xff_00(self):
        data = b'\xff\x02\x02\x00\x02\x00'
        subframe = Subframe.parse(data, (0, ) * len(data))
        self.assertEqual(subframe.sf_type, SF_TYPE_PADDING)
        self.assertEqual(subframe.sf_bytes, data[2:])


if __name__ == '__main__':
      unittest.main()

