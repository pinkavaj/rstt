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


#ifndef _QA_INVALID_FRAME_FILTER_H_
#define _QA_INVALID_FRAME_FILTER_H_

#include <cppunit/extensions/HelperMacros.h>
#include <cppunit/TestCase.h>

namespace gr {
  namespace rstt {

    class qa_error_correction : public CppUnit::TestCase
    {
    public:
      CPPUNIT_TEST_SUITE(qa_error_correction);
      CPPUNIT_TEST(t1);
      CPPUNIT_TEST(t2);
      CPPUNIT_TEST(t3);
      CPPUNIT_TEST_SUITE_END();

    private:
      void t1();
      void t2();
      void t3();
    };

  } /* namespace rstt */
} /* namespace gr */

#endif /* _QA_INVALID_FRAME_FILTER_H_ */

