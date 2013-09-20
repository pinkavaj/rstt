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
 * 
 */

#ifndef INCLUDED_RSTT_DECODER_IMPL_H
#define INCLUDED_RSTT_DECODER_IMPL_H

#include <rstt/decoder.h>
#include <rstt/bits2bytes.h>
#include <rstt/bytes2frames.h>
#include <rstt/error_correction.h>
#include <rstt/invalid_frame_filter.h>
#include <rstt/symbols2bits.h>

namespace gr {
  namespace rstt {

    class decoder_impl : public decoder
    {
     private:
       typedef unsigned char in_t;
       typedef short out_t;

       bits2bytes::sptr fbits2bytes;
       bytes2frames::sptr fbytes2frames;
       error_correction::sptr ferror_correction;
       invalid_frame_filter::sptr finvalid_frame_filter;
       symbols2bits::sptr fsymbols2bits;

     public:
      decoder_impl(int sync_nbits, int sync_nbytes, bool drop_invalid);
      ~decoder_impl();
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_DECODER_IMPL_H */

