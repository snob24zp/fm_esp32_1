import json
import logging
import os
import re
import signal
import ssl
import sys
import time
import uuid
from dataclasses import dataclass
from typing import List, Optional, Tuple

import paho.mqtt.client as mqtt


@dataclass
class EmulatorConfig:
    aws_iot_endpoint: str
    ca_file: str
    cert_file: str
    key_file: str
    mqtt_client_id: str
    mac: str
    serial: str

    @property
    def command_topic(self) -> str:
        return f">/{self.mac}/{self.serial}/3"

    @property
    def response_topic(self) -> str:
        return f"</{self.mac}/{self.serial}/3"

    @staticmethod
    def from_env() -> "EmulatorConfig":
        return EmulatorConfig(
            aws_iot_endpoint=os.getenv("AWS_IOT_ENDPOINT", "").strip(),
            ca_file=os.getenv("AWS_IOT_CA_FILE", "config/cert/AmazonRootCA1.pem").strip(),
            cert_file=os.getenv("AWS_IOT_CERT_FILE", "config/cert/certificate.pem.crt").strip(),
            key_file=os.getenv("AWS_IOT_KEY_FILE", "config/cert/private_pkcs8.pem").strip(),
            mqtt_client_id=os.getenv("MQTT_CLIENT_ID", "roboscine-sync-emulator").strip(),
            mac=os.getenv("DEVICE_MAC", "48:3f:da:55:07:5b").strip(),
            serial=os.getenv("DEVICE_SERIAL", "3996365522").strip(),
        )


def parse_command_string(raw_command: str) -> Tuple[str, Optional[str]]:
    """Parses commands in `<VERB:arg>` or `<GET FIRST FAll>` format."""
    cmd = raw_command.strip()
    if not (cmd.startswith("<") and cmd.endswith(">")):
        raise ValueError("Command must be wrapped in <>.")

    body = cmd[1:-1].strip()
    if ":" in body:
        verb, arg = body.split(":", 1)
        normalized_verb = re.sub(r"\s+", " ", verb).upper()
        return normalized_verb, arg

    normalized_verb = re.sub(r"\s+", " ", body).upper()
    return normalized_verb, None


class EmulatedDeviceFs:
    def __init__(self):
        self.directories = {"/", "/level1", "/level1/level2"}
        self.files = {}
        for index in range(1, 51):
            name = f"file_{index:02d}.txt"
            path = f"/level1/level2/{name}"
            self.files[path] = f"Text content from {name}."

        self.cwd = "/"
        self.open_file_path: Optional[str] = None
        self.open_file_buffer: List[str] = []

        self.read_chunks: List[str] = []
        self.read_index = 0

        self.list_entries: List[str] = []
        self.list_index = 0

    def _normalize_path(self, path: str) -> str:
        path = path.strip()
        if not path:
            return self.cwd

        if path.startswith("/"):
            candidate = path
        elif path == "..":
            if self.cwd == "/":
                return "/"
            parent = self.cwd.rsplit("/", 1)[0]
            return parent or "/"
        else:
            candidate = f"{self.cwd.rstrip('/')}/{path}" if self.cwd != "/" else f"/{path}"

        parts = [chunk for chunk in candidate.split("/") if chunk and chunk != "."]
        normalized = "/" + "/".join(parts)
        return normalized if normalized else "/"

    def _list_current_entries(self) -> List[str]:
        base = self.cwd.rstrip("/")
        prefix = f"{base}/" if base else "/"
        entries = {}

        for directory in sorted(self.directories):
            if directory == self.cwd:
                continue
            if not directory.startswith(prefix):
                continue
            rel = directory[len(prefix):]
            if "/" in rel or not rel:
                continue
            entries[rel] = f"{rel}|0|DIR"

        for file_path, text in sorted(self.files.items()):
            if not file_path.startswith(prefix):
                continue
            rel = file_path[len(prefix):]
            if "/" in rel or not rel:
                continue
            entries[rel] = f"{rel}|{len(text)}|FILE"

        return [entries[key] for key in sorted(entries)]

    @staticmethod
    def _split_chunks(text: str, chunk_size: int = 30) -> List[str]:
        chunks = [text[idx: idx + chunk_size] for idx in range(0, len(text), chunk_size)]
        return chunks or [""]

    def _read_next_chunk(self) -> str:
        if self.read_index >= len(self.read_chunks):
            return "<EOF>"
        chunk = self.read_chunks[self.read_index]
        self.read_index += 1
        return chunk

    def _list_next_block(self, block_size: int = 10) -> str:
        if self.list_index >= len(self.list_entries):
            return "<EOD>"

        block = self.list_entries[self.list_index: self.list_index + block_size]
        self.list_index += block_size
        result = ";".join(block)
        if self.list_index >= len(self.list_entries):
            result = f"{result};<EOD>"
        return result

    def handle(self, command_text: str) -> str:
        command, arg = parse_command_string(command_text)

        if command == "FCHDIR":
            target = self._normalize_path(arg or "/")
            if target in self.directories:
                self.cwd = target
                return "<ACK>"
            return "<NACK:1>"

        if command == "FMKDIR":
            target = self._normalize_path(arg or "")
            if target:
                self.directories.add(target)
            return "<ACK>"

        if command == "FOPEN":
            self.open_file_path = self._normalize_path(arg or "new_file.txt")
            self.open_file_buffer = []
            return "<ACK>"

        if command == "FWRITE":
            self.open_file_buffer.append(arg or "")
            return "<ACK>"

        if command == "FCLOSE":
            if self.open_file_path:
                self.files[self.open_file_path] = "".join(self.open_file_buffer) or "Written by emulator."
            self.open_file_path = None
            self.open_file_buffer = []
            return "<ACK>"

        if command == "FREAD":
            target = self._normalize_path(arg or "")
            return self.files.get(target, f"Text content from {os.path.basename(target) or 'file' }.")

        if command == "FREADFIRST":
            target = self._normalize_path(arg or "")
            text = self.files.get(target, f"Text content from {os.path.basename(target) or 'file' }.")
            self.read_chunks = self._split_chunks(text)
            self.read_index = 0
            return self._read_next_chunk()

        if command == "FREADNEXT":
            return self._read_next_chunk()

        if command == "FDEL":
            target = self._normalize_path(arg or "")
            self.files.pop(target, None)
            return "<ACK>"

        if command == "GET FIRST FALL":
            self.list_entries = self._list_current_entries()
            self.list_index = 0
            return self._list_next_block()

        if command == "GET NEXT FALL":
            return self._list_next_block()

        return "<NACK:3>"


