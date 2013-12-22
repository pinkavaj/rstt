#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from rstt_swig import clip

class qa_clip (gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def do(self, data_src, data_exp, test_block, vlen):
        src = blocks.vector_source_f(data_src, False, vlen)
        self.tb.connect(src, test_block)
        dst = blocks.vector_sink_f(test_block.vlen_out())
        self.tb.connect(test_block, dst)
        self.tb.run()
        result_data = tuple([int(x) for x in dst.data()])
        self.assertEqual(data_exp, result_data)

    def test_00(self):
        data_src = (11., 12., 13., 14., 15., -14., -13., -12., -11., )
        data_exp = (12, 13, 14, 15, -14, -13, -12, )
        vlen = len(data_src)
        test_block = clip(vlen, 1., 0.8)
        self.do(data_src, data_exp, test_block, len(data_src))

    def test_01(self):
        data_src = (11., 12., 13., 14., 15., -15., -14., -13., -12., -11., )
        data_exp = (12, 13, 14, 15, -15, -14, -13, -12, )
        vlen = len(data_src)
        test_block = clip(vlen, 1., 0.82)
        self.do(data_src, data_exp, test_block, len(data_src))

    def test_02(self):
        data_src = (11., 12., 13., 14., 15., -14., -13., -12., -11.,
            21., 22., 23., 24., 25., -24., -23., -22., -21., )
        data_exp = (12, 13, 14, 15, -14, -13, -12,
            22, 23, 24, 25, -24, -23, -22, )
        vlen = len(data_src) / 2
        test_block = clip(vlen, 1., 0.8)
        self.do(data_src, data_exp, test_block, len(data_src) / 2)

    def test_03(self):
        data_src = (11., 12., 13., 14., 15., -15., -14., -13., -12., -11.,
            21., 22., 23., 24., 25., -25., -24., -23., -22., -21., )
        data_exp = (12, 13, 14, 15, -15, -14, -13, -12,
            22, 23, 24, 25, -25, -24, -23, -22, )
        vlen = len(data_src) / 2
        test_block = clip(vlen, 1., 0.82)
        self.do(data_src, data_exp, test_block, len(data_src) / 2)


if __name__ == '__main__':
    gr_unittest.run(qa_clip, "qa_clip.xml")

