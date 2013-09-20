#!/usr/bin/env python2
# -*- coding: utf8 -*-
#
# Copyright 2013 Jiří Pinkava <j-pi@seznam.cz>
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
from rstt_swig import error_correction

class qa_error_correction (gr_unittest.TestCase):
    _packet00 = """
2a 2a 2a 2a 2a 10 65 10 4b 05 20 20 48 34 31 33
33 32 38 34 00 6d 00 0b ba 53 b5 1e 75 73 5d c3
1f 38 b8 05 43 20 83 54 71 8b 69 0c eb 27 0f b6
82 0f 2d df 0f 0a 27 11 d8 4a 11 a8 54 0f 7e 54
0d f4 55 0d 07 47 67 3d ac 46 80 14 77 ab 37 10
ab 45 80 82 9f 01 5f 3f 4f 1f 1f 6f f0 4f 7f 6f
3f f0 85 32 a1 00 6b 1b a2 01 ff a5 89 00 d1 08
8f 07 ff ff ff 7f 27 e9 a6 05 09 22 09 00 d7 e1
8a fe 0a a6 3d 00 40 6f a7 fc 26 e4 5c 00 1e 70
95 fc ff ff ff 7f 01 ce b1 00 87 10 e1 00 9a 5c
99 fe da f3 91 00 69 08 92 00 67 ac 4a 00 a0 c6
96 00 ff ff ff 7f de 50 95 00 ff ff ff 7f 9c 92
f3 01 0e 02 68 05 03 03 00 00 00 00 00 00 00 00
b2 7d ff 02 02 00 02 00 2e c0 0a 8b 89 3e d3 69
e6 75 86 1d d8 76 ca bb 37 94 e0 69 7b 91 34 1a""".replace('\n', '').replace(' ', '')

    def do(self, data_src, data_exp, test_block):
        src = blocks.vector_source_s(data_src, vlen=240)
        self.tb.connect(src, test_block)
        dst = blocks.vector_sink_s(vlen=240)
        self.tb.connect(test_block, dst)
        self.tb.run()
        result_data = tuple([int(x) for x in dst.data()])
        self.assertEqual(data_exp, result_data)

    def setUp(self):
        self.tb = gr.top_block ()

    def tearDown(self):
        self.tb = None

    def test_001(self):
        data_src = tuple([ord(x) for x in self._packet00.decode('hex')])
        data_exp = data_src
        data_src = data_src[:12] + (0, ) + data_src[13:]
        test_block = error_correction()
        self.do(data_src, data_exp, test_block)
        self.tb.run ()

    def test_002(self):
        data_src = tuple([ord(x) for x in self._packet00.decode('hex')])
        data_exp = data_src
        data_src = data_src[:230] + (0, ) + data_src[231:]
        test_block = error_correction()
        self.do(data_src, data_exp, test_block)
        self.tb.run ()

    def test_004(self):
        """13 data bytes broken, uncorrectable."""
        data_src = tuple([ord(x) for x in self._packet00.decode('hex')])
        data_src = data_src[:72] + (0, )*13 + data_src[85:]
        data_exp = data_src
        test_block = error_correction()
        self.do(data_src, data_exp, test_block)
        self.tb.run ()

    def test_005(self):
        """13 data bytes broken (1 erasure), correctable."""
        data_src = tuple([ord(x) for x in self._packet00.decode('hex')])
        data_src = data_src[:72] + (0, )*12 + (0x400, ) + data_src[85:]
        data_exp = data_src
        test_block = error_correction()
        self.do(data_src, data_exp, test_block)
        self.tb.run ()


if __name__ == '__main__':
    gr_unittest.run(qa_error_correction, "qa_error_correction.xml")
