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
extern "C" {
#include <gnuradio/fec/rs.h>
}
#include "byte_status.h"
#include "error_correction_impl.h"

namespace gr {
  namespace rstt {

    static const int rs_symsize = 8;
    static const int rs_gfpoly = 0x11d;
    static const int rs_fcr = 0;
    static const int rs_prim = 1;
    static const int rs_nroots = 24;

    static const int RS_N = (1 << rs_symsize) - 1;
    static const int RS_M = RS_N - rs_nroots;
    static const int FRAME_LEN = 240;
    static const int FRAME_HDR_LEN = 6;
    static const int FRAME_RS_LEN = rs_nroots;
    static const int FRAME_DATA_LEN = FRAME_LEN - FRAME_HDR_LEN - FRAME_RS_LEN;

    error_correction::sptr
    error_correction::make()
    {
      return gnuradio::get_initial_sptr
        (new error_correction_impl());
    }

    error_correction_impl::error_correction_impl()
      : gr::sync_block("error_correction",
              gr::io_signature::make(1, 1, sizeof(in_t)*FRAME_LEN),
              gr::io_signature::make(1, 1, sizeof(out_t)*FRAME_LEN))
    {
        rs = init_rs_char(rs_symsize, rs_gfpoly, rs_fcr, rs_prim, rs_nroots);
        assert (d_rs != 0);
    }

    error_correction_impl::~error_correction_impl()
    {
        free_rs_char(rs);
    }

    int
    error_correction_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const in_t *in = (const in_t *) input_items[0];
        out_t *out = (out_t *) output_items[0];

        for (int frame_num = 0; frame_num < noutput_items; ++frame_num) {
            if (!do_correction(in, out)) {
                memcpy(out, in, FRAME_LEN*sizeof(in_t));
            }
            in += FRAME_LEN;
            out += FRAME_LEN;
        }

        return noutput_items;
    }

    bool
    error_correction_impl::do_correction(const in_t *in, out_t *out) const
    {
        unsigned char rs_data[RS_N];
        int erasures[rs_nroots];
        int nerasures = 0;

        memset(rs_data, 0, sizeof(rs_data));
        for (int in_idx = FRAME_HDR_LEN; in_idx < FRAME_LEN; ++in_idx) {
            const int rs_idx = in_idx < FRAME_HDR_LEN + FRAME_DATA_LEN ?
                RS_M - 1 - (in_idx - FRAME_HDR_LEN) :
                RS_N - 1 - (in_idx - FRAME_HDR_LEN - FRAME_DATA_LEN);
            const in_t ival = in[in_idx];
            if (ival & gr::rstt::STATUS_ERR_BYTE) {
                if (nerasures >= rs_nroots) {
                    return false;
                }
                erasures[nerasures] = rs_idx;
                ++nerasures;
                continue;
            }
            rs_data[rs_idx] = ival;
        }

        const int ncorr = decode_rs_char(rs, rs_data, erasures, nerasures);
        if (ncorr == -1) {
            nerasures = 0;
            for (int in_idx = FRAME_HDR_LEN; in_idx < FRAME_LEN - FRAME_RS_LEN;
                    ++in_idx) {
                const int rs_idx = in_idx < FRAME_HDR_LEN + FRAME_DATA_LEN ?
                    RS_M - 1 - (in_idx - FRAME_HDR_LEN) :
                    RS_N - 1 - (in_idx - FRAME_HDR_LEN - FRAME_DATA_LEN);
                const in_t ival = in[in_idx];
                if (ival & (~0xff)) {
                    if (nerasures >= rs_nroots) {
                        return false;
                    }
                    erasures[nerasures] = rs_idx;
                    ++nerasures;
                    continue;
                }
            }
            const int ncorr2 = decode_rs_char(rs, rs_data, erasures, nerasures);
            if (ncorr2 == -1) {
                return false;
            }
        }

        // copy back corrected data and create new (correct) header
        out[0] = '*';
        out[1] = '*';
        out[2] = '*';
        out[3] = '*';
        out[4] = '*';
        out[5] = 0x10;
        for (int out_idx = FRAME_HDR_LEN; out_idx < FRAME_LEN; ++out_idx) {
            const int rs_idx = out_idx < (FRAME_HDR_LEN + FRAME_DATA_LEN) ?
                RS_M - 1 - (out_idx - FRAME_HDR_LEN) :
                RS_N - 1 - (out_idx - FRAME_HDR_LEN - FRAME_DATA_LEN);
            out[out_idx] = rs_data[rs_idx];
        }

        return true;
    }

  } /* namespace rstt */
} /* namespace gr */

