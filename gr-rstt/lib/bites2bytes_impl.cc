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
#include "bites2bytes_impl.h"

namespace gr {
  namespace rstt {

    bites2bytes::sptr
    bites2bytes::make(int sync_nbytes)
    {
      return gnuradio::get_initial_sptr
        (new bites2bytes_impl(sync_nbytes));
    }

    /*
     * The private constructor
     */
    bites2bytes_impl::bites2bytes_impl(int sync_nbytes)
      : gr::block("bites2bytes",
              gr::io_signature::make(1, 1, sizeof(in_t)),
              gr::io_signature::make(1, 1, sizeof(out_t)))
    {}

    /*
     * Our virtual destructor.
     */
    bites2bytes_impl::~bites2bytes_impl()
    {
    }

    void
    bites2bytes_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    }

    int
    bites2bytes_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const in_t *in = (const in_t *) input_items[0];
        out_t *out = (out_t *) output_items[0];

        // Do <+signal processing+>
        // Tell runtime system how many input items we consumed on
        // each input stream.
        consume_each (noutput_items);

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace rstt */
} /* namespace gr */

