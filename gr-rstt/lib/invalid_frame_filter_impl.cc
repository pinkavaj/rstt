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
#include <boost/crc.hpp>
#include "invalid_frame_filter_impl.h"

#include <stdio.h>

namespace gr {
  namespace rstt {

    static const int FRAME_LEN = 240;

    invalid_frame_filter::sptr
    invalid_frame_filter::make()
    {
      return gnuradio::get_initial_sptr
        (new invalid_frame_filter_impl());
    }

    invalid_frame_filter_impl::invalid_frame_filter_impl()
      : gr::block("invalid_frame_filter",
              gr::io_signature::make(1, 1, sizeof(in_t)*FRAME_LEN),
              gr::io_signature::make(1, 1, sizeof(out_t)*FRAME_LEN))
    {}

    invalid_frame_filter_impl::~invalid_frame_filter_impl()
    {}

    void
    invalid_frame_filter_impl::forecast (int noutput_items,
            gr_vector_int &ninput_items_required)
    {
        ninput_items_required[0] = noutput_items;
    }

    int
    invalid_frame_filter_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const in_t *in = (const in_t *) input_items[0];
        out_t *out = (out_t *) output_items[0];

        int out_idx = 0;
        int in_idx = 0;
        for (; in_idx < ninput_items[0] && out_idx < noutput_items; ++in_idx) {
            if (!is_frame_valid(in+FRAME_LEN*in_idx)) {
                continue;
            }
            memcpy(out + FRAME_LEN * out_idx, in + FRAME_LEN * in_idx,
                    sizeof(in_t) * FRAME_LEN);
            ++out_idx;
        }
        consume_each (in_idx);

        return out_idx;
    }

    bool
    invalid_frame_filter_impl::is_frame_valid(const in_t *in)
    {
        const in_t *const in_end = in + FRAME_LEN - 24;
        in += 6;
        while(in < in_end) {
            const in_t type = in[0] & 0xff;
            const int len = in[1] * 2;
            if (type == 0xff) {
                break;
            }
            if (in + 2 + len + 2 <= in_end) {
                if (chech_crc(in + 2, len)) {
                    return true;
                }
            }
            in += 2 + len + 2;
        }
        return false;
    }
    bool
    invalid_frame_filter_impl::chech_crc(const in_t *in, int len)
    {
        boost::crc_ccitt_type crc;

        for (int i = 0; i < len; ++i) {
            crc.process_byte(in[i] & 0xff);
        }
        boost::crc_ccitt_type::value_type crc_exp =
              (in[len] & 0xff) | ((in[len + 1] & 0xff) << 8);

        return crc.checksum() == crc_exp;
    }

  } /* namespace rstt */
} /* namespace gr */

