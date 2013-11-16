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

#include "noise_level_estimator_impl.h"
#include <algorithm>
#include <boost/foreach.hpp>
#include <cmath>

#include <stdio.h>

namespace gr {
  namespace rstt {

    bool chunk_by_mean(const noise_level_estimator_impl::Chunk &l,
        const noise_level_estimator_impl::Chunk &r)
    {
      if (l.mean() == r.mean())
        return l.len() < r.len();
      return l.mean() < r.mean();
    }

    noise_level_estimator::sptr
    noise_level_estimator::make(float coverage, int nsplits)
    {
      return sptr(new noise_level_estimator_impl(coverage, nsplits));
    }

    noise_model
    noise_level_estimator_impl::estimate(const float *data, int data_items) const
    {
      idata.resize(data_items);
      float prev = 0;
      for (int idx = 0; idx < data_items; ++idx) {
        prev = idata[idx] = data[idx] + prev;
      }

      chunks.clear();
      chunks.push_back(Chunk(0, data_items, idata.data()));
      for (int chunkno = 0; chunkno < nsplits; ++chunkno) {
        Chunk chunk = chunks.back();
        chunks.pop_back();
        Chunk new_chunk = chunk.split(idata.data());
        chunks.insert(
            std::lower_bound(chunks.begin(), chunks.end(), chunk), chunk);
        chunks.insert(
            std::lower_bound(chunks.begin(), chunks.end(), new_chunk), new_chunk);
      }

      BOOST_FOREACH(Chunk &chunk, chunks) {
        chunk.shift_mean(data);
      }
      std::sort(chunks.begin(), chunks.end(), chunk_by_mean);

      float mean = 0;
      float sigma = 0;
      int len = 0;
      BOOST_FOREACH(Chunk &chunk, chunks) {
        mean += chunk.mean() * chunk.len();
        for (int idx = chunk.start(); idx < chunk.start() + chunk.len(); ++idx) {
          sigma += data[idx] * data[idx];
        }
        len += chunk.len();
        if (len >= coverage * data_items)
          break;
      }

      mean /= len;
      sigma = sqrt(sigma/len - mean*mean) * 2;

      return noise_model(mean, sigma);
    }

  } // namespace rstt
} // namespace gr

