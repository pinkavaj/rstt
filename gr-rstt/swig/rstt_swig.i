/* -*- c++ -*- */

#define RSTT_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "rstt_swig_doc.i"

%{
#include "rstt/symbols2bites.h"
%}


%include "rstt/symbols2bites.h"
GR_SWIG_BLOCK_MAGIC2(rstt, symbols2bites);
