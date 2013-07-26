/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "bits2bytes_impl.h"

namespace gr {
  namespace rstt {

    bits2bytes::sptr
    bits2bytes::make(int sync_nbytes)
    {
      return gnuradio::get_initial_sptr
        (new bits2bytes_impl(sync_nbytes));
    }

    bits2bytes_impl::bits2bytes_impl(int sync_nbytes)
      : gr::block("bits2bytes",
              gr::io_signature::make(1, 1, sizeof(in_t)),
              gr::io_signature::make(1, 1, sizeof(out_t))),
        sync_nbits(10*sync_nbytes),
        fill_in_bits(sync_nbits),
        in_idx(0),
        do_bit_resync(true),
        send_bytes_remain(0),
        sync_win_idx(0),
        sync_offs(0)
    {
        memset(sync_win, 0, sizeof(sync_win));
    }

    bits2bytes_impl::~bits2bytes_impl()
    {
    }

    void
    bits2bytes_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
        ninput_items_required[0] = 10*noutput_items + sync_nbits + 20;
    }

    int
    bits2bytes_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const in_t *in = (const in_t *) input_items[0];
        out_t *out = (out_t *) output_items[0];
        const int in_len = ninput_items[0];

        if (!work_fill(in_len, in)) {
            return 0;
        }
        const int produced = work_convert(noutput_items, in_len, in, out);
        const int consume = in_idx - sync_nbits;
        consume_each(consume);
        in_idx -= consume;

        return produced;
    }

    bits2bytes_impl::out_t
    bits2bytes_impl::get_byte(const in_t *in, bool start_bite_missing) const
    {
        out_t status = STATUS_INVALID_START;
        int idx = in_idx - sync_nbits;
        if (!start_bite_missing) {
            if (in[idx++] == 0) {
                status = 0;
            }
        }
        out_t B = 0;
        for (const int end = idx + 8; idx < end; ++idx) {
            const in_t b = in[idx];
            B >>= 1;
            if (b == -1) {
                status |= STATUS_INVALID_BYTE;
                continue;
            }
            B |= b << 7;
        }
        if (in[idx] != 1) {
            status |= STATUS_INVALID_STOP;
        }
        return B | status;
    }

    int
    bits2bytes_impl::get_sync_offs() const
    {
        // by default try to keep sync at current position
        int sync_offs_new = sync_offs;
        int max = sync_win[sync_offs_new];
        // preffer sync to +-1 bit
        if (sync_win[(sync_offs - 1) % 10] > max) {
            sync_offs_new = (sync_offs - 1) % 10;
            max = sync_win[sync_offs_new];
        } else
        if (sync_win[(sync_offs + 1) % 10] > max) {
            sync_offs_new = (sync_offs + 1) % 10;
            max = sync_win[sync_offs_new];
        }
        // check for sync at other positions
        for (int i = 0; i < 10; ++i) {
            if (sync_win[i] > max) {
                sync_offs_new = i;
                max = sync_win[sync_offs_new];
            }
        }

        return sync_offs_new;
    }

    int
    bits2bytes_impl::resync_stream(int out_len, int produced, int in_len,
        const in_t *in, out_t *out)
    {
        if (!do_bit_resync && send_bytes_remain == 0) {
            return produced;
        }
        while (produced < out_len && in_idx < in_len - 9 && send_bytes_remain) {
            out[produced++] = get_byte(in);
            shift_bits(in);
            --send_bytes_remain;
        }
        if (send_bytes_remain) {
            return -produced;
        }
        const int of = get_sync_offs();
        const int shift = (of - sync_offs) % 10;
        if (shift == 9) {
            if (in_idx < in_len - 18 && produced < out_len) {
                out[produced++] = get_byte(in, true);
                shift_bits(in, 9);
                sync_offs = of;
                do_bit_resync = false;
                return produced;
            }
        } else {
            if (shift == 0) {
                do_bit_resync = false;
                return produced;
            }
            if (in_idx < in_len - 9 - shift) {
                shift_bits(in, shift);
                sync_offs = of;
                do_bit_resync = false;
                return produced;
            }
        }

        return -produced;
    }

    void bits2bytes_impl::shift_bits(const in_t *in, int nbits)
    {
        for (const int end = in_idx + nbits; in_idx < end; ++in_idx) {
            const in_t _b0 = in[in_idx - sync_nbits];
            const in_t _b9 = in[in_idx - sync_nbits + 9];
            const in_t b0 = in[in_idx];
            const in_t b9 = in[in_idx + 9];

            sync_win_idx_pp((b0 == 0 && b9 == 1) - (_b0 == 0 && _b9 == 1));
        }
    }

    void
    bits2bytes_impl::sync_win_idx_pp(int inc) {
        sync_win[sync_win_idx++] += inc;
        if (sync_win_idx > 9) {
            sync_win_idx = 0;
        }
    }

    int
    bits2bytes_impl::work_convert(int out_len,
        int in_len,
        const in_t *in,
        out_t *out)
    {
        if (in_idx >= in_len - 19 || 0 >= out_len) {
            return 0;
        }
        int produced = resync_stream(out_len, 0, in_len, in, out);
        if (produced < 0) {
            return -produced;
        }
        while (in_idx < in_len - 19 && produced < out_len) {
            const int so = get_sync_offs();
            if (so != sync_offs) {
                send_bytes_remain = sync_nbits / 10 / 2 - 1;
                produced = resync_stream(out_len, produced, in_len, in, out);
                if (produced < 0) {
                    return -produced;
                }
                continue;
            }
            out[produced++] = get_byte(in);
            shift_bits(in);
        }
        return produced;
    }

    bool
    bits2bytes_impl::work_fill(int in_len, const in_t *in)
    {
        if (!fill_in_bits) {
            return true;
        }

        const int len = in_idx + std::min(fill_in_bits, in_len - in_idx - 9);
        for ( ; in_idx < len; ++in_idx ) {
            sync_win_idx_pp(in[in_idx] == 0 && in[in_idx + 9] == 1);
        }
        fill_in_bits -= len;
        return fill_in_bits == 0;
    }

  } /* namespace rstt */
} /* namespace gr */

