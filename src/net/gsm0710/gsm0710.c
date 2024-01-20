/*
 *
 * GSM 07.10 Implementation with User Space Serial Ports
 *
 * Copyright (C) 2003  Tuukka Karvonen <tkarvone@iki.fi>
 *
 * Version 1.0 October 2003
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
 * @see https://raw.githubusercontent.com/ya-jeks/gsmmux/
 */

#include <features.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <assert.h>

#include "buffer.h"
#include "gsm0710.h"

#define WRITE_RETRIES 5

#ifdef MICROPY_ENABLE_DYNRUNTIME
#include "py/dynruntime.h"
#define printf(...) mp_printf(&mp_plat_print, __VA_ARGS__)

void *malloc(size_t n) {
    void *ptr = m_malloc(n);
    return ptr;
}

void free(void *ptr) {
    m_free(ptr);
}
#endif

static const int max_frame_size = 127; // 31 - The limit of Sony-Ericsson GM47

static int write_frame(gsm0710_ctx_t *ctx, int channel, const uint8_t *input, int count, uint8_t type)
{
    // flag, EA=1 C channel, frame type, length 1-2
    uint8_t prefix[5] = {F_FLAG, EA | CR, 0, 0, 0};
    uint8_t postfix[2] = {0xFF, F_FLAG};
    int prefix_length = 4, c;

    printf("send frame to ch: %d \n", channel);
    // EA=1, Command, let's add address
    prefix[1] = prefix[1] | ((63 & (uint8_t)channel) << 2);
    // let's set control field
    prefix[2] = type;

    // let's not use too big frames
    count = min(max_frame_size, count);

    // length
    if (count > 127)
    {
        prefix_length = 5;
        prefix[3] = ((127 & count) << 1);
        prefix[4] = (32640 & count) >> 7;
    }
    else
    {
        prefix[3] = 1 | (count << 1);
    }
    // CRC checksum
    postfix[0] = make_fcs(prefix + 1, prefix_length - 1);

    c = ctx->write_sl(ctx, prefix, prefix_length);
    if (c != prefix_length)
    {
        printf("Couldn't write the whole prefix to the serial port for the virtual port %d. Wrote only %d  bytes.", channel, c);
        return 0;
    }
    if (count > 0)
    {
        c = ctx->write_sl(ctx, input, count);
        if (count != c)
        {
            printf("Couldn't write all data to the serial port from the virtual port %d. Wrote only %d bytes.\n", channel, c);
            return 0;
        }
    }
    c = ctx->write_sl(ctx, postfix, 2);
    if (c != 2)
    {
        printf("Couldn't write the whole postfix to the serial port for the virtual port %d. Wrote only %d bytes.", channel, c);
        return 0;
    }

    return count;
}

static int ussp_send_data(gsm0710_ctx_t *ctx, uint8_t *buf, int n, int port)
{
    ctx->on_read_vl(ctx, port, buf, n);
    return n;
}

/* Handles commands received from the control channel.
 */
static void handle_command(gsm0710_ctx_t *ctx, GSM0710_Frame *frame)
{
    uint8_t type, signals;
    int length = 0, i, type_length, supported = 1;
    uint8_t *response;

    if (frame->data_length > 0)
    {
        type = frame->data[0]; // only a byte long types are handled now
        // skip extra bytes
        for (i = 0; (frame->data_length > i && (frame->data[i] & EA) == 0); i++)
        {
        }

        i++;
        type_length = i;
        if ((type & CR) == CR)
        {
            // command not ack

            // extract frame length
            while (frame->data_length > i)
            {
                length = (length * 128) + ((frame->data[i] & 254) >> 1);
                if ((frame->data[i] & 1) == 1)
                    break;
                i++;
            }
            i++;

            switch ((type & ~CR))
            {
            case C_CLD:
                ctx->terminate = __LINE__;
                break;
            case C_TEST:
                break;
            case C_MSC:
                if (i + 1 < frame->data_length)
                {
                    i++;
                    signals = (frame->data[i]);
                    printf("C_MSC: Signal: %d \r\n", signals);
                }
                break;
            default:
                printf( "Unknown command (%d) from the control channel.\n", type);
                response = (uint8_t *)malloc(sizeof(uint8_t) * (2 + type_length));
                response[0] = C_NSC;
                // supposes that type length is less than 128
                response[1] = EA & ((127 & type_length) << 1);
                i = 2;
                while (type_length--)
                {
                    response[i] = frame->data[(i - 2)];
                    i++;
                }
                write_frame(ctx, 0, response, i, UIH);
                free(response);
                supported = 0;
                break;
            }

            if (supported)
            {
                // acknowledge the command
                frame->data[0] = frame->data[0] & ~CR;
                write_frame(ctx, 0, frame->data, frame->data_length, UIH);
            }
        }
        else
        {
            // received ack for a command
            if (COMMAND_IS(C_NSC, type))
            {
                printf("The mobile station didn't support the command sent.\n");
            }
        }
    }
}

/* Extracts and handles frames from the receiver buffer.
 *
 * PARAMS:
 * buf - the receiver buffer
 */
