#!/usr/bin/env python2
# -*- coding: utf8 -*-
#
# Copyright 2013 Jiří Pinkava <j-pi@seznam.cz>.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

from gnuradio import gr, gr_unittest, blocks
from rstt_swig import bits2bytes

class qa_bits2bytes(gr_unittest.TestCase):

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

    def test_00(self):
        data_src = \
                (0, 0, 0, 0, 1, 0, 0, 0, 0, 1, ) + \
                (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, ) + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 18
        data_exp = (0x08, 0xff, 0xd9 )
        test_block = bits2bytes(16)
        self.do(data_src, data_exp, test_block)

    def test_01(self):
        data_src = \
                (0, 1, 0, 1, 0, ) + \
                (0, 0, 0, 0, 1, 0, 0, 0, 0, 1, ) + \
                (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, ) + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 18
        data_exp = (0x08, 0xff, 0xd9 )
        test_block = bits2bytes(16)
        self.do(data_src, data_exp, test_block)

    def test_02(self):
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
        test_block = bits2bytes(16)
        self.do(data_src, data_exp, test_block)

    def test_03(self):
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
        test_block = bits2bytes(16)
        self.do(data_src, data_exp, test_block)

    def test_04(self):
        """Multibite shift 4b"""
        data_src = \
                (0, 0, 0, 0, 1, 0, 0, 1, 0, 1, ) + \
                (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 16 + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, 0, 1, 0, ) + \
                (0, 1, 1, 0, 1, 0, 1, 0, 1, 1, ) + \
                (0, 1, 0, 0, 1, 1, 0, 1, 1, 1, ) + \
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ) * 19
        data_exp = (0x48, 0xff,) + (0, )*16 + (0xd9, 0xAB, 0xd9, 0x00 )
        test_block = bits2bytes(16)
        self.do(data_src, data_exp, test_block)

if __name__ == '__main__':
    gr_unittest.run(qa_bits2bytes, "qa_bits2bytes.xml")

