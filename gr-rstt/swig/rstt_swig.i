/* -*- c++ -*- */

#define RSTT_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "rstt_swig_doc.i"

%{
#include "rstt/symbols2bits.h"
#include "rstt/bits2bytes.h"
#include "rstt/bytes2frames.h"
#include "rstt/error_correction.h"
%}


%include "rstt/symbols2bits.h"
GR_SWIG_BLOCK_MAGIC2(rstt, symbols2bits);
%include "rstt/bits2bytes.h"
GR_SWIG_BLOCK_MAGIC2(rstt, bits2bytes);
%include "rstt/bytes2frames.h"
GR_SWIG_BLOCK_MAGIC2(rstt, bytes2frames);
%include "rstt/error_correction.h"
GR_SWIG_BLOCK_MAGIC2(rstt, error_correction);
