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

#include "py/dynruntime.h"

#include "gsm0710.h"

#ifndef STATIC
#define STATIC static
#endif

mp_obj_full_type_t gsm0710_type;

#define container_of(ptr, type, member) ({                 \
    const __typeof__(((type *)0)->member) *__mptr = (ptr); \
    (type *)((char *)__mptr - offsetof(type, member));     \
})

typedef struct _gsm0710_obj_t
{
    mp_obj_base_t base;
    gsm0710_ctx_t ctx;
    mp_obj_t _write_sl_cb;
    mp_obj_t _on_fault_cb;
    mp_obj_t _on_read_vl_cb;
} gsm0710_obj_t;

STATIC mp_obj_t gsm0710_set_on_fault(mp_obj_t self_in, mp_obj_t cb)
{
    (void)self_in;

    gsm0710_obj_t *self = MP_OBJ_TO_PTR(self_in);
    self->_on_fault_cb = cb;
    mp_printf(&mp_plat_print, "%s:%d \r\n", __FILE__, __LINE__);
    return mp_const_none;
}

MP_DEFINE_CONST_FUN_OBJ_2(mp_gsm0710_set_on_fault_obj, gsm0710_set_on_fault);

STATIC mp_obj_t gsm0710_set_on_read_vl(mp_obj_t self_in, mp_obj_t cb)
{
    (void)self_in;

    gsm0710_obj_t *self = MP_OBJ_TO_PTR(self_in);
    self->_on_read_vl_cb = cb;
    mp_printf(&mp_plat_print, "%s:%d \r\n", __FILE__, __LINE__);
    return mp_const_none;
}

MP_DEFINE_CONST_FUN_OBJ_2(mp_gsm0710_set_on_read_vl_obj, gsm0710_set_on_read_vl);

STATIC mp_obj_t gsm0710_set_write_sl(mp_obj_t self_in, mp_obj_t cb)
{
    gsm0710_obj_t *self = MP_OBJ_TO_PTR(self_in);
    self->_write_sl_cb = cb;
    mp_printf(&mp_plat_print, "%s:%d \r\n", __FILE__, __LINE__);
    return mp_const_none;
}

MP_DEFINE_CONST_FUN_OBJ_2(mp_gsm0710_set_write_sl_obj, gsm0710_set_write_sl);

STATIC mp_obj_t gsm0710_on_read_serial(mp_obj_t self_in, mp_obj_t data)
{
    gsm0710_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(data, &bufinfo, MP_BUFFER_READ);

    on_read_sl(&self->ctx, bufinfo.buf, bufinfo.len);
    mp_printf(&mp_plat_print, "%s:%d \r\n", __FILE__, __LINE__);
    return mp_const_none;
}

MP_DEFINE_CONST_FUN_OBJ_2(mp_gsm0710_on_read_serial_obj, gsm0710_on_read_serial);

STATIC mp_obj_t gsm0710_write_virtual(size_t n_args, const mp_obj_t *args)
{
    if (n_args < 3)
    {
        mp_printf(&mp_plat_print, "%s:%d n_args: %lld\r\n", __FILE__, __LINE__, n_args);
        return mp_const_none;
    }

    gsm0710_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    uint8_t port = mp_obj_get_int(args[1]);

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(args[2], &bufinfo, MP_BUFFER_READ);

    mp_printf(&mp_plat_print, "%s:%d port: %d buf[%d]: %p\r\n", __FILE__, __LINE__, port, bufinfo.len, bufinfo.buf);
    return mp_obj_new_int(write_vl(&self->ctx, port, bufinfo.buf, bufinfo.len));
}

MP_DEFINE_CONST_FUN_OBJ_VAR(mp_gsm0710_write_virtual_obj, 3, gsm0710_write_virtual);

STATIC mp_obj_t gsm0710_deinit(mp_obj_t self_in)
{
    mp_printf(&mp_plat_print, "%s:%d \r\n", __FILE__, __LINE__);
    gsm0710_obj_t *self = MP_OBJ_TO_PTR(self_in);
    close_mux(&self->ctx);
    return mp_const_none;
}

MP_DEFINE_CONST_FUN_OBJ_1(mp_gsm0710_deinit_obj, gsm0710_deinit);

STATIC void _on_fault_mock(gsm0710_ctx_t *ctx, uint32_t err)
{

    gsm0710_obj_t *self = container_of(ctx, gsm0710_obj_t, ctx);
    if (self->_on_fault_cb != MP_OBJ_NULL)
    {
        mp_obj_t args[1];
        args[0] = mp_obj_new_int(err);
        mp_call_function_n_kw(self->_on_fault_cb, 1, 0, args);
    }
}

