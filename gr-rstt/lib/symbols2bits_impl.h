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

#ifndef INCLUDED_RSTT_SYMBOLS2BITS_IMPL_H
#define INCLUDED_RSTT_SYMBOLS2BITS_IMPL_H

#include <rstt/symbols2bits.h>
#include <boost/shared_array.hpp>

namespace gr {
  namespace rstt {

    class symbols2bits_impl : public symbols2bits
    {
     private:
      typedef unsigned char in_t;
      typedef signed char out_t;
      typedef signed char win_t;

      /** Number of error in even/odd synchronization windw. */
      int sync_win_nerrs[2];
      /** Number of bits to send before normal operation can continue. */
      int roll_out_nbits;
      /** Lenght of synchronization window. */
      int sync_win_len;
      /** Current synchronized window, odd = 0, even = 1. */
      int sync_win_offs;
      /** Synchronization window length. */
      boost::shared_array<win_t> sync_win;
      /** Fill buffers with nsymbols before normal operation can start. */
      int sync_win_idx;
      int fill_in_nsymbols;

      bool is_out_of_sync() const;

      win_t put_symbol(const in_t *in);

      int roll_out(int out_len,
              int &consume,
              const in_t *in,
              out_t *out);

      void shift_bite(const in_t *in, out_t *out);

      int work_convert(int out_len,
              int &consume,
              const in_t *in,
              out_t *out);

      int work_fill(int out_len,
              int &consume,
              const in_t *in,
              out_t *out);

     public:
      symbols2bits_impl(int sync_nbits);
      ~symbols2bits_impl();

      void forecast(int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_SYMBOLS2BITS_IMPL_H */

