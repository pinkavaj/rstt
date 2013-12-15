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

#include "noise_level_estimator2_impl.h"
#include <algorithm>
#include <boost/foreach.hpp>
#include <cmath>
#include <stdexcept>

#include <stdio.h>

namespace gr {
  namespace rstt {

    noise_level_estimator2::sptr
    noise_level_estimator2::make(float coverage, float chunk_size)
    {
      if (!(coverage > 0.))
        throw std::out_of_range("noise_level_estimator2 coverage must be > 0.");
      if (!(coverage <= 1.))
        throw std::out_of_range("noise_level_estimator2 coverage must be <= 1.");
      if (!(chunk_size > 0.))
        throw std::out_of_range("noise_level_estimator2 chunk_size must be > 0.");
      if (!(chunk_size <= coverage))
        throw std::out_of_range("noise_level_estimator2 chunk_size must be <= coverage");
      return sptr(new noise_level_estimator2_impl(coverage, chunk_size));
    }

    noise_model
    noise_level_estimator2_impl::estimate(const float *data, int data_items) const
    {
      const int coverage = data_items * this->coverage;
      const int chunk_size = data_items * this->chunk_size;

      const int ms_size = data_items - chunk_size + 1;
      float mean[ms_size];
      float mean2[ms_size];

      // moving average, first point
      mean[0] = 0.;
      mean2[0] = 0.;
      for (int i = 0; i < chunk_size; ++i) {
        mean[0] += data[i];
        mean2[0] += data[i] * data[i];
      }

      // moving average, other points
      for (int i = chunk_size, j = 1; i < data_items; ++i, ++j) {
       mean[j] = mean[j-1] - data[j-1] + data[i];
       mean2[j] = mean2[j-1] - (data[j-1] * data[j-1]) + (data[i] * data[i]);
      }

      for (int i = 0; i < ms_size; ++i) {
        mean[i] /= chunk_size;
        mean2[i] /= chunk_size;
      }

      // moving standard deviation (s^2)
      float s2[ms_size];
      for (int i = 0; i < ms_size; ++i) {
        s2[i] = mean2[i] - mean[i] * mean[i];
      }

      // get the average of lower bound values for mean and deviation
      std::sort(s2, s2 + ms_size);
      float s = 0.;
      for (int i = 0; i < coverage; ++i) {
        s += std::sqrt(s2[i]);
      }
      s /= coverage;

      std::sort(mean, mean + ms_size);
      float m = 0.;
      for (int i = 0; i < coverage; ++i) {
        m += mean[i];
      }
      m /= coverage;

      return noise_model(m, s);
    }

  } // namespace rstt
} // namespace gr

