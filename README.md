# Sistema Robótico ROS2 con Banda Transportadora, Robotino, Visión, Audio y Simulación Webots

<div align="center">
  <img width="331" height="496" alt="Captura de pantalla 2026-03-17 a la(s) 9 47 18 p m" src="https://github.com/user-attachments/assets/935a6e47-0d9a-458d-832b-6bb80e144825" />
</div>

---

## Descripción general

Este repositorio implementa un sistema robótico completo basado en ROS2 que integra:

- Control de banda transportadora (TECO L510 vía Modbus RTU)
- Dashboard web en tiempo real
- Interfaz táctil tipo HMI
- Control mediante joystick
- Simulación en Webots
- Robotino (simulación + real)
- Visión artificial (YOLO, segmentación, pose, reconocimiento facial)
- Audio (voz a texto + texto a voz)
- Navegación autónoma (Nav2 + SLAM)
- Árboles de comportamiento

---

## Estructura del repositorio

```text
.
├── maps
├── worlds
├── requirements.txt
├── src
│   ├── conveyor_dashboard
│   ├── conveyor_webots
│   ├── joy_mapper
│   ├── known_locations_tf_server
│   ├── l510_controller
│   ├── robotino_audio
│   ├── robotino_bts
│   ├── robotino_interfaces
│   ├── robotino_webots
│   ├── robot_movement
│   ├── touch_hmi
│   └── vision
```

---

## Instalación

### Crear workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

### Entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools
```

### Dependencias

```bash
pip install pymodbus pyserial opencv-python fastapi uvicorn pyyaml numpy scipy
```

---

## Ejecución

### Banda real

```bash
ros2 launch conveyor_dashboard dashboard.launch.py
```

### Simulación

```bash
ros2 launch robotino_webots robotino.launch.py
```

---

## Notas

- Usar ROS2 Jazzy
- Usar entorno virtual
- Verificar permisos de /dev/ttyUSB0
