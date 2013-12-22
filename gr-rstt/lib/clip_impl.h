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

#ifndef INCLUDED_RSTT_CLIP_IMPL_H
#define INCLUDED_RSTT_CLIP_IMPL_H

#include <rstt/clip.h>

namespace gr {
  namespace rstt {

    class clip_impl : public clip
    {
     private:
      int _trim;
      int _vlen_out;

     public:
      clip_impl(int vlen_in, int trim);
      ~clip_impl();

      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);

      virtual int trim() const;
      virtual int vlen_out() const;
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_CLIP_IMPL_H */

