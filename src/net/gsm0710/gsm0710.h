#ifndef _GSM0710_H_
#define _GSM0710_H_

/*
 * gsm0710.h -- definitions needed by the gsm0710 protocol daemon.
 *
 * Copyright (C) 2003 Tuukka Karvonen <tkarvone@iki.fi>
 *
 * Version 1.0 October 2003
 *
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 *
 */

#include <stddef.h>
#include <stdint.h>
#include "buffer.h"

/** @see https://raw.githubusercontent.com/ya-jeks/gsmmux/ */

// basic mode flag for frame start and end
#define F_FLAG 0xF9

// bits: Poll/final, Command/Response, Extension
#define PF 16
#define CR 2
#define EA 1
// the types of the frames
#define SABM 47
#define UA 99
#define DM 15
#define DISC 67
#define UIH 239
#define UI 3
// the types of the control channel commands
#define C_CLD 193
#define C_TEST 33
#define C_MSC 225
#define C_NSC 17
// V.24 signals: flow control, ready to communicate, ring indicator, data valid
// three last ones are not supported by Siemens TC_3x
#define S_FC 2
#define S_RTC 4
#define S_RTR 8
#define S_IC 64
#define S_DV 128

#define COMMAND_IS(command, type) ((type & ~CR) == command)
#define PF_ISSET(frame) ((frame->control & PF) == PF)
#define FRAME_IS(type, frame) ((frame->control & ~PF) == type)

#define MAX_CHANNEL_COUNT 4

// Channel status tells if the DLC is open and what were the last
// v.24 signals sent
typedef struct _channel_status
{
	uint8_t opened;
} channel_status_t;

typedef struct _gsm0710_ctx
{
	uint32_t terminate;
	channel_status_t cstatus[MAX_CHANNEL_COUNT];
	GSM0710_Buffer *in_buf;
	
	/**
	 * @brief Write into real serial-line
	 * @param buf Output data
	 * @param len Output size
	 */
	size_t (*write_sl)(const void *, size_t); 
	
	/**
	 * @brief On recieve in virtual line
	 * @param port Port number
	 * @param data Read data (output-data)
	 * @param len Length of read data
	 */
	void (*on_read_vl)(uint8_t, const void *, size_t);
	
	/**
	 * @brief On fault
	 * Will be called if terminate set to 1 somewhere
	 * @param err Error number (line number in gsm0710.c)
	*/
	void (*on_fault)(uint32_t);
} gsm0710_ctx_t;

/**
 * @brief Opens MUX
 * @param ctx Mux context
 * @param num_of_ports Number of opened ports
*/
void open_mux(gsm0710_ctx_t *ctx, uint8_t num_of_ports);

/**
 * @brief Closes mux (Closes control line)
 * @param ctx Mux context
*/
void close_mux(gsm0710_ctx_t *ctx);

/**
 * @brief should be called on incoming data from real serial port
 * @param ctx Mux context
 * @param buf Output data
 * @param len Output data len
*/
size_t on_read_sl(gsm0710_ctx_t *ctx, const void* buf, size_t len);

/**
 * @brief Writing into virtual port
 * @param ctx Mux context
 * @param port Port number 
 * @param buf Output data
 * @param len Output data len
*/
size_t write_vl(gsm0710_ctx_t *ctx, uint8_t port, const uint8_t* buf, size_t len);

#endif /* _GSM0710_H_ */
