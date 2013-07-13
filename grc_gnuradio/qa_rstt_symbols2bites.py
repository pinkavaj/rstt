#!/usr/bin/env python

from gnuradio import gr, gr_unittest, blocks
from rstt_symbols2bites import symbols2bites

_1 = (0, 1, )
_0 = (1, 0, )
_e0 = (0, 0, )
_e1 = (1, 1, )

class test_rstt_symbols2bites(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block ()

    def tearDown(self):
        self.tb = None

    def do(self, data_src, data_exp, test_block):
        src = blocks.vector_source_b(data_src)
        self.tb.connect(src, test_block)
        dst = blocks.vector_sink_b()
        self.tb.connect(test_block, dst)
        self.tb.run()
        result_data = tuple([int(x) for x in dst.data()])
        self.assertEqual(data_exp, result_data)

    def test_rstt_symbosl2bites_00(self):
        data_src = _0 + _0 + _0*16 + _0
        data_exp = (0, 0, )
        test_block = symbols2bites(16)
        self.do(data_src, data_exp, test_block)

    def test_rstt_symbosl2bites_01(self):
        data_src = _0 + _1 + _0*16 + _0
        data_exp = (0, 1, )
        test_block = symbols2bites(16)
        self.do(data_src, data_exp, test_block)

    def test_rstt_symbosl2bites_02(self):
        """Single insertion error."""
        _10 = _1 + _0
        data_src = _10*16 + (0, ) + _10*16 + _0*4
        data_exp = (1, 0)*16 + (1, 0)*10
        test_block = symbols2bites(16)
        self.do(data_src, data_exp, test_block)

    def test_rstt_symbosl2bites_03(self):
        """Single insertion error."""
        _10 = _1 + _0
        data_src = (0, ) + _10*16 + (0, ) + _10*16 + _0*4
        data_exp = (1, 0)*16 + (255, ) + (1, 0)*9 + (1, )
        test_block = symbols2bites(16)
        self.do(data_src, data_exp, test_block)

    def test_rstt_symbosl2bites_04(self):
        """Single insertion error."""
        _10010001 = _1 + _0 + _0 + _1 + _0 + _0 + _0 + _1
        data_src = _10010001*2 + (0, )*5 + _10010001*2 + _0*16
        data_exp = \
                (1, 0, 0, 1, 0, 0, 0, 1) + \
                (1, 0, 0, 1, 0, 0, 0, 1) + \
                (255, 255, 255, ) + \
                (0, 0, 1, 0, 0, 0, 1) + \
                (1, 0, 0, 1, 0, 0, 0, 1)
        test_block = symbols2bites(16)
        self.do(data_src, data_exp, test_block)

    def test_rstt_symbosl2bites_05(self):
        """Single insertion error."""
        _10010001 = _1 + _0 + _0 + _1 + _0 + _0 + _0 + _1
        data_src = (0,) + _10010001*2 + (0, )*5 + _10010001*2 + _0*16
        data_exp = \
                (1, 0, 0, 1, 0, 0, 0, 1) + \
                (1, 0, 0, 1, 0, 0, 0, 1) + \
                (255, 255, 255, ) + \
                (1, 0, 0, 1, 0, 0, 0, 1) + \
                (1, 0, 0, 1, 0, 0, 0)
        test_block = symbols2bites(16)
        self.do(data_src, data_exp, test_block)

if __name__ == '__main__':
    gr_unittest.run(test_rstt_symbols2bites, "test_rstt_symbols2bites.xml")

