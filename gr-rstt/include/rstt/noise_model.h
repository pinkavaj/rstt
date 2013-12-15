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

#ifndef INCLUDED_RSTT_NOISE_MODEL_H
#define INCLUDED_RSTT_NOISE_MODEL_H

#include <rstt/api.h>
#include <boost/shared_ptr.hpp>

namespace gr {
  namespace rstt {

    /*!
     * \brief Result of noise estimation.
     * \ingroup rstt
     */
    class RSTT_API noise_model {
     public:
      noise_model(float mean, float sigma) :
        _mean(mean), _sigma(sigma)
      {}

      /*!
       * \brief Return logarithm of power level estimation for noise/signal border.
       * @param snr must be greater or equal 1 to make sense. 2 or 3 is good value.
       */
      inline float lvl(float snr) const {
        return _mean + _sigma * snr;
      }

      inline float mean_lvl() const {
        return _mean;
      }

      inline float sigma() const {
        return _sigma;
      }

    protected:
      float _mean;
      float _sigma;
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_NOISE_MODEL_H */