class FileSyncDeviceEmulator:
    def __init__(self, config: EmulatorConfig):
        self.config = config
        self.fs = EmulatedDeviceFs()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._stop = False

        self.mqtt_client = mqtt.Client(client_id=self.config.mqtt_client_id)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_disconnect = self._on_disconnect

    def validate_config(self) -> None:
        required = {
            "AWS_IOT_ENDPOINT": self.config.aws_iot_endpoint,
            "AWS_IOT_CA_FILE": self.config.ca_file,
            "AWS_IOT_CERT_FILE": self.config.cert_file,
            "AWS_IOT_KEY_FILE": self.config.key_file,
            "DEVICE_MAC": self.config.mac,
            "DEVICE_SERIAL": self.config.serial,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required settings: {', '.join(missing)}")

        for path in (self.config.ca_file, self.config.cert_file, self.config.key_file):
            if not os.path.exists(path):
                raise FileNotFoundError(f"TLS file not found: {path}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            self.logger.error("MQTT connect failed, rc=%s", rc)
            return

        self.logger.info("Connected to AWS IoT MQTT. Subscribing to %s", self.config.command_topic)
        client.subscribe(self.config.command_topic, qos=1)

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0 and not self._stop:
            self.logger.warning("Unexpected MQTT disconnect, rc=%s", rc)

    def _on_message(self, client, userdata, msg):
        payload_text = msg.payload.decode("utf-8", errors="replace").strip()
        self.logger.info("Incoming command: topic=%s payload=%s", msg.topic, payload_text)

        try:
            envelope = json.loads(payload_text)
            command_text = envelope.get("command", "")
            request_id = envelope.get("id") or str(uuid.uuid4())
            result = self.fs.handle(command_text)

            response = {"result": result, "id": request_id}
            client.publish(
                self.config.response_topic,
                payload=json.dumps(response),
                qos=1,
                retain=False,
            )
            self.logger.info("Published response: topic=%s payload=%s", self.config.response_topic, response)
        except Exception as exc:
            self.logger.exception("Failed to process command payload=%s: %s", payload_text, exc)

    def start(self) -> None:
        self.validate_config()

        self.mqtt_client.tls_set(
            ca_certs=self.config.ca_file,
            certfile=self.config.cert_file,
            keyfile=self.config.key_file,
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
        )

        self.logger.info("Connecting to AWS IoT endpoint %s:8883", self.config.aws_iot_endpoint)
        self.mqtt_client.connect(self.config.aws_iot_endpoint, 8883, keepalive=60)
        self.mqtt_client.loop_start()

        self.logger.info("Device emulator is running. Press Ctrl+C to stop.")
        while not self._stop:
            time.sleep(0.5)

    def stop(self) -> None:
        self._stop = True
        try:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        except Exception:
            pass


def main() -> int:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    config = EmulatorConfig.from_env()
    emulator = FileSyncDeviceEmulator(config)

    def _handle_signal(signum, frame):
        logging.getLogger("main").info("Received signal %s, stopping emulator...", signum)
        emulator.stop()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        emulator.start()
        return 0
    except Exception as exc:
        logging.getLogger("main").exception("Emulator crashed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())

