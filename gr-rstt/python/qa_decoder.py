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
from rstt_swig import decoder

class qa_decoder (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def do(self, data_src, data_exp, test_block):
        src = blocks.vector_source_b(data_src)
        self.tb.connect(src, test_block)
        dst = blocks.vector_sink_s(vlen=240)
        self.tb.connect(test_block, dst)
        self.tb.run()
        result_data = tuple([int(x) for x in dst.data()])
        self.assertEqual(data_exp, result_data)

    def test_01(self):
        """Dummy test, just proves module can be loaded/called."""
        data_src = ()
        data_exp = ()
        test_block = decoder()
        self.do(data_src, data_exp, test_block)


if __name__ == '__main__':
    gr_unittest.run(qa_decoder, "qa_decoder.xml")
