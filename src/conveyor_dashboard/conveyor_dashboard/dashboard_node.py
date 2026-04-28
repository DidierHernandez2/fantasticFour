#!/usr/bin/env python3

import json
import threading
import time
import asyncio

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn


app = FastAPI()

ros_node = None
latest_telemetry = {}
latest_frame = None


class DashboardBridge(Node):
    def __init__(self):
        super().__init__("dashboard_bridge")

        self.cmd_pub = self.create_publisher(String, "/conveyor/cmd", 10)

        self.telemetry_sub = self.create_subscription(
            String,
            "/conveyor/telemetry",
            self.telemetry_callback,
            10,
        )

        self.image_sub = self.create_subscription(
            CompressedImage,
            "/camera/image/compressed",
            self.image_callback,
            10,
        )

    def telemetry_callback(self, msg):
        global latest_telemetry
        try:
            latest_telemetry = json.loads(msg.data)
        except json.JSONDecodeError:
            pass

    def image_callback(self, msg):
        global latest_frame
        latest_frame = bytes(msg.data)

    def send_cmd(self, data):
        msg = String()
        msg.data = json.dumps(data)
        self.cmd_pub.publish(msg)


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Banda L510</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111827;
            color: white;
            margin: 0;
            padding: 20px;
        }

        h1 {
            margin-bottom: 20px;
        }

        .grid {
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 20px;
        }

        .card {
            background: #1f2937;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
        }

        button {
            font-size: 18px;
            padding: 12px 18px;
            margin: 6px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
        }

        .run { background: #22c55e; color: black; }
        .rev { background: #f59e0b; color: black; }
        .stop { background: #ef4444; color: white; }
        .emg { background: #991b1b; color: white; font-weight: bold; }

        input {
            width: 100%;
        }

        img {
            width: 100%;
            border-radius: 12px;
            background: black;
        }

        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
        }

        .metric {
            background: #111827;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #374151;
        }

        .label {
            color: #9ca3af;
            font-size: 14px;
            margin-bottom: 6px;
        }

        .value {
            font-size: 24px;
            font-weight: bold;
        }

        .description {
            margin-top: 6px;
            color: #d1d5db;
            font-size: 14px;
        }

        .ok { color: #22c55e; }
        .warn { color: #facc15; }
        .bad { color: #ef4444; }
        .info { color: #38bdf8; }

        .status-banner {
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 18px;
            font-size: 22px;
            font-weight: bold;
            text-align: center;
        }

        .banner-stop {
            background: #374151;
            color: white;
        }

        .banner-run {
            background: #064e3b;
            color: #86efac;
        }

        .banner-error {
            background: #7f1d1d;
            color: #fecaca;
        }
    </style>
</head>

<body>
    <h1>Dashboard de Supervisión - Banda L510</h1>

    <div id="mainStatus" class="status-banner banner-stop">
        Esperando datos del sistema...
    </div>

    <div class="grid">
        <div class="card">
            <h2>Video de cámara</h2>
            <img src="/video">
        </div>

        <div class="card">
            <h2>Control de banda</h2>

            <button class="run" onclick="cmd('forward')">Avanzar</button>
            <button class="rev" onclick="cmd('reverse')">Reversa</button>
            <button class="stop" onclick="cmd('stop')">Detener</button>
            <button class="emg" onclick="cmd('emergency_stop')">Paro de emergencia</button>

            <h3>Velocidad solicitada: <span id="speedLabel">10</span> Hz</h3>
            <input type="range" min="0" max="60" value="10" step="1"
                   oninput="setSpeed(this.value)">
        </div>
    </div>

    <div class="card" style="margin-top:20px;">
        <h2>Telemetría interpretada</h2>

        <div class="telemetry-grid">
            <div class="metric">
                <div class="label">Estado general</div>
                <div class="value" id="stateText">---</div>
                <div class="description" id="stateDesc">Sin datos todavía.</div>
            </div>

            <div class="metric">
                <div class="label">Condición del variador</div>
                <div class="value" id="errorText">---</div>
                <div class="description" id="errorDesc">Sin datos todavía.</div>
            </div>

            <div class="metric">
                <div class="label">Velocidad solicitada</div>
                <div class="value info" id="freqCmd">---</div>
                <div class="description" id="freqCmdDesc">Referencia enviada al variador.</div>
            </div>

            <div class="metric">
                <div class="label">Velocidad real de salida</div>
                <div class="value info" id="freqOut">---</div>
                <div class="description" id="freqOutDesc">Velocidad que realmente está entregando el variador.</div>
            </div>

            <div class="metric">
                <div class="label">Carga aproximada del motor</div>
                <div class="value" id="currentText">---</div>
                <div class="description" id="currentDesc">Corriente de salida interpretada.</div>
            </div>

            <div class="metric">
                <div class="label">Resumen para operador</div>
                <div class="value" id="operatorText">---</div>
                <div class="description" id="operatorDesc">Mensaje simple de operación.</div>
            </div>
        </div>
    </div>

<script>
    const ws = new WebSocket(`ws://${location.host}/ws`);

    function interpretState(state) {
        if (state === null || state === undefined) {
            return {
                text: "Sin datos",
                desc: "No se está recibiendo información del variador.",
                cls: "warn",
                banner: "Esperando datos del sistema...",
                bannerClass: "banner-stop"
            };
        }

        if (state === 4) {
            return {
                text: "Detenida",
                desc: "La banda está lista, pero no está corriendo.",
                cls: "warn",
                banner: "Banda detenida",
                bannerClass: "banner-stop"
            };
        }

        if (state === 5) {
            return {
                text: "Avanzando",
                desc: "La banda está corriendo en dirección normal.",
                cls: "ok",
                banner: "Banda avanzando",
                bannerClass: "banner-run"
            };
        }

        if (state === 7) {
            return {
                text: "Corriendo",
                desc: "La banda está en movimiento. Puede estar en reversa o en modo activo de operación.",
                cls: "ok",
                banner: "Banda en movimiento",
                bannerClass: "banner-run"
            };
        }

        return {
            text: `Estado ${state}`,
            desc: "Estado recibido del variador. Requiere interpretación específica.",
            cls: "info",
            banner: `Estado del sistema: ${state}`,
            bannerClass: "banner-stop"
        };
    }

    function interpretError(error) {
        if (error === null || error === undefined) {
            return {
                text: "Sin datos",
                desc: "No se pudo leer el estado de error.",
                cls: "warn"
            };
        }

        if (error === 0) {
            return {
                text: "Normal",
                desc: "No hay errores activos en el variador.",
                cls: "ok"
            };
        }

        if (error === 26) {
            return {
                text: "Detenido a 0 Hz",
                desc: "El variador está detenido porque la referencia de velocidad es cero.",
                cls: "warn"
            };
        }

        return {
            text: `Código ${error}`,
            desc: "El variador reporta un código de error/estado. Revisar manual si persiste.",
            cls: "bad"
        };
    }

    function interpretCurrent(currentRaw) {
        if (currentRaw === null || currentRaw === undefined) {
            return {
                text: "Sin lectura",
                desc: "No se pudo leer la corriente del motor.",
                cls: "warn"
            };
        }

        const ampsApprox = currentRaw / 10.0;

        if (currentRaw === 0) {
            return {
                text: "Sin carga",
                desc: "El motor no está consumiendo corriente significativa.",
                cls: "warn"
            };
        }

        if (currentRaw <= 8) {
            return {
                text: `${ampsApprox.toFixed(1)} A aprox.`,
                desc: "Carga baja. Operación normal para pruebas ligeras.",
                cls: "ok"
            };
        }

        if (currentRaw <= 15) {
            return {
                text: `${ampsApprox.toFixed(1)} A aprox.`,
                desc: "Carga media. El motor está trabajando, pero sigue en rango razonable.",
                cls: "warn"
            };
        }

        return {
            text: `${ampsApprox.toFixed(1)} A aprox.`,
            desc: "Carga alta. Revisar si la banda está atorada o forzada.",
            cls: "bad"
        };
    }

    function operatorSummary(data) {
        const state = data.state;
        const error = data.error;
        const fout = data.freq_out_hz ?? 0;
        const current = data.current_raw ?? 0;

        if (error !== null && error !== undefined && error !== 0 && error !== 26) {
            return {
                text: "Revisar sistema",
                desc: "Hay un código de error activo. Se recomienda detener y revisar.",
                cls: "bad"
            };
        }

        if (state === 4 || fout === 0) {
            return {
                text: "Lista para operar",
                desc: "La banda está detenida y lista para recibir una orden.",
                cls: "warn"
            };
        }

        if ((state === 5 || state === 7) && current <= 8) {
            return {
                text: "Operación normal",
                desc: "La banda se mueve correctamente y la carga es baja.",
                cls: "ok"
            };
        }

        if ((state === 5 || state === 7) && current > 8) {
            return {
                text: "Operando con carga",
                desc: "La banda está en movimiento y el motor presenta carga.",
                cls: "warn"
            };
        }

        return {
            text: "Estado no identificado",
            desc: "El sistema está reportando valores poco comunes.",
            cls: "info"
        };
    }

    function setClass(element, cls) {
        element.className = "value " + cls;
    }

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        const stateInfo = interpretState(data.state);
        const errorInfo = interpretError(data.error);
        const currentInfo = interpretCurrent(data.current_raw);
        const opInfo = operatorSummary(data);

        const banner = document.getElementById("mainStatus");
        banner.innerText = stateInfo.banner;
        banner.className = "status-banner " + stateInfo.bannerClass;

        const stateText = document.getElementById("stateText");
        stateText.innerText = stateInfo.text;
        setClass(stateText, stateInfo.cls);
        document.getElementById("stateDesc").innerText = stateInfo.desc;

        const errorText = document.getElementById("errorText");
        errorText.innerText = errorInfo.text;
        setClass(errorText, errorInfo.cls);
        document.getElementById("errorDesc").innerText = errorInfo.desc;

        document.getElementById("freqCmd").innerText =
            data.freq_cmd_hz !== null && data.freq_cmd_hz !== undefined
                ? `${data.freq_cmd_hz.toFixed(2)} Hz`
                : "---";

        document.getElementById("freqOut").innerText =
            data.freq_out_hz !== null && data.freq_out_hz !== undefined
                ? `${data.freq_out_hz.toFixed(2)} Hz`
                : "---";

        const currentText = document.getElementById("currentText");
        currentText.innerText = currentInfo.text;
        setClass(currentText, currentInfo.cls);
        document.getElementById("currentDesc").innerText = currentInfo.desc;

        const operatorText = document.getElementById("operatorText");
        operatorText.innerText = opInfo.text;
        setClass(operatorText, opInfo.cls);
        document.getElementById("operatorDesc").innerText = opInfo.desc;
    };

    function cmd(action) {
        fetch("/cmd", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({action})
        });
    }

    function setSpeed(hz) {
        document.getElementById("speedLabel").innerText = hz;

        fetch("/cmd", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({action: "set_speed", hz: parseFloat(hz)})
        });
    }
</script>
</body>
</html>
"""


@app.get("/")
def index():
    return HTMLResponse(HTML)


@app.post("/cmd")
async def send_command(data: dict):
    if ros_node is not None:
        ros_node.send_cmd(data)
    return {"ok": True, "sent": data}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_text(json.dumps(latest_telemetry))
        await asyncio.sleep(0.3)


def mjpeg_generator():
    global latest_frame

    while True:
        if latest_frame is not None:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                latest_frame +
                b"\r\n"
            )
        time.sleep(0.05)


@app.get("/video")
def video():
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


def ros_spin():
    global ros_node

    rclpy.init()
    ros_node = DashboardBridge()
    rclpy.spin(ros_node)


def main():
    thread = threading.Thread(target=ros_spin, daemon=True)
    thread.start()
    time.sleep(1.0)

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()