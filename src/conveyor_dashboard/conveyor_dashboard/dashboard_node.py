import json
import threading
import time

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
            print("TELEMETRIA:", latest_telemetry)
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
            font-family: Arial;
            background: #111827;
            color: white;
            margin: 0;
            padding: 20px;
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
        }
        button {
            font-size: 18px;
            padding: 12px 18px;
            margin: 6px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
        }
        .run { background: #22c55e; }
        .rev { background: #f59e0b; }
        .stop { background: #ef4444; color: white; }
        .emg { background: #b91c1c; color: white; font-weight: bold; }
        input {
            width: 100%;
        }
        img {
            width: 100%;
            border-radius: 12px;
            background: black;
        }
        .value {
            font-size: 28px;
            font-weight: bold;
            color: #38bdf8;
        }
    </style>
</head>
<body>
    <h1>Dashboard de Supervisión - Banda L510</h1>

    <div class="grid">
        <div class="card">
            <h2>Video</h2>
            <img src="/video">
        </div>

        <div class="card">
            <h2>Control</h2>

            <button class="run" onclick="cmd('forward')">RUN Forward</button>
            <button class="rev" onclick="cmd('reverse')">RUN Reverse</button>
            <button class="stop" onclick="cmd('stop')">STOP</button>
            <button class="emg" onclick="cmd('emergency_stop')">EMERGENCY STOP</button>

            <h3>Velocidad: <span id="speedLabel">10</span> Hz</h3>
            <input type="range" min="0" max="60" value="10" step="1"
                   oninput="setSpeed(this.value)">
        </div>
    </div>

    <div class="card" style="margin-top:20px;">
        <h2>Telemetría</h2>
        <p>Estado: <span class="value" id="state">---</span></p>
        <p>Error: <span class="value" id="error">---</span></p>
        <p>Frecuencia referencia: <span class="value" id="freqCmd">---</span> Hz</p>
        <p>Frecuencia salida: <span class="value" id="freqOut">---</span> Hz</p>
        <p>Corriente: <span class="value" id="current">---</span></p>
    </div>

<script>
    const ws = new WebSocket(`ws://${location.host}/ws`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        document.getElementById("state").innerText = data.state ?? "---";
        document.getElementById("error").innerText = data.error ?? "---";
        document.getElementById("freqCmd").innerText = data.freq_cmd_hz ?? "---";
        document.getElementById("freqOut").innerText = data.freq_out_hz ?? "---";
        document.getElementById("current").innerText = data.current_raw ?? "---";
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
        await asyncio_sleep(0.3)


async def asyncio_sleep(seconds):
    import asyncio
    await asyncio.sleep(seconds)


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
    global ros_node

    rclpy.init()
    ros_node = DashboardBridge()

    thread = threading.Thread(target=rclpy.spin, args=(ros_node,), daemon=True)
    thread.start()

    time.sleep(1.0)

    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()