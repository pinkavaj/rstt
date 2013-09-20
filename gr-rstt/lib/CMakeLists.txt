# Copyright 2011,2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIRS})

list(APPEND rstt_sources
    symbols2bits_impl.cc
    bits2bytes_impl.cc
    bytes2frames_impl.cc
    error_correction_impl.cc
    decoder_impl.cc
)

add_library(gnuradio-rstt SHARED ${rstt_sources})
target_link_libraries(gnuradio-rstt ${Boost_LIBRARIES} ${GNURADIO_RUNTIME_LIBRARIES} ${GNURADIO_FEC_LIBRARIES})
set_target_properties(gnuradio-rstt PROPERTIES DEFINE_SYMBOL "gnuradio_rstt_EXPORTS")

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-rstt
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

include_directories(${CPPUNIT_INCLUDE_DIRS})

list(APPEND test_rstt_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/test_rstt.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/qa_rstt.cc
)

add_executable(test-rstt ${test_rstt_sources})

target_link_libraries(
  test-rstt
  ${GNURADIO_RUNTIME_LIBRARIES}
  ${GNURADIO_FEC_LIBRARIES}
  ${Boost_LIBRARIES}
  ${CPPUNIT_LIBRARIES}
  gnuradio-rstt
)

GR_ADD_TEST(test_rstt test-rstt)