static int extract_frames(gsm0710_ctx_t *ctx)
{

    // version test for Siemens terminals to enable version 2 functions
    //static const uint8_t version_test[] = "\x23\x21\x04TEMUXVERSION2\0\0";
    int framesExtracted = 0;
    GSM0710_Buffer *buf = ctx->in_buf;

    GSM0710_Frame *frame;

    while ((frame = gsm0710_buffer_get_frame(buf)))
    {
        ++framesExtracted;
        if ((FRAME_IS(UI, frame) || FRAME_IS(UIH, frame)))
        {
            if (frame->channel > 0)
            {
                ussp_send_data(ctx, frame->data, frame->data_length, frame->channel - 1);
            }
            else
            {
                handle_command(ctx, frame);
            }
        }
        else
        {
            switch ((frame->control & ~PF))
            {
            case UA:
                if (ctx->cstatus[frame->channel].opened == 1)
                {
                    ctx->cstatus[frame->channel].opened = 0;
                }
                else
                {
                    ctx->cstatus[frame->channel].opened = 1;
                    // if (frame->channel == 0)
                    // {
                    //     write_frame(ctx, 0, version_test, sizeof(version_test), UIH);
                    // }
                    printf("Open channel: %d \r\n", frame->channel);
                }
                break;
            case DM:
                if (ctx->cstatus[frame->channel].opened)
                {
                    printf("Close channel: %d \r\n", frame->channel);
                    ctx->cstatus[frame->channel].opened = 0;
                }
                else
                {
                    if (frame->channel == 0)
                    {
                        printf("Couldn't open control channel.\n->Terminating.\n");
                        ctx->terminate = __LINE__;
                    }
                }
                break;
            case DISC:
                if (ctx->cstatus[frame->channel].opened)
                {
                    ctx->cstatus[frame->channel].opened = 0;
                    write_frame(ctx, frame->channel, NULL, 0, UA | PF);
                    if (frame->channel == 0)
                    {
                        printf("Control channel closed.\n");
                        ctx->terminate = __LINE__;
                    }
                    else
                    {
                        printf("Logical channel %d closed.\n", frame->channel);
                    }
                }
                else
                {
                    // channel already closed
                    printf("Received DISC even though channel %d was already closed.\n", frame->channel);
                    write_frame(ctx, frame->channel, NULL, 0, DM | PF);
                }
                break;
            case SABM:
                // channel open request
                if (ctx->cstatus[frame->channel].opened == 0)
                {
                    if (frame->channel == 0)
                    {
                        printf("Control channel opened.\n");
                    }
                    else
                    {
                        printf("Logical channel %d opened.\n", frame->channel);
                    }
                }
                else
                {
                    // channel already opened
                    printf("Received SABM even though channel %d was already closed.\n", frame->channel);
                }
                ctx->cstatus[frame->channel].opened = 1;
                write_frame(ctx, frame->channel, NULL, 0, UA | PF);
                break;
            }
        }

        destroy_frame(frame);
    }
    return framesExtracted;
}

size_t on_read_sl(gsm0710_ctx_t *ctx, const void *buf, size_t len)
{
    if (ctx->terminate)
    {
        if (ctx->on_fault)
        {
            ctx->on_fault(ctx, ctx->terminate);
        }
        return 0;
    }

    size_t size = gsm0710_buffer_free(ctx->in_buf);
    if (size > 0)
    {
        len = min(size, len);
        gsm0710_buffer_write(ctx->in_buf, buf, len);
        // extract and handle ready frames
        extract_frames(ctx);
        return len;
    }

    return 0;
}

size_t write_vl(gsm0710_ctx_t *ctx, uint8_t port, const uint8_t *buf, size_t len)
{
    int written = 0;
    int i = 0;
    int last = 0;

    if (ctx->terminate)
    {
        if (ctx->on_fault)
        {
            ctx->on_fault(ctx, ctx->terminate);
        }
        return 0;
    }

    // try to write 5 times
    while (written != len && i < WRITE_RETRIES)
    {
        last = write_frame(ctx, port, &buf[written], len - written, UIH);
        written += last;
        if (last == 0)
        {
            i++;
        }
    }
    if (i == WRITE_RETRIES)
    {
        printf("Couldn't write data to channel %d. Wrote only %d bytes, when should have written %ld.\n", port, written, (long)len);
    }
    return written;
}

void open_mux(gsm0710_ctx_t *ctx, uint8_t num_of_ports)
{
    
    assert(ctx->on_read_vl);
    assert(ctx->write_sl);
    
    if (ctx->in_buf == NULL)
    {
        ctx->in_buf = gsm0710_buffer_init();
        assert(ctx->in_buf);
    }

    printf("Opening control channel.\n");
    write_frame(ctx, 0, NULL, 0, SABM | PF);
    printf("Opening logical channels.\n");
    if (num_of_ports > MAX_CHANNEL_COUNT)
    {
        num_of_ports = MAX_CHANNEL_COUNT;
        printf("maximum could be %d channels\r\n", MAX_CHANNEL_COUNT);
    }

    for (uint8_t i = 1; i <= num_of_ports - 1; i++)
    {
        ctx->cstatus[i].opened = 0;
        write_frame(ctx, i, NULL, 0, SABM | PF);
        printf("Connecting to virtual channel %d \r\n", i);
    }
}

void close_mux(gsm0710_ctx_t *ctx)
{
    const uint8_t _close_mux[1] = {C_CLD | CR};
    write_frame(ctx, 0, _close_mux, sizeof(_close_mux), UIH);
    gsm0710_buffer_destroy(ctx->in_buf);
}
