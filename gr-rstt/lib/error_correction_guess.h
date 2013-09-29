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

#ifndef INCLUDED_RSTT_ERROR_CORRECTION_GUESS_H
#define INCLUDED_RSTT_ERROR_CORRECTION_GUESS_H

namespace gr {
  namespace rstt {

    /**
      Collect statistics, trying to find constant bytes.
    */
    class error_correction_guess {
      static const int LEN = 240-24;

      int chenges_cnt[LEN];
      unsigned char prev_data[LEN];
      int update_count;

     public:
      class predicate {
        const int *changes_cnt;
        const unsigned char *prev_data;
        int replace_level, erasure_level;
        int next_level;

       public:
        predicate(const int *changes_cnt, const unsigned char *prev_data,
            int replace_level, int erasure_level) :
          changes_cnt(changes_cnt),
          prev_data(prev_data),
          replace_level(replace_level),
          erasure_level(erasure_level),
          next_level(257)
        {}

        int operator()(int val, int idx);

        inline int get_next_level() const
        {
          return next_level;
        }
      };

      error_correction_guess() :
        // first call of update() initializes internal state, it is not real update
        update_count(-1)
      {}

      void update(const unsigned short *data);
      int get_level(int level) const;

      inline predicate get_predicate(int replace_level, int erasure_level) const
      {
        return predicate(chenges_cnt, prev_data,
            get_level(replace_level), get_level(erasure_level));
      }
    };

  } // namespace rstt
} // namespace gr

#endif /* INCLUDED_RSTT_ERROR_CORRECTION_GUESS_H */

