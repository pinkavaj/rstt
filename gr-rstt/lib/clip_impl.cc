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
#include <math.h>
#include "clip_impl.h"

namespace gr {
  namespace rstt {

    clip::sptr
    clip::make(int vlen_in, float bw_in, float bw_out)
    {
      const int trim = roundf(vlen_in * (bw_in - bw_out) / bw_in / 2.);
      if (0 > trim || 2 * trim >= vlen_in) {
        throw std::out_of_range(
            "gr::rstt::clip condition (0 <= 2 * trim < vlen_out) unsatisfied.");
      }

      return make(vlen_in, trim);
    }

    clip::sptr
    clip::make(int vlen_in, int trim)
    {
      return gnuradio::get_initial_sptr(new clip_impl(vlen_in, trim));
    }

    clip_impl::clip_impl(int vlen_in, int trim)
      : gr::sync_block("clip",
              gr::io_signature::make(1, 1, sizeof(float) * vlen_in),
              gr::io_signature::make(1, 1, sizeof(float) * (vlen_in - 2 * trim))),
      _trim(trim),
      _vlen_out(vlen_in - 2 * trim)
    {}

    int clip_impl::trim() const
    {
      return _trim;
    }

    int clip_impl::vlen_out() const
    {
      return _vlen_out;
    }

    clip_impl::~clip_impl()
    {}

    int
    clip_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const float *in = (const float *) input_items[0];
        float *out = (float *) output_items[0];

        for (int ni = 0, no = 0; no < noutput_items * _vlen_out; ) {
          ni += _trim;
          memcpy(out + no, in + ni, _vlen_out * sizeof(float));
          no += _vlen_out;
          ni += _vlen_out;
          ni += _trim;
        }

        return noutput_items;
    }

  } /* namespace rstt */
} /* namespace gr */

