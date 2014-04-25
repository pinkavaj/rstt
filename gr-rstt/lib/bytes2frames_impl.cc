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
#include "bytes2frames_impl.h"
#include "byte_status.h"

namespace gr {
  namespace rstt {

    bytes2frames::sptr
    bytes2frames::make()
    {
        return gnuradio::get_initial_sptr
            (new bytes2frames_impl());
    }

    bytes2frames_impl::bytes2frames_impl()
      : gr::block("bytes2frames",
              gr::io_signature::make(1, 1, sizeof(in_t)),
              gr::io_signature::make(1, 1, sizeof(out_t)*PACKET_SIZE)),
        more(false)
    {}

    bytes2frames_impl::~bytes2frames_impl()
    {
    }

    int
    bytes2frames_impl::correlate(const in_t *in) const
    {
        // ignore all bite errors except 'invalid byte'
        const in_t _MASK = 0xff | STATUS_ERR_BYTE;

        int nerr = 0;
        for (unsigned char i = 0; i < 5; ++i) {
            nerr += ((in[i] & _MASK) == '*') ? 0 : 1;
        }
        if ((in[5] & _MASK) == 0x10) {
            if (nerr <= 3) {
                return nerr;
            }
            return 6;
        }

        // first and last '*' is required, to guess frame start mark
        // up to 3 error are tollerable (and 0x10 is missing)
        if (nerr <= 2) {
            if (in[0] & _MASK == '*' && in[4] & _MASK == '*') {
                return nerr + 1;
            }
        }

        return 6;
    }

    int
    bytes2frames_impl::find_sync(const in_t *in) const
    {
        int nerr_min = INT_MAX;
        int corr_idx = 0;
        for (int idx = 0; idx < PACKET_SIZE; ++idx) {
            const int nerr = correlate(in + idx);
            if (nerr < nerr_min) {
                nerr_min = nerr;
                corr_idx = idx;
                if (nerr == 0) {
                    break;
                }
            }
        }
        return (nerr_min < 6 && corr_idx > 0) ? corr_idx : PACKET_SIZE;
    }

    void
    bytes2frames_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
        const int n = noutput_items*PACKET_SIZE;
        ninput_items_required[0] = more ? n+239 : n;
    }

    int
    bytes2frames_impl::general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const in_t *in = (const in_t *) input_items[0];
        out_t *out = (out_t *) output_items[0];
        const int in_len = ninput_items[0];

        int consumed = 0;
        const int produced = work(noutput_items, in_len, consumed, in, out);
        consume_each(consumed);

        return produced;
    }

    void
    bytes2frames_impl::send_packet(const in_t *in, out_t *out, int packet_size)
    {
        const int missing = PACKET_SIZE - packet_size;
        for (int idx = 0; idx < missing; ++idx) {
            out[idx] = STATUS_ERR_STOP | STATUS_ERR_START | STATUS_ERR_BYTE;
        }
        memcpy(out+missing, in, (PACKET_SIZE-missing)*sizeof(out_t));
    }

    int
    bytes2frames_impl::work(int out_len,
            int in_len,
            int &consumed,
            const in_t *in,
            out_t *out)
    {
        int produced = 0;
        while (produced < out_len && consumed < in_len - 239) {
            const int nerr = correlate(in + consumed);
            more = false;
            if (nerr == 0) {
                send_packet(in + consumed, out + produced*PACKET_SIZE);
                ++produced;
                consumed += PACKET_SIZE;

                continue;
            }
            if (consumed >= in_len - 2*PACKET_SIZE + 1) {
                more = true;
                break;
            }
            int sync_idx = find_sync(in + consumed);

            send_packet(in + consumed, out + produced*PACKET_SIZE, sync_idx);
            ++produced;
            consumed += sync_idx;
        }
        return produced;
    }

  } /* namespace rstt */
} /* namespace gr */

