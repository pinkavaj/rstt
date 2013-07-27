/* -*- c++ -*- */
/* 
 * Copyright 2013 Jiří Pinkava
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

#include <stdio.h>

namespace gr {
  namespace rstt {

    const bytes2frames_impl::sync_byte_t bytes2frames_impl::SYNC_BYTES[]  = {
      { 0, 0x2A },
      { 1, 0x2A },
      { 2, 0x2A },
      { 3, 0x2A },
      { 4, 0x2A },
      { 5, 0x10 },
      { 6, 0x65 },
      { 7, 0x10 },
      { 42, 0x69 },
      { 43, 0x0C },
      { 70, 0x3D },
      { 71, 0x94 },
      { 196, 0x68 },
      { 197, 0x05 },
      { 210, 0xff },
      { 211, 0x02 },
    };

    const int bytes2frames_impl::NSYNC_BYTES = sizeof(bytes2frames_impl::SYNC_BYTES) /
        sizeof(bytes2frames_impl::sync_byte_t);

    bytes2frames::sptr
    bytes2frames::make(float threshold)
    {
        return gnuradio::get_initial_sptr
            (new bytes2frames_impl(threshold));
    }

    bytes2frames_impl::bytes2frames_impl(float threshold)
      : gr::block("bytes2frames",
              gr::io_signature::make(1, 1, sizeof(in_t)),
              gr::io_signature::make(1, 1, sizeof(out_t)*240)),
        threshold(round(16*threshold)),
        more(false)
    {}

    bytes2frames_impl::~bytes2frames_impl()
    {
    }

    int
    bytes2frames_impl::correlate(const in_t *in) const
    {
        int corr = 0;
        for (int n = 0; n < NSYNC_BYTES; ++n) {
            corr += (in[SYNC_BYTES[n].idx] & 0xff == SYNC_BYTES[n].value);
        }
        return corr;
    }

    int
    bytes2frames_impl::find_sync(const in_t *in) const
    {
        int corr_max = 0;
        int corr_idx = 0;
        for (int idx = 0; idx < PACKET_SIZE; ++idx) {
            const int corr = correlate(in + idx);
            if (corr > corr_max) {
                corr_max = corr;
                corr_idx = idx;
            }
        }
        return corr_max > 0 ? corr_idx : PACKET_SIZE;
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

    int
    bytes2frames_impl::send_packet(const in_t *in, out_t *out, int packet_size)
    {
        const int missing = PACKET_SIZE - packet_size;
        for (int idx = 0; idx < missing; ++idx) {
            out[idx] = STATUS_ERR_STOP | STATUS_ERR_START | STATUS_ERR_BYTE;
        }
        memcpy(out+missing, in, (PACKET_SIZE-missing)*sizeof(out_t));
        int corr = 0;
        for (int n = 0; n < NSYNC_BYTES; ++n) {
            if ((out[SYNC_BYTES[n].idx] & 0xff) == SYNC_BYTES[n].value) {
                ++corr;
            } else {
                out[SYNC_BYTES[n].idx] |= STATUS_ERR_SYN;
            }
        }
        return corr >= threshold;
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
            const int nsync = correlate(in + consumed);
            more = false;
            if (nsync == NSYNC_BYTES) {
                produced += send_packet(in + consumed, out + produced*PACKET_SIZE);
                consumed += PACKET_SIZE;

                continue;
            }
            if (consumed < in_len - 240 - 239) {
                more = true;
                break;
            }
            int sync_idx = find_sync(in + consumed);
            sync_idx = sync_idx > 0 ? sync_idx : PACKET_SIZE;

            produced += send_packet(in + consumed, out + produced*PACKET_SIZE, sync_idx);
            consumed += sync_idx;
        }
        return produced;
    }

  } /* namespace rstt */
} /* namespace gr */

