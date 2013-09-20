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

#ifndef INCLUDED_RSTT_BITS2BYTES_H
#define INCLUDED_RSTT_BITS2BYTES_H

#include <rstt/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace rstt {

    /*!
     * \brief Convert bit stream to byte stream.
     * \ingroup rstt
     *
     */
    class RSTT_API bits2bytes : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<bits2bytes> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of rstt::bits2bytes.
       *
       * To avoid accidental use of raw pointers, rstt::bits2bytes's
       * constructor is in a private implementation
       * class. rstt::bits2bytes::make is the public interface for
       * creating new instances.
       */
      static sptr make(int sync_nbytes);
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_BITS2BYTES_H */

