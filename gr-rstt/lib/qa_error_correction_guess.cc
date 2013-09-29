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

#include "qa_error_correction_guess.h"
#include "error_correction_guess.h"
#include <cppunit/TestAssert.h>

namespace gr {
  namespace rstt {

    static const int LEN = 240;
    static const int VAL_INC = 16;

    void
    init_data(int *changes_cnt, int cnt, unsigned char *prev_data,
        int *data, int *data_exp)
    {
      for (int i = 0; i < LEN-24; ++i) {
        changes_cnt[i] = cnt;
        data_exp[i] = data[i] = prev_data[i] = i + VAL_INC;
      }
      for (int i = LEN-24; i < LEN; ++i) {
        data_exp[i] = data[i] = i + VAL_INC;
      }
    }

    void
    qa_error_correction_guess::t1_ok()
    {
      int changes_cnt[LEN-24];
      unsigned char prev_data[LEN-24];
      int data[LEN];
      int data_exp[LEN];

      init_data(changes_cnt, 0, prev_data, data, data_exp);

      error_correction_guess::predicate predicate(changes_cnt, prev_data, 0, 0);

      for (int i = 0; i < LEN; ++i) {
        CPPUNIT_ASSERT(predicate(data[i], i) == data_exp[i]);
      }
    }

    void
    qa_error_correction_guess::t2()
    {
      int changes_cnt[LEN-24];
      unsigned char prev_data[LEN-24];
      int data[LEN];
      int data_exp[LEN];

      init_data(changes_cnt, 8, prev_data, data, data_exp);
      changes_cnt[8] = 0;
      data[8] = 1;

      error_correction_guess::predicate predicate(changes_cnt, prev_data, 1, 1);

      for (int i = 0; i < LEN; ++i) {
        CPPUNIT_ASSERT(predicate(data[i], i) == data_exp[i]);
      }
    }

    void
    qa_error_correction_guess::t3()
    {
      int changes_cnt[LEN-24];
      unsigned char prev_data[LEN-24];
      int data[LEN];
      int data_exp[LEN];

      init_data(changes_cnt, 8, prev_data, data, data_exp);
      changes_cnt[8] = 0;
      changes_cnt[9] = 1;
      data[8] = 1;
      data[9] = 1;
      data_exp[9] = -1;

      error_correction_guess::predicate predicate(changes_cnt, prev_data, 1, 2);

      for (int i = 0; i < LEN; ++i) {
        CPPUNIT_ASSERT(predicate(data[i], i) == data_exp[i]);
      }
    }

  } /* namespace rstt */
} /* namespace gr */

