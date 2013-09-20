/* -*- c++ -*- */
/* 
 * Copyright 2013 Jiří Pinkava <j-pi@seznam.cz>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "decoder_impl.h"

namespace gr {
  namespace rstt {

    decoder::sptr
    decoder::make(int sync_nbits, int sync_nbytes, bool drop_invalid)
    {
      return gnuradio::get_initial_sptr
        (new decoder_impl(sync_nbits, sync_nbytes, drop_invalid));
    }

    decoder_impl::decoder_impl(int sync_nbits, int sync_nbytes, bool drop_invalid)
      : gr::hier_block2("decoder",
              gr::io_signature::make(1, 1, sizeof(in_t)),
              gr::io_signature::make(1, 1, sizeof(out_t)*240))
    {
        fbits2bytes = bits2bytes::make(sync_nbytes);
        fbytes2frames = bytes2frames::make();
        ferror_correction = error_correction::make();
        fsymbols2bits = symbols2bits::make(sync_nbits);

        connect(self(), 0, fsymbols2bits, 0);
        connect(fsymbols2bits, 0, fbits2bytes, 0);
        connect(fbits2bytes, 0, fbytes2frames, 0);
        connect(fbytes2frames, 0, ferror_correction, 0);
        if (drop_invalid) {
            finvalid_frame_filter = invalid_frame_filter::make();
            connect(ferror_correction, 0, finvalid_frame_filter, 0);
            connect(finvalid_frame_filter, 0, self(), 0);
        } else {
            connect(ferror_correction, 0, self(), 0);
        }
    }

    decoder_impl::~decoder_impl()
    {}

  } /* namespace rstt */
} /* namespace gr */

