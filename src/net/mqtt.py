import socket
import struct
import select

try:
    from time import ticks_ms, time
except ImportError:
    from time import time

    def ticks_ms():
        return time() * 1000

class MQTTException(Exception):
    pass


class MQTTClient:
    def __init__(
        self,
        client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=False,
        ssl_params={},
    ):
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.pid = 0
        self.cb = None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False
        self._keepalive_tmr = time()

    def _send_str(self, s:str):
        self.sock.send(struct.pack("!H", len(s)))
        self.sock.send(s.encode())

    @staticmethod
    def _recv_len(d: bytes):
        sh = 0
        n = 0
        while True:
            n |= (d[0] & 0x7F) << sh
            if not d[0] & 0x80:
                break
            sh += 7
            d = d[1:]
        return n, d[1:]

    def set_callback(self, f):
        self.cb = f

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session=True):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)
        if self.ssl:
            import ssl
            self.sock = ssl.wrap_socket(self.sock, **self.ssl_params)
        premsg = bytearray([0x10,0x00,0x00,0x00,0x00])
        msg = bytearray(b"\x04MQTT\x04\x02\0\0")

        sz = 10 + 2 + len(self.client_id)
        msg[6] = clean_session << 1
        if self.user is not None:
            sz += 2 + len(self.user) + 2 + len(self.pswd)
            msg[6] |= 0xC0
        if self.keepalive:
            assert self.keepalive < 65536
            msg[7] |= self.keepalive >> 8
            msg[8] |= self.keepalive & 0x00FF
        if self.lw_topic:
            sz += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)
            msg[6] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[6] |= self.lw_retain << 5

        i = 1
        while sz > 0x7F:
            premsg[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        premsg[i] = sz
        premsg = premsg[:i + 2]
        premsg.extend(msg)
        self.sock.send(premsg)

        # print(hex(len(msg)), hexlify(msg, ":"))
        self._send_str(self.client_id)
        if self.lw_topic:
            self._send_str(self.lw_topic)
            self._send_str(self.lw_msg)
        if self.user is not None:
            self._send_str(self.user)
            self._send_str(self.pswd)
        resp = self.sock.recv(4)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            raise MQTTException(resp[3])

        self._keepalive_tmr = time()
        return resp[2] & 1

    def disconnect(self):
        self.sock.send(b"\xe0\0")
        self.sock.close()

    def ping(self):
        self._keepalive_tmr = time()
        self.sock.send(b"\xc0\0")

    def publish(self, topic, msg, retain=False, qos=0):
        pkt = bytearray(b"\x30\0\0\0")
        if isinstance(msg, str):
            msg = msg.encode()

        pkt[0] |= qos << 1 | retain
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        assert sz < 2097152
        i = 1
        while sz > 0x7F:
            pkt[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz
        pkt = pkt[:i + 1]
        self.sock.send(pkt)
        self._send_str(topic)
        if qos > 0:
            self.pid += 1
            pid = self.pid
            struct.pack_into("!H", pkt, 0, pid)
            self.sock.send(pkt[:2])
        self.sock.send(msg)
        self._keepalive_tmr = time()

    def subscribe(self, topic, qos=0):
        assert self.cb is not None, "Subscribe callback is not set"
        pkt = bytearray(b"\x82\0\0\0")
        self.pid += 1
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic) + 1, self.pid)
        # print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.send(pkt)
        self._send_str(topic)
        self.sock.send(qos.to_bytes(1, "little"))

    # Wait for a single incoming MQTT message and process it.
    # Subscribed messages are delivered to a callback previously
    # set by .set_callback() method. Other (internal) MQTT
    # messages processed internally.
    def wait_msg(self):
        if self.keepalive:
            diff = time() - self._keepalive_tmr
            backoff = self.keepalive - (self.keepalive * 0.1)
            if diff > backoff:
                self.ping()

        sock, _, _ = select.select((self.sock,),(),(), 0.01)
        if sock:
            sock = sock[0]
            res = True
            while res:
                try:
                    sock.setblocking(False)
                    res = sock.recv(1536)

                except OSError as ex:
                    if ex.errno == 11: # blocking issue on cpython
                        res = None
                    else:
                        raise ex
                finally:
                    sock.setblocking(True)

                if res is None:
                    return

                if res == b"":
                    raise OSError(-1)

                if len(res) < 2:
                    continue

                op = res[0]
                if op & 0xF0 != 0x30:
                    if op == 0xd0:  # PINGRESP
                        sz = res[1]
                        assert sz == 0
                        res = res[2:]

                    elif op == 0x40: # PUBACK
                        sz = res[1]
                        assert sz == b"\x02"
                        res = res[4:]

                    elif op == 0x90: # SUBACK
                        if res[4] == 0x80:
                            raise MQTTException(res[4])
                        res = res[5:]
                        self._keepalive_tmr = time()
                    else:
                        print(f'-- unknown OP: 0x{op:x}')
                    continue

                sz, res = self._recv_len(res[1:])
                topic_len = (res[0] << 8) | res[1]
                topic = res[2:topic_len + 2]
                res = res[topic_len + 2:]

                sz -= topic_len + 2
                if op & 6:
                    pid = res[0] << 8 | res[1]
                    res = res[2:]
                    sz -= 2

                msg = res[:sz]
                self.cb(topic, msg)
                res = res[sz:]
                if op & 6 == 2:
                    pkt = bytearray(b"\x40\x02\0\0")
                    struct.pack_into("!H", pkt, 2, pid)
                    sock.send(pkt)
                elif op & 6 == 4:
                    assert 0

            #self.sock.setblocking(True)


    def check_msg(self):
        # self.sock.setblocking(False)
        return self.wait_msg()

# import net.mqtt as mqtt; mqtt.test()

def test():
    def on_msg(t, m):
        print(t, m)

    mq = MQTTClient('mqtt-client-id', server='x.ks.ua', port=1883, keepalive=60)
    mq.set_callback(on_msg)
    mq.connect()
    mq.subscribe('/topic/test-sub')
    tm = ticks_ms()
    idx = 0
    while True:
        if ticks_ms() > (tm + 1000):
            print(f'{idx}; /topic/test-pub => ampy -p /dev/ttyACM0 put src/uclient/mqtt_transport.py uclient/mqtt_transport.py')
            mq.publish('/topic/test-pub', b'ampy -p /dev/ttyACM0 put src/uclient/mqtt_transport.py uclient/mqtt_transport.py')
            tm = ticks_ms()
            idx += 1

        mq.check_msg()


if __name__ == "__main__":
    test()
