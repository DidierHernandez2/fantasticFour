#!/usr/bin/env python3

import json
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from pymodbus.client import ModbusSerialClient


REG_OP_SIGNAL = 9473
REG_FREQ_CMD = 9474

REG_STATE = 9504
REG_ERR = 9505
REG_FREQ_RD = 9507
REG_FREQ_OUT = 9508
REG_CURRENT = 9511

MIN_HZ = 0.0
MAX_HZ = 60.0


class L510Controller:
    def __init__(self, port: str, device_id: int, baudrate: int = 9600):
        self.device_id = device_id
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity="N",
            stopbits=1,
            bytesize=8,
            timeout=1.0,
        )
        self.last_freq_hz = 10.0

    def connect(self) -> bool:
        return self.client.connect()

    def close(self):
        self.client.close()

    def read1(self, addr: int):
        rr = self.client.read_holding_registers(addr, 1, slave=self.device_id)
        if rr.isError():
            return None
        return rr.registers[0]

    def write1(self, addr: int, value: int) -> bool:
        wr = self.client.write_register(addr, value, slave=self.device_id)
        return not wr.isError()

    def hz_to_word(self, hz: float) -> int:
        hz = max(MIN_HZ, min(MAX_HZ, hz))
        return int(round(hz * 100))

    def word_to_hz(self, word):
        if word is None:
            return None
        return word / 100.0

    def set_frequency(self, hz: float) -> bool:
        hz = max(MIN_HZ, min(MAX_HZ, hz))
        ok = self.write1(REG_FREQ_CMD, self.hz_to_word(hz))
        if ok:
            self.last_freq_hz = hz
        return ok

    def run_forward(self) -> bool:
        return self.write1(REG_OP_SIGNAL, 1)

    def run_reverse(self) -> bool:
        return self.write1(REG_OP_SIGNAL, 3)

    def stop(self) -> bool:
        return self.write1(REG_OP_SIGNAL, 0)

    def get_status(self) -> dict:
        state = self.read1(REG_STATE)
        err = self.read1(REG_ERR)
        fcmd = self.read1(REG_FREQ_RD)
        fout = self.read1(REG_FREQ_OUT)
        curr = self.read1(REG_CURRENT)

        return {
            "state": state,
            "error": err,
            "freq_cmd_hz": self.word_to_hz(fcmd),
            "freq_out_hz": self.word_to_hz(fout),
            "current_raw": curr,
            "timestamp": time.time(),
        }


class L510Node(Node):
    def __init__(self):
        super().__init__("l510_node")

        self.declare_parameter("port", "/dev/ttyUSB0")
        self.declare_parameter("slave", 1)
        self.declare_parameter("baudrate", 9600)
        self.declare_parameter("initial_speed", 10.0)

        port = self.get_parameter("port").value
        slave = int(self.get_parameter("slave").value)
        baudrate = int(self.get_parameter("baudrate").value)
        self.initial_speed = float(self.get_parameter("initial_speed").value)

        self.ctrl = L510Controller(
            port=port,
            device_id=slave,
            baudrate=baudrate,
        )

        if not self.ctrl.connect():
            self.get_logger().error(f"No conecta al L510 en {port}")
            raise RuntimeError(f"No conecta al L510 en {port}")

        self.get_logger().info(f"Conectado al L510 en {port}, slave/device_id={slave}")

        self.telemetry_pub = self.create_publisher(
            String,
            "/conveyor/telemetry",
            10,
        )

        self.cmd_sub = self.create_subscription(
            String,
            "/conveyor/cmd",
            self.cmd_callback,
            10,
        )

        self.initialize_drive()

        self.status_timer = self.create_timer(0.5, self.publish_telemetry)

    def initialize_drive(self):
        hz = max(MIN_HZ, min(MAX_HZ, self.initial_speed))

        self.get_logger().info(f"Inicializando banda: STOP + {hz:.2f} Hz")

        ok_stop = self.ctrl.stop()
        time.sleep(0.5)

        ok_freq = self.ctrl.set_frequency(hz)
        time.sleep(0.2)

        self.get_logger().info(
            f"STOP inicial -> {ok_stop}, velocidad inicial {hz:.2f} Hz -> {ok_freq}"
        )

    def publish_telemetry(self):
        try:
            data = self.ctrl.get_status()
        except Exception as e:
            self.get_logger().warn(f"No se pudo leer telemetría: {e}")
            data = {
                "state": None,
                "error": None,
                "freq_cmd_hz": None,
                "freq_out_hz": None,
                "current_raw": None,
                "timestamp": time.time(),
            }

        msg = String()
        msg.data = json.dumps(data)
        self.telemetry_pub.publish(msg)

    def cmd_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().error("Comando JSON inválido")
            return

        action = data.get("action")

        if action == "set_speed":
            try:
                hz = float(data.get("hz", 0.0))
            except (TypeError, ValueError):
                self.get_logger().error("Velocidad inválida")
                return

            hz = max(MIN_HZ, min(MAX_HZ, hz))

            if self.ctrl.set_frequency(hz):
                self.get_logger().info(f"Frecuencia -> {hz:.2f} Hz")
            else:
                self.get_logger().error("Falló escritura de frecuencia")

            time.sleep(0.2)
            self.publish_telemetry()
            return

        if action == "forward":
            if self.ctrl.run_forward():
                self.get_logger().info("RUN forward enviado")
            else:
                self.get_logger().error("Falló RUN forward")

            time.sleep(0.3)
            self.publish_telemetry()
            return

        if action == "reverse":
            if self.ctrl.run_reverse():
                self.get_logger().info("RUN reverse enviado")
            else:
                self.get_logger().error("Falló RUN reverse")

            time.sleep(0.3)
            self.publish_telemetry()
            return

        if action == "stop":
            if self.ctrl.stop():
                self.get_logger().info("STOP enviado")
            else:
                self.get_logger().error("Falló STOP")

            time.sleep(0.3)
            self.publish_telemetry()
            return

        if action == "emergency_stop":
            if self.ctrl.stop():
                self.get_logger().warn("EMERGENCY STOP enviado")
            else:
                self.get_logger().error("Falló EMERGENCY STOP")

            time.sleep(0.3)
            self.publish_telemetry()
            return

        self.get_logger().warn(f"Acción desconocida: {action}")

    def destroy_node(self):
        try:
            self.get_logger().info("Cerrando nodo: enviando STOP")
            self.ctrl.stop()
            time.sleep(0.2)
        except Exception:
            pass

        try:
            self.ctrl.close()
        except Exception:
            pass

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = L510Node()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()