STATIC void _on_read_vl_mock(gsm0710_ctx_t *ctx, uint8_t port, const void *buf, size_t sz)
{
    gsm0710_obj_t *self = container_of(ctx, gsm0710_obj_t, ctx);

    if (self->_on_read_vl_cb != MP_OBJ_NULL)
    {
        const mp_obj_str_t _bytes_obj = {{&mp_type_bytes}, 0, sz, buf};
        mp_obj_t args[3];
        args[0] = MP_OBJ_FROM_PTR(self);
        args[1] = mp_obj_new_int(port);
        args[2] = MP_OBJ_FROM_PTR(&_bytes_obj);

        mp_call_function_n_kw(self->_on_read_vl_cb, 3, 0, args);
    }
}

STATIC size_t _write_sl_mock(gsm0710_ctx_t *ctx, const void *buf, size_t sz)
{
    gsm0710_obj_t *self = container_of(ctx, gsm0710_obj_t, ctx);
    if (self->_write_sl_cb != MP_OBJ_NULL)
    {
        const mp_obj_str_t _bytes_obj = {{&mp_type_bytes}, 0, sz, buf};
        mp_obj_t args[2];
        args[0] = MP_OBJ_FROM_PTR(self);
        args[1] = MP_OBJ_FROM_PTR(&_bytes_obj);

        return mp_obj_get_int(mp_call_function_n_kw(self->_write_sl_cb, 2, 0, args));
    }
    return 0;
}

STATIC mp_obj_t gsm0710_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args_in)
{
    (void)n_args;
    (void)args_in;
    (void)n_kw;

    gsm0710_obj_t *self = mp_obj_malloc(gsm0710_obj_t, type);
    self->_on_fault_cb = MP_OBJ_NULL;
    self->_on_read_vl_cb = MP_OBJ_NULL;
    self->_write_sl_cb = MP_OBJ_NULL;

    self->ctx.on_read_vl = _on_read_vl_mock;
    self->ctx.write_sl = _write_sl_mock;
    self->ctx.on_fault = _on_fault_mock;

    return MP_OBJ_FROM_PTR(self);
}

mp_map_elem_t gsm0710_locals_dict_table[6];
STATIC MP_DEFINE_CONST_DICT(gsm0710_locals_dict, gsm0710_locals_dict_table);

// This is the entry point and is called when the module is imported
mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args)
{
    // This must be first, it sets up the globals dict and other things
    MP_DYNRUNTIME_INIT_ENTRY

    mp_store_global(MP_QSTR___name__, MP_OBJ_NEW_QSTR(MP_QSTR_gsm0710));

    gsm0710_type.base.type = mp_fun_table.type_type;
    gsm0710_type.name = MP_QSTR_gsm0710_ctrl;
    MP_OBJ_TYPE_SET_SLOT(&gsm0710_type, make_new, &gsm0710_make_new, 0);

    gsm0710_locals_dict_table[0] = (mp_map_elem_t){MP_OBJ_NEW_QSTR(MP_QSTR_gsm0710_deinit), MP_OBJ_FROM_PTR(&mp_gsm0710_deinit_obj)};
    gsm0710_locals_dict_table[1] = (mp_map_elem_t){MP_OBJ_NEW_QSTR(MP_QSTR_gsm0710_write_virtual), MP_OBJ_FROM_PTR(&mp_gsm0710_write_virtual_obj)};
    gsm0710_locals_dict_table[2] = (mp_map_elem_t){MP_OBJ_NEW_QSTR(MP_QSTR_gsm0710_on_read_serial), MP_OBJ_FROM_PTR(&mp_gsm0710_on_read_serial_obj)};
    gsm0710_locals_dict_table[3] = (mp_map_elem_t){MP_OBJ_NEW_QSTR(MP_QSTR_gsm0710_set_write_sl), MP_OBJ_FROM_PTR(&mp_gsm0710_set_write_sl_obj)};
    gsm0710_locals_dict_table[4] = (mp_map_elem_t){MP_OBJ_NEW_QSTR(MP_QSTR_gsm0710_set_on_read_vl), MP_OBJ_FROM_PTR(&mp_gsm0710_set_on_read_vl_obj)};
    gsm0710_locals_dict_table[5] = (mp_map_elem_t){MP_OBJ_NEW_QSTR(MP_QSTR_gsm0710_set_on_fault), MP_OBJ_FROM_PTR(&mp_gsm0710_set_on_fault_obj)};

    MP_OBJ_TYPE_SET_SLOT(&gsm0710_type, locals_dict, (void *)&gsm0710_locals_dict, 2);

    mp_store_global(MP_QSTR_gsm0710, MP_OBJ_FROM_PTR(&gsm0710_type));
    // This must be last, it restores the globals dict
    MP_DYNRUNTIME_INIT_EXIT
}