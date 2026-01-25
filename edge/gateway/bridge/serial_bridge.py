import logging
import threading
import time
from typing import Optional, Tuple

import serial


class ArduinoSerialBridge:
    def __init__(self, port: str, baud_rate: int = 115200):
        self.logger = logging.getLogger("ArduinoBridge")
        self.serial: Optional[serial.Serial] = None
        self.port = port
        self.baud_rate = baud_rate
        self._serial_lock = threading.Lock()

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1.0)
            time.sleep(2)
            self.serial.reset_input_buffer()

            with self._serial_lock:
                self.serial.reset_input_buffer()

            self.logger.info(f"✅ Arduino connected on {self.port}")
        except serial.SerialException as e:
            self.logger.error(f"❌ Failed to connect to Arduino: {e}")

    def disconnect(self):
        with self._serial_lock:
            if self.serial and self.serial.is_open:
                self.serial.close()
                self.logger.info("Arduino disconnected.")

    def _send_and_receive(self, command: str, expected_tag: str) -> Optional[str]:

        if not self.serial or not self.serial.is_open:
            return None

        with self._serial_lock:
            try:
                self.serial.reset_input_buffer()
                self.serial.write(f"{command}\n".encode("utf-8"))

                line = self.serial.readline().decode("utf-8").strip()

                if line.startswith(expected_tag):
                    return line.replace(expected_tag, "")
                else:
                    if line:
                        self.logger.warning(
                            f"Unexpected response for {command}: '{line}'"
                        )
                    return None

            except Exception as e:
                self.logger.error(f"Serial Error during {command}: {e}")
                return None

    def get_distance(self) -> float:
        response = self._send_and_receive("GET:DIST", "DIST:")

        if response:
            try:
                return float(response)
            except ValueError:
                self.logger.error(f"Errore parsing distanza: {response}")
        return 0.0

    def get_power_data(self) -> Tuple[float, float, float]:
        response = self._send_and_receive("GET:PWR", "PWR:")

        if response:
            try:
                parts = response.split(":")
                if len(parts) >= 3:
                    voltage = float(parts[0])
                    current = float(parts[1])
                    power = float(parts[2])
                    return voltage, current, power
            except ValueError:
                self.logger.error(f"Errore parsing power data: {response}")

        return 0.0, 0.0, 0.0

    def set_l298(self, pwm: int, status: str) -> bool:
        if not self.serial or not self.serial.is_open:
            self.logger.warning("Impossibile settare attuatore: Bridge disconnesso")
            return False

        cmd = f"SET:L298:{int(pwm)}:{status}"

        with self._serial_lock:
            try:
                self.serial.write(f"{cmd}\n".encode("utf-8"))
                self.logger.debug(f"Inviato comando attuatore: {cmd}")
                return True
            except Exception as e:
                self.logger.error(f"Errore invio comando attuatore: {e}")
                return False
