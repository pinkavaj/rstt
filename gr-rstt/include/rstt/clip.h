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

#ifndef INCLUDED_RSTT_CLIP_H
#define INCLUDED_RSTT_CLIP_H

#include <rstt/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace rstt {

    /*!
     * \brief Clip symmetrically both sides of vector, shrinking it from
     *      in_bw to out_bw.
     * \ingroup rstt
     *
     */
    class RSTT_API clip : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<clip> sptr;

      static sptr make(int vlen, float in_bw, float out_bw);
      static sptr make(int vlen_in, int trim);

      virtual int trim() const = 0;
      virtual int vlen_out() const = 0;
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_CLIP_H */

