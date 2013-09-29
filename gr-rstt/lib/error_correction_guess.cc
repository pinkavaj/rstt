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

#include "error_correction_guess.h"
#include <string.h>

namespace gr {
  namespace rstt {

    int
    error_correction_guess::predicate::operator()(int val, int idx)
    {
      if (idx >= LEN) {
        if (val & (~0xff)) {
          return -1;
        }
        return val;
      }
      if (changes_cnt[idx] > erasure_level && next_level > changes_cnt[idx]) {
        next_level = changes_cnt[idx];
      }
      if (changes_cnt[idx] < replace_level) {
        return prev_data[idx];
      }
      if (changes_cnt[idx] < erasure_level) {
        return val == prev_data[idx] ? val : -1;
      }
      if (val & (~0xff)) {
        return -1;
      }
      return val;
    }

    void
    error_correction_guess::update(const unsigned short *data)
    {
      ++update_count;
      if (update_count == 0) {
        memset(chenges_cnt, 0, sizeof(int)*LEN);
        for (int x = 0; x < LEN; ++x) {
          prev_data[x] = data[x];
        }
        return;
      }
      for (int x = 0; x < LEN; ++x) {
        if (prev_data[x] != (data[x] & 0xff)) {
          prev_data[x] = data[x] & 0xff;
          chenges_cnt[x] += 1;
        }
      }
      if (update_count == 512) {
        update_count /= 2;
        for (int x = 0; x < LEN; ++x) {
          chenges_cnt[x] /= 2;
        }
      }
    }

    int
    error_correction_guess::get_level(int level) const {
      if (update_count < 1) {
        level = 0;
      } else if (update_count > 256) {
        level = level * update_count / 256;
      }
      return level;
    }

  } // namespace rstt
} // namespace gr

