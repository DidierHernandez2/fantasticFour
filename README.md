# Sistema Robótico ROS2 con Banda Transportadora, Robotino y Simulación

<div align="center">
  <img width="331" height="496" src="https://github.com/user-attachments/assets/935a6e47-0d9a-458d-832b-6bb80e144825" />
</div>

---

## Descripción

Sistema modular basado en ROS2 que integra:

- Banda transportadora (TECO L510 vía Modbus)
- Dashboard web
- Interfaz táctil
- Joystick
- Simulación Webots
- Robotino
- Visión y audio

---

## Instalación

### 1. Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

---

### 2. Entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

---

### 3. Dependencias (IMPORTANTE)

```bash
pip install -r requirements.txt
```

---

### 4. Compilar

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

---

## ROS2 RUN (nodos disponibles)

### conveyor_dashboard

```bash
ros2 run conveyor_dashboard l510_node
```
Controla el variador L510.

```bash
ros2 run conveyor_dashboard webcam_node
```
Publica cámara.

```bash
ros2 run conveyor_dashboard dashboard_node
```
Levanta dashboard web.

---

### l510_controller

```bash
ros2 run l510_controller l510_node
```
Control directo del variador.

```bash
ros2 run l510_controller l510_topic_node
```
Control por tópicos.

---

### touch_hmi

```bash
ros2 run touch_hmi touch_hmi_node
```
Interfaz táctil.

---

### joy_mapper

```bash
ros2 run joy_mapper joy_mapper_node
```
Traduce joystick a comandos.

---

### vision

```bash
ros2 run vision vision_node
```
Nodo principal de visión.

```bash
ros2 run vision yolo_person_node
```
Detección de personas.

---

### robotino_audio

```bash
ros2 run robotino_audio vosk_node
```
Reconocimiento de voz.

---

### robotino_tts

```bash
ros2 run robotino_tts espeak_tts_node
```
Síntesis de voz.

---

### robotino_bts

```bash
ros2 run robotino_bts task_manager
```
Árboles de comportamiento.

---

## ROS2 LAUNCH (sistemas completos)

### Banda real

```bash
ros2 launch conveyor_dashboard dashboard.launch.py
```
Inicia:
- Control L510
- Cámara
- Dashboard web

---

### Banda simulada

```bash
ros2 launch conveyor_webots conveyor_launch.py
```
Simulación Webots.

---

### Robotino simulación

```bash
ros2 launch robotino_webots robotino.launch.py
```

---

### Navegación

```bash
ros2 launch robotino_webots nav_robotino.launch.py
```

---

### SLAM

```bash
ros2 launch robotino_webots slam_mapping.launch.py
```

---

### Robot real

```bash
ros2 launch robotino_webots real_robotino.launch.py
```

---

## Uso recomendado

### Sistema completo banda

```bash
ros2 launch conveyor_dashboard dashboard.launch.py
```

Abrir:

http://localhost:8000

---

### Pruebas simples

```bash
ros2 run l510_controller l510_topic_node
```

---

### Simulación

```bash
ros2 launch robotino_webots robotino.launch.py
```

---

## Notas

- Usar ROS2 Jazzy
- Usar entorno virtual
- Verificar puerto /dev/ttyUSB0
