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


#ifndef INCLUDED_RSTT_SYMBOLS2BITES_H
#define INCLUDED_RSTT_SYMBOLS2BITES_H

#include <rstt/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace rstt {

    /*!
     * \brief <+description of block+>
     * \ingroup rstt
     *
     */
    class RSTT_API symbols2bites : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<symbols2bites> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of rstt::symbols2bites.
       *
       * To avoid accidental use of raw pointers, rstt::symbols2bites's
       * constructor is in a private implementation
       * class. rstt::symbols2bites::make is the public interface for
       * creating new instances.
       */
      static sptr make(int sync_nbites);
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_SYMBOLS2BITES_H */

