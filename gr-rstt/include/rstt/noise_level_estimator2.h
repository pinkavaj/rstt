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

#ifndef INCLUDED_RSTT_NOISE_LEVEL_ESTIMATOR2_H
#define INCLUDED_RSTT_NOISE_LEVEL_ESTIMATOR2_H

#include <rstt/api.h>
#include <boost/shared_ptr.hpp>
#include <rstt/noise_model.h>

namespace gr {
  namespace rstt {

    /*!
     * Estimate noise level value in signal.

     * It find parts of signal power spectrum with low power density.
     * Noise level and straggling is then estiated.
     */
    class RSTT_API noise_level_estimator2 {
     protected:
       noise_level_estimator2()
       {}

     public:
      typedef boost::shared_ptr<noise_level_estimator2> sptr;

      /*!
       * @param coverage size of spectrum used for noise estimation,
       *    Expects value in range (0., 1.), 0.33 is good value.
       * @param chunk_size size of continous part of spectrum containign
       *    only noise, should be value in range (0., 1), 0.05 is good value.
       */
      static sptr
      make(float coverage, float chunk_size);

      virtual ~noise_level_estimator2()
      { }

      /*!
       * Do noise level estimation.
       *
       * @param data (natural) logarithm of signal power spectrum.
       * @param data_items length of input data.
       */
      virtual noise_model estimate(const float *data, int data_items) const = 0;
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_NOISE_LEVEL_ESTIMATOR2_H */

