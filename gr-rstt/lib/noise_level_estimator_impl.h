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

#include <rstt/noise_level_estimator.h>
#include <vector>

namespace gr {
  namespace rstt {

    /*!
     * \brief Estimate noise level value in signal.
     *
     * It does so by spliting input signal power spectrum into chunks.
     * Then are identified chunks which contains only noise and
     * from which noise level (mean and dispersion) are estimated.
     */
    class noise_level_estimator_impl : public noise_level_estimator {
    public:
      /*! \brief Chunk of spectrum power data for noise estimation. */
      class Chunk {
        int _start;
        int _len;
        float _mean;
        float _extreme_val;
        int _extreme_rel_idx;

        inline void set_extreme(const float *data) {
          _extreme_val = 0;
          _extreme_rel_idx = 0;
          for (int idx = 0; idx < _len; ++idx) {
            float val = data[idx] - data[0] - _mean * idx;
            val = val < 0. ? -val : val;
            if (val > _extreme_val) {
              _extreme_val = val;
              _extreme_rel_idx = idx;
            }
          }
        }

        inline void reset(const float *data) {
          _mean = (_len > 1) ? (data[_len - 1] - data[0]) / (_len - 1) : 0.;
          set_extreme(data);
        }

      public:
        /*!
         * \brief Evaluate parameters for chunk of data
         * @param start index of first item in data for chunk
         * @param len lenght of chunk
         * @param data integrated value of signal spectrum power
         */
        Chunk(int start, int len, const float *data) :
          _start(start),
          _len(len)
        {
          reset(data + _start);
        }

        /*!
         * \brief transforms relative mean to absolute mean
         * @param data power level values
         */
        inline void shift_mean(const float *data) {
          _mean = (_mean * (_len - 1) + data[_start]) / _len;
        }

        inline Chunk split(const float *data) {
          const int idx2 = _start + _extreme_rel_idx + 1;
          const int len2 = _len - _extreme_rel_idx - 1;
          _len = _extreme_rel_idx + 1;
          reset(data + _start);
          return Chunk(idx2, len2, data);
        }

        inline void reset(int start, int len, const float *data) {
          this->_start = start;
          this->_len = len;
          reset(data + _start);
        }

        bool operator <(const Chunk &r) const
        {
          if (_extreme_val == r._extreme_val)
            return _len < r._len;
          return _extreme_val < r._extreme_val;
        }

        inline int start() const { return _start; }
        inline int len() const { return _len; }
        inline float mean() const { return _mean; }
        inline float extreme_val() const { return _extreme_val; }
        inline int extreme_rel_idx() const { return _extreme_rel_idx; };
      };

    private:

      float coverage;
      int nsplits;

// just optimalization, it avoids buffer alocation for each call of estimate()
      mutable std::vector<float> idata;
      mutable std::vector<Chunk> chunks;

     public:
      /*!
       * @param coverage is value in range from 0. to 1. It represents amount of
       *   signal power spectrum used for noise estimation. 0.2 is good value.
       * @param nsplits numer of fragmens generated for noise estimation.
       */
      noise_level_estimator_impl(float coverage, int nsplits) :
        coverage(coverage),
        nsplits(nsplits)
      {
        chunks.reserve(nsplits);
      }

      virtual ~noise_level_estimator_impl()
      {}

      /*!
       * \brief Do noise level estimation.
       *
       * @param data logarithm (natural) of signal power spectrum.
       * @param data_items length of input data.
       */
      noise_model estimate(const float *data, int data_items) const;
    };

    bool chunk_by_mean(const noise_level_estimator_impl::Chunk &l,
        const noise_level_estimator_impl::Chunk &r);

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_NOISE_LEVEL_ESTIMATOR_IMPL_H */

