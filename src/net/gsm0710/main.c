#include <stdio.h>
#include "gsm0710.h"

static gsm0710_ctx_t ctx = {};

void print_hex(const void *data, size_t len)
{
    for (size_t i = 0; i < len - 1; i++)
    {
        printf("%02x-", ((const uint8_t *)data)[i]);
    }
    printf("%02x \r\n", ((const uint8_t *)data)[len - 1]);
}

static void __mock_on_fault(uint32_t line)
{
    fprintf(stderr, "Error in LINE: %d \r\n", line);
}

static void __mock_on_read_vl(uint8_t port, const void *buf, size_t len)
{
    printf("Recv@%d: [len: %d - %p] \r\n", port, (int)len, buf);
    print_hex(buf, len);
}

static size_t __mock_write_sl(const void *data, size_t len)
{
    printf("Write-serial: %d \r\n", (int)len);
    print_hex(data, len);
    return len;
}

void init(uint8_t num_ch)
{
    open_mux(&ctx, num_ch);
}

void set_on_fault(void (*cb)(uint32_t))
{
    ctx.on_fault = cb;
}

void set_on_read_vl(void (*cb)(uint8_t, const void *, size_t))
{
    ctx.on_read_vl = cb;
}

void set_write_sl(size_t (*cb)(const void *, size_t))
{
    ctx.write_sl = cb;
}

void on_read_serial(const uint8_t *data, size_t sz)
{
    on_read_sl(&ctx, data, sz);
}

size_t write_virtual(uint8_t port, const uint8_t *data, size_t sz)
{
    return write_vl(&ctx, port, data, sz);
}

void deinit()
{
    close_mux(&ctx);
}

int main()
{
    ctx.on_fault = __mock_on_fault;
    ctx.on_read_vl = __mock_on_read_vl;
    ctx.write_sl = __mock_write_sl;

    // mux will send hello to 3 pipes
    open_mux(&ctx, 3);

    // simulate the answer
    // 'f9037301d7f9',
    const uint8_t buf0[] = {0xf9, 0x03, 0x73, 0x01, 0xd7, 0xf9};
    on_read_sl(&ctx, &buf0, sizeof(buf0));

    // f907730115f9
    const uint8_t buf1[] = {0xf9, 0x07, 0x73, 0x01, 0x15, 0xf9};
    on_read_sl(&ctx, &buf1, sizeof(buf1));

    // f90b730192f9
    const uint8_t buf2[] = {0xf9, 0x0b, 0x73, 0x01, 0x92, 0xf9};
    on_read_sl(&ctx, &buf2, sizeof(buf2));

    // f90f730150f9
    const uint8_t buf3[] = {0xf9, 0x0f, 0x73, 0x01, 0x50, 0xf9};
    on_read_sl(&ctx, &buf3, sizeof(buf3));

    return 0;
}