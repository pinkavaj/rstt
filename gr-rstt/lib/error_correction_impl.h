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

#ifndef INCLUDED_RSTT_ERROR_CORRECTION_IMPL_H
#define INCLUDED_RSTT_ERROR_CORRECTION_IMPL_H

#include <rstt/error_correction.h>

namespace gr {
  namespace rstt {

    class error_correction_impl : public error_correction
    {
     private:
      typedef short in_t;
      typedef short out_t;

      /** Try guess some byte values if correction fails. */
      bool guess;
      /** Map sync byte position to value. */
      std::map<int, unsigned char> syn_bytes;
      /** Reed-Solomon codec data. */
      void *rs;
      bool do_correction(const in_t *in, out_t *out) const;

     public:
      error_correction_impl(bool guess);
      ~error_correction_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_ERROR_CORRECTION_IMPL_H */

