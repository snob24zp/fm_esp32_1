/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2016 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "py/stream.h"
#include "py/dynruntime.h"

mp_obj_full_type_t gsm0710_type;

typedef struct _gsm0710_obj_t
{
    mp_obj_base_t base;
    uint8_t uart_num;
    uint16_t timeout;      // timeout waiting for first char (in ms)
    uint16_t timeout_char; // timeout waiting between chars (in ms)
} gsm0710_obj_t;


STATIC mp_uint_t gsm0710_read(mp_obj_t self_in, void *buf_in, mp_uint_t size, int *errcode)
{
    gsm0710_obj_t *self = MP_OBJ_TO_PTR(self_in);
    (void)self;
    (void)self_in;
    (void)buf_in;
    (void)size;
    (void)errcode;

    return 0;
}

STATIC mp_uint_t gsm0710_write(mp_obj_t self_in, const void *buf_in, mp_uint_t size, int *errcode)
{
    gsm0710_obj_t *self = MP_OBJ_TO_PTR(self_in);
    (void)self;
    (void)self_in;
    (void)buf_in;
    (void)errcode;

    return size;
}

STATIC mp_uint_t gsm0710_ioctl(mp_obj_t self_in, mp_uint_t request, uintptr_t arg, int *errcode)
{
    gsm0710_obj_t *self = self_in;
    (void)request;
    (void)arg;
    (void)self;
    (void)errcode;
    return 0;
}


// Re-implemented from py/stream.c, not yet available in dynruntime.h.
mp_obj_t mp_stream_close(mp_obj_t stream) {
    const mp_stream_p_t *stream_p = mp_get_stream(stream);
    int error;
    mp_uint_t res = stream_p->ioctl(stream, MP_STREAM_CLOSE, 0, &error);
    if (res == MP_STREAM_ERROR) {
        mp_raise_OSError(error);
    }
    return mp_const_none;
}

MP_DEFINE_CONST_FUN_OBJ_1(mp_stream_close_obj, mp_stream_close);


STATIC const mp_stream_p_t gsm0710_stream_p = {
     .read = gsm0710_read,
     .write = gsm0710_write,
     .ioctl = gsm0710_ioctl,
     .is_text = false,
};


STATIC mp_obj_t gsm0710_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args_in) {

    mp_int_t uart_num = n_args > 1 ? mp_obj_get_int(args_in[0]) : 0;
    mp_int_t timeout = n_args > 1 ? mp_obj_get_int(args_in[1]) : 0;

    gsm0710_obj_t *self = mp_obj_malloc(gsm0710_obj_t, type);
    self->uart_num = uart_num;
    self->timeout = timeout;
    self->timeout_char = 0;

    return MP_OBJ_FROM_PTR(self);
}


mp_map_elem_t gsm0710_locals_dict_table[5];
STATIC MP_DEFINE_CONST_DICT(gsm0710_locals_dict, gsm0710_locals_dict_table);


// This is the entry point and is called when the module is imported
mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args) {
    // This must be first, it sets up the globals dict and other things
    MP_DYNRUNTIME_INIT_ENTRY

    (void)gsm0710_locals_dict;
    (void)gsm0710_make_new;
    (void)gsm0710_stream_p;

    mp_store_global(MP_QSTR___name__, MP_OBJ_NEW_QSTR(MP_QSTR_gsm0710));
    
    gsm0710_type.base.type = mp_fun_table.type_type;
    gsm0710_type.name = MP_QSTR_gsm0710_ctrl;
    MP_OBJ_TYPE_SET_SLOT(&gsm0710_type, make_new, &gsm0710_make_new, 0);
    MP_OBJ_TYPE_SET_SLOT(&gsm0710_type, protocol, &gsm0710_stream_p, 1);
    gsm0710_locals_dict_table[0] = (mp_map_elem_t){ MP_OBJ_NEW_QSTR(MP_QSTR_read), MP_OBJ_FROM_PTR(&mp_stream_read_obj) };
    gsm0710_locals_dict_table[1] = (mp_map_elem_t){ MP_OBJ_NEW_QSTR(MP_QSTR_readinto), MP_OBJ_FROM_PTR(&mp_stream_readinto_obj) };
    gsm0710_locals_dict_table[2] = (mp_map_elem_t){ MP_OBJ_NEW_QSTR(MP_QSTR_readline), MP_OBJ_FROM_PTR(&mp_stream_unbuffered_readline_obj) };
    gsm0710_locals_dict_table[3] = (mp_map_elem_t){ MP_OBJ_NEW_QSTR(MP_QSTR_write), MP_OBJ_FROM_PTR(&mp_stream_write_obj) };
    gsm0710_locals_dict_table[4] = (mp_map_elem_t){ MP_OBJ_NEW_QSTR(MP_QSTR_close), MP_OBJ_FROM_PTR(&mp_stream_close_obj) };
    MP_OBJ_TYPE_SET_SLOT(&gsm0710_type, locals_dict, (void*)&gsm0710_locals_dict, 2);

    mp_store_global(MP_QSTR_gsm0710, MP_OBJ_FROM_PTR(&gsm0710_type));
    // This must be last, it restores the globals dict
    MP_DYNRUNTIME_INIT_EXIT
}