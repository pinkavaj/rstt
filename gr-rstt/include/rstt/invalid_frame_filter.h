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

#ifndef INCLUDED_RSTT_INVALID_FRAME_FILTER_H
#define INCLUDED_RSTT_INVALID_FRAME_FILTER_H

#include <rstt/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace rstt {

    /*!
     * \brief Drop frames with no valid subframes (chech subframe CRC).
     * \ingroup rstt
     */
    class RSTT_API invalid_frame_filter : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<invalid_frame_filter> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of rstt::invalid_frame_filter.
       *
       * To avoid accidental use of raw pointers, rstt::invalid_frame_filter's
       * constructor is in a private implementation
       * class. rstt::invalid_frame_filter::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_INVALID_FRAME_FILTER_H */

