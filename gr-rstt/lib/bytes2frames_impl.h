/* -*- c++ -*- */
/* 
 * Copyright 2013 Jiří Pinkava.
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

#ifndef INCLUDED_RSTT_BYTES2FRAMES_IMPL_H
#define INCLUDED_RSTT_BYTES2FRAMES_IMPL_H

#include <rstt/bytes2frames.h>

namespace gr {
  namespace rstt {

    class bytes2frames_impl : public bytes2frames
    {
     private:
      typedef short in_t;
      typedef short out_t;

      const static int PACKET_SIZE = 240;
      /** Need more data to find a frame. */
      bool more;

      int correlate(const in_t *in) const;
      int find_sync(const in_t *in) const;
      void send_packet(const in_t *in, out_t *out, int packet_size = PACKET_SIZE);
      int work(int out_len, int in_len, int &consumed, const in_t *in, out_t *out);

     public:
      bytes2frames_impl();
      ~bytes2frames_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_BYTES2FRAMES_IMPL_H */

