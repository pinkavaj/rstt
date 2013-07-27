/* -*- c++ -*- */
/*
 * Copyright 2013 Jiří Pinkava <j-pi@seznam.cz>
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
#include "symbols2bits_impl.h"

#include <stdio.h>

namespace gr {
  namespace rstt {

    symbols2bits::sptr
    symbols2bits::make(int sync_nbits)
    {
      return gnuradio::get_initial_sptr
        (new symbols2bits_impl(sync_nbits));
    }

    symbols2bits_impl::symbols2bits_impl(int sync_nbits)
      : gr::block("symbols2bits",
              gr::io_signature::make(1, 1, sizeof(in_t)),
              gr::io_signature::make(1, 1, sizeof(out_t))),
        roll_out_nbits(0),
        sync_win_len(2*sync_nbits),
        sync_win_offs(0),
        sync_win(new win_t[sync_win_len]),
        sync_win_idx(0),
        fill_in_nsymbols(sync_win_len)
    {
        sync_win_nerrs[0] = sync_win_nerrs[1] = 0;
        memset(sync_win.get(), 1, sync_win_len*sizeof(win_t));
    }

    symbols2bits_impl::~symbols2bits_impl()
    {
    }

    void
    symbols2bits_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
        ninput_items_required[0] = 2 * noutput_items + fill_in_nsymbols + 1;
    }

    int
    symbols2bits_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const in_t *in = (const in_t *) input_items[0];
        out_t *out = (out_t *) output_items[0];

        int consume = ninput_items[0];
        int produced = work_fill(noutput_items, consume, in, out);

        if (!fill_in_nsymbols) {
          in += ninput_items[0] - consume;
          out += produced;
          noutput_items -= produced;
          produced += work_convert(noutput_items, consume, in, out);
        }

        consume_each(ninput_items[0] - consume);

        return produced;
    }

    bool
    symbols2bits_impl::is_out_of_sync() const
    {
        return (sync_win_offs == 0 && sync_win_nerrs[0] > sync_win_nerrs[1]) ||
          (sync_win_offs == 1 && sync_win_nerrs[0] < sync_win_nerrs[1]);
    }

    symbols2bits_impl::win_t
    symbols2bits_impl::put_symbol(const in_t *in)
    {
      const win_t val_old = sync_win[sync_win_idx];
      const win_t val_new = win_t(in[1]) - win_t(in[0]);
      sync_win[sync_win_idx] = val_new;
      sync_win_nerrs[sync_win_idx % 2] += abs(val_old) - abs(val_new);

      ++sync_win_idx;
      if (sync_win_idx == sync_win_len) {
        sync_win_idx = 0;
      }
      return val_old;
    }

    int
    symbols2bits_impl::roll_out(int out_len, int &consume, const in_t *in, out_t *out)
    {
        if (!roll_out_nbits) {
            return 0;
        }
        const int nroll = std::min(
            std::min(roll_out_nbits, out_len),
            consume/2);
        int produced = 0;
        for ( ; produced < nroll; ++produced) {
            shift_bite(in, out);
            ++out;
            in += 2;
            consume -= 2;
        }

        roll_out_nbits -= produced;
        if (roll_out_nbits) {
          return -produced;
        }
        if (is_out_of_sync()) {
            sync_win_offs = 1 - sync_win_offs;
        }
        return produced;
    }

    void
    symbols2bits_impl::shift_bite(const in_t *in, out_t *out)
    {
      const win_t val1 = put_symbol(in);
      const win_t val2 = put_symbol(in+1);
      const win_t val = sync_win_offs ? val2 : val1;
      if (val == -1) {
        out[0] = 0;
      } else if (val == 1) {
        out[0] = 1;
      } else {
        out[0] = -1;
      }
    }

    int
    symbols2bits_impl::work_convert(int out_len,
                       int &consume,
                       const in_t *in,
                       out_t *out)
    {
        int consume_ = consume; // bellow we do: in += consumed
        int produced = roll_out(out_len, consume, in, out);
        if (produced < 0) {
            return -produced;
        }
        in += consume_ - consume;
        out += produced;

        while (consume > 2 && produced < out_len) {
          if (is_out_of_sync()) {
            roll_out_nbits += sync_win_len/2 - std::max(sync_win_nerrs[0], sync_win_nerrs[1]);
            if (!roll_out_nbits) {
                sync_win_offs = 1 - sync_win_offs;
                continue;
            }
            consume_ = consume;
            const int p = roll_out(out_len - produced, consume, in, out);
            if (p < 0) {
                produced += -p;
                break;
            }
            produced += p;
            out += p;
            in += consume_ - consume;
            continue;
          }
          shift_bite(in, out);
          consume -= 2;
          in += 2;
          ++produced;
          ++out;
        }

        return produced;
    }

    int
    symbols2bits_impl::work_fill(int,
                       int &consume,
                       const in_t *in,
                       out_t *)
    {
        if (!fill_in_nsymbols) {
            return 0;
        }
        while (fill_in_nsymbols && consume > 1) {
            put_symbol(in);
            ++in;
            --consume;
            --fill_in_nsymbols;
        }

        if (!fill_in_nsymbols) {
            if (is_out_of_sync()) {
              sync_win_offs = 1 - sync_win_offs;
            }
        }

        return 0;
    }

  } /* namespace rstt */
} /* namespace gr */

