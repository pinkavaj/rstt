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

#ifndef INCLUDED_RSTT_NOISE_LEVEL_ESTIMATOR_IMPL_H
#define INCLUDED_RSTT_NOISE_LEVEL_ESTIMATOR_IMPL_H

#include <rstt/noise_level_estimator2.h>
#include <vector>

namespace gr {
  namespace rstt {

    /*!
     * \brief Estimate noise level value in signal.
     */
    class noise_level_estimator2_impl : public noise_level_estimator2 {
    private:

      float coverage;
      float chunk_size;

     public:
      noise_level_estimator2_impl(float coverage, float chunk_size) :
        coverage(coverage),
        chunk_size(chunk_size)
      {
      }

      virtual ~noise_level_estimator2_impl()
      {}

      /*!
       * \brief Do noise level estimation.
       *
       * @param data logarithm (natural) of signal power spectrum.
       * @param data_items length of input data.
       */
      noise_model estimate(const float *data, int data_items) const;
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_NOISE_LEVEL_ESTIMATOR_IMPL_H */

