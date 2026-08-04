#!/usr/bin/env python3
"""
Изолированный тест класса AckFramingBuffer (потоковый конвейер UART -> MQTT).
Не требует железа / board.py, проверяет только логику фрейминга.
"""
import sys
sys.path.insert(0, 'src')

import consts

# --- Эмуляция MicroPython time API для CPython ---
import time as _time
if not hasattr(_time, 'ticks_ms'):
    _fake_ticks = [0]
    def _ticks_ms():
        return _fake_ticks[0]
    def _ticks_diff(a, b):
        return a - b
    _time.ticks_ms = _ticks_ms
    _time.ticks_diff = _ticks_diff
    _time._fake_ticks = _fake_ticks


class AckFramingBuffer:
    '''
    Zero-copy конвейер UART -> MQTT.
    Накопление байт из маленького C-буфера UART в единый глобальный bytearray.
    Отправка кадра происходит строго по таймауту тишины на линии UART.
    '''
    def __init__(self, device_id: int):
        self.hdr = f'{{"dev":{device_id},"val":"'.encode()
        self.ftr = b'"}'

        self.hdr_len = len(self.hdr)
        self.ftr_len = len(self.ftr)

        self.max_frame_size = self.hdr_len + consts.MAX_UART_PAYLOAD_LEN + self.ftr_len
        self.buf = bytearray(self.max_frame_size)

        self.buf[0:self.hdr_len] = self.hdr

        self.payload_len = 0
        self.last_rx_time = 0

    def append_chunk(self, chunk: bytes) -> bool:
        chunk_len = len(chunk)

        if self.payload_len + chunk_len > consts.MAX_UART_PAYLOAD_LEN:
            print(f"[UART] Переполнение! Пакет превысил {consts.MAX_UART_PAYLOAD_LEN} B")
            self.payload_len = 0
            return False

        write_pos = self.hdr_len + self.payload_len
        self.buf[write_pos:write_pos + chunk_len] = chunk

        self.payload_len += chunk_len
        self.last_rx_time = _time.ticks_ms()
        return True

    def try_flush(self, send_mqtt_cb, send_uart_cb) -> bool:
        if self.payload_len == 0:
            return False

        now = _time.ticks_ms()
        if _time.ticks_diff(now, self.last_rx_time) > consts.UART_TIMEOUT_MS:
            data_end = self.hdr_len + self.payload_len
            pkt_end = data_end + self.ftr_len
            self.buf[data_end:pkt_end] = self.ftr

            packet_view = memoryview(self.buf)[:pkt_end]

            mqtt_success = send_mqtt_cb(packet_view)

            # TODO: закомментировано — UART.flush() блокирует без приёмника на линии
            # if mqtt_success:
            #     send_uart_cb(consts.ACK_BYTE)
            # else:
            #     send_uart_cb(consts.NACK_BYTE)

            self.payload_len = 0
            return True

        return False


def main():
    sent_uart = []
    sent_mqtt = []

    framer = AckFramingBuffer(12345)

    def mqtt_ok(pkt):
        sent_mqtt.append(bytes(pkt))
        return True

    def uart_sink(data):
        sent_uart.append(data)

    # --- Тест 1: накопление чанков по 512 Б (маленький C-буфер) ---
    # 4 чанка по 512 = 2048 Б (ровно MAX_UART_PAYLOAD_LEN)
    _time._fake_ticks[0] = 0
    ok1 = framer.append_chunk(b'A' * 512)
    ok2 = framer.append_chunk(b'B' * 512)
    ok3 = framer.append_chunk(b'C' * 512)
    ok4 = framer.append_chunk(b'D' * 512)
    assert ok1 and ok2 and ok3 and ok4, 'Чанки должны приниматься'
    assert framer.payload_len == consts.MAX_UART_PAYLOAD_LEN, \
        f'payload_len = {framer.payload_len}, ожидался {consts.MAX_UART_PAYLOAD_LEN}'
    print('Тест 1 (накопление 4x512 Б): OK')
    print(f'  payload_len = {framer.payload_len}')

    # --- Тест 2: try_flush до истечения таймаута тишины ---
    _time._fake_ticks[0] = consts.UART_TIMEOUT_MS - 1  # ещё не тишина
    flushed = framer.try_flush(mqtt_ok, uart_sink)
    assert flushed is False, 'Не должен флашить до таймаута'
    assert sent_mqtt == [], 'MQTT не должен вызываться до таймаута'
    print('Тест 2 (try_flush до таймаута): OK')

    # --- Тест 3: try_flush после таймаута тишины -> публикация в MQTT ---
    _time._fake_ticks[0] = consts.UART_TIMEOUT_MS + 1  # тишина наступила
    flushed = framer.try_flush(mqtt_ok, uart_sink)
    assert flushed is True, 'Должен флашить после таймаута'
    assert len(sent_mqtt) == 1, 'Должен быть 1 MQTT payload'
    expected = b'{"dev":12345,"val":"' + b'A' * 512 + b'B' * 512 + b'C' * 512 + b'D' * 512 + b'"}'
    assert sent_mqtt[0] == expected, f'Неверный MQTT payload'
    assert framer.payload_len == 0, 'payload_len должен сброситься после flush'
    print('Тест 3 (try_flush после таймаута -> MQTT): OK')
    print(f'  frame size : {len(sent_mqtt[0])} B')

    # --- Тест 4: переполнение (Overrun Protection) -> сброс кадра ---
    sent_uart.clear()
    sent_mqtt.clear()
    _time._fake_ticks[0] = 0
    framer.append_chunk(b'X' * 100)
    ok = framer.append_chunk(b'Y' * (consts.MAX_UART_PAYLOAD_LEN - 99))  # 100 + 1949 = 2049 > 2048
    assert ok is False, 'Должен вернуть False при переполнении'
    assert framer.payload_len == 0, 'Кадр должен быть сброшен при переполнении'
    print('Тест 4 (переполнение -> сброс): OK')

    # --- Тест 5: сбой MQTT -> кадр всё равно сбрасывается ---
    sent_uart.clear()
    sent_mqtt.clear()
    _time._fake_ticks[0] = 0
    framer.append_chunk(b'HELLO')
    _time._fake_ticks[0] = consts.UART_TIMEOUT_MS + 1
    flushed = framer.try_flush(lambda pkt: False, uart_sink)
    assert flushed is True, 'Должен флашить'
    assert framer.payload_len == 0, 'payload_len должен сброситься после flush'
    print('Тест 5 (сбой MQTT -> сброс кадра): OK')

    # --- Тест 6: пустой буфер -> try_flush возвращает False ---
    flushed = framer.try_flush(mqtt_ok, uart_sink)
    assert flushed is False, 'Пустой буфер не должен флашить'
    print('Тест 6 (пустой буфер): OK')

    print()
    print('Все тесты AckFramingBuffer (потоковая схема) пройдены.')


if __name__ == '__main__':
    main()