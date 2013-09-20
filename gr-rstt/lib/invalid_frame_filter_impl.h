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

#ifndef INCLUDED_RSTT_INVALID_FRAME_FILTER_IMPL_H
#define INCLUDED_RSTT_INVALID_FRAME_FILTER_IMPL_H

#include <rstt/invalid_frame_filter.h>

namespace gr {
  namespace rstt {

    class invalid_frame_filter_impl : public invalid_frame_filter
    {
     private:
      typedef short in_t;
      typedef short out_t;

      static bool chech_crc(const in_t *in, int len);

     public:
      invalid_frame_filter_impl();
      ~invalid_frame_filter_impl();

      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

      static bool is_frame_valid(const in_t *in);
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_INVALID_FRAME_FILTER_IMPL_H */

