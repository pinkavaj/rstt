/* 
 * Copyright 2013 Jiří Pinkava.
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

#ifndef INCLUDED_RSTT_BYTE_STATUS_H
#define INCLUDED_RSTT_BYTE_STATUS_H

namespace gr {
  namespace rstt {
      /** Error states for recieved byte. */
      typedef enum {
          STATUS_ERR_START = 0x100,
          STATUS_ERR_BYTE = 0x200,
          STATUS_ERR_STOP = 0x400
      } byte_status_t;
  }
}

#endif
