#!/usr/bin/env python

from gnuradio import gr, gr_unittest, blocks
from bites2bytes import bites2bytes

class test_rstt_bites2bytes(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block ()

    def tearDown(self):
        self.tb = None

    def do(self, data_src, data_exp, test_block):
        src = blocks.vector_source_b(data_src)
        self.tb.connect(src, test_block)
        dst = blocks.vector_sink_s()
        self.tb.connect(test_block, dst)
        self.tb.run()
        result_data = tuple([int(x) for x in dst.data()])
        self.assertEqual(data_exp, result_data)

    def test_rstt_symbosl2bites_00(self):
        data_src = \
                (0, 0, 0, 0, 1, 0, 0, 0, 0, 1, ) + \
                (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, ) + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 18
        data_exp = (0x08, 0xff, 0xd9 )
        test_block = bites2bytes(16)
        self.do(data_src, data_exp, test_block)

    def test_rstt_symbosl2bites_01(self):
        data_src = \
                (0, 1, 0, 1, 0, ) + \
                (0, 0, 0, 0, 1, 0, 0, 0, 0, 1, ) + \
                (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, ) + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 18
        data_exp = (0x08, 0xff, 0xd9 )
        test_block = bites2bytes(16)
        self.do(data_src, data_exp, test_block)

    def test_rstt_symbosl2bites_02(self):
        """Test single bit insertion."""
        data_src = \
                (0, 0, 0, 0, 1, 0, 0, 1, 0, 1, ) + \
                (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 16 + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, ) + \
                (0, 0, 1, 0, 1, 1, 1, 0, 0, 1, ) + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 18
        data_exp = (0x48, 0xff,) + (0, )*16 + (0xd9, 0x3a, 0xd9, )
        test_block = bites2bytes(16)
        self.do(data_src, data_exp, test_block)

    def test_rstt_symbosl2bites_03(self):
        """Test single bit deletion."""
        data_src = \
                (0, 0, 0, 0, 1, 0, 0, 1, 0, 1, ) + \
                (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 16 + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (1, 1, 0, 1, 0, 1, 0, 1, 1, ) + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 18
        data_exp = (0x48, 0xff,) + (0, )*16 + (0xd9, 0x1ab, 0xd9, )
        test_block = bites2bytes(16)
        self.do(data_src, data_exp, test_block)

if __name__ == '__main__':
    gr_unittest.run(test_rstt_bites2bytes, "test_rstt_bites2bytes.xml")

