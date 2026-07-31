import gc

from net.umqtt_simple import MQTTClient, MQTTException


# AWS IoT Core MQTT endpoint. Port 8883 is MQTT over TLS, not HTTPS.
HOST = "a3bb1kruav9c9p-ats.iot.eu-central-1.amazonaws.com"
PORT = 8883

# Keep the ID unique among simultaneously connected devices.
CLIENT_ID = "esp32-c3-mpy-test"

# Topic used by the working ESP32 C++ implementation.
TOPIC = "</17:91:a8:06:f4:fc/4243850920/TestConnectESP32"


def test():
    """Connect to AWS IoT and verify an MQTT QoS 1 publish."""
    print("=== AWS MQTT TEST ===")
    gc.collect()
    print("FREE BEFORE MQTT =", gc.mem_free())

    client = None
    try:
        print("Loading certificates...")
        # The ECC credential pair needs far less heap than RSA-2048 during
        # the mutual TLS handshake on this MicroPython build.
        with open("certs/ecc-crt.der", "rb") as f:
            cert = f.read()
        with open("certs/ecc-key.der", "rb") as f:
            key = f.read()
        with open("certs/root_ca.der", "rb") as f:
            ca = f.read()

        client = MQTTClient(
            CLIENT_ID,
            HOST,
            port=PORT,
            keepalive=60,
            ssl=True,
            ssl_params={
                "key": key,
                "cert": cert,
                "cadata": ca,
                "server_hostname": HOST,
            },
        )

        print("MQTT CONNECT...")
        session_present = client.connect()
        print("CONNACK OK; session_present =", session_present)

        payload = b'{"status":"working","device":"ESP32C3"}'
        print("MQTT PUBLISH QoS=1...")
        client.publish(TOPIC, payload, qos=1)
        print("PUBACK OK; message accepted by AWS IoT")

    except MQTTException as e:
        print("MQTT ERROR:", repr(e))
    except OSError as e:
        print("NETWORK/TLS ERROR:", repr(e))
    except Exception as e:
        print("ERROR:", repr(e))
    finally:
        if client is not None:
            try:
                client.disconnect()
                print("MQTT DISCONNECTED")
            except Exception:
                pass
