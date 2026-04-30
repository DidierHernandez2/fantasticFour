# Sistema Robótico ROS2 con Banda Transportadora, Robotino y Simulación

<div align="center">
  <img width="331" height="496" src="https://github.com/user-attachments/assets/935a6e47-0d9a-458d-832b-6bb80e144825" />
</div>

---
## Videos entrgables:
**Video Demostración Dashboard Banda:** https://youtu.be/YWbX2HWoBfs
**Video Demostración Webots:** https://youtu.be/8T3zra04jqQ

## Descripción

Sistema modular basado en ROS2 que integra:

- Banda transportadora (TECO L510 vía Modbus RTU)
- Dashboard web en tiempo real
- Interfaz táctil (HMI)
- Control por joystick
- Simulación en Webots
- Robotino
- Visión artificial y audio

---

## Configuración del variador L510

Para que la comunicación por RS485 funcione correctamente, el variador TECO L510 debe configurarse con los siguientes parámetros:

### Parámetros configurados

| Parámetro | Valor | Descripción |
|----------|------|------------|
| 00-02 | 2 | Fuente de RUN por comunicación |
| 00-03 | 0 | Dirección controlada por comunicación |
| 00-05 | 5 | Fuente de frecuencia por comunicación |
| 00-06 | 2 | Fuente secundaria de frecuencia |
| 09-00 | 1 | Dirección slave (ID Modbus) |
| 09-01 | 0 | Modo comunicación |
| 09-02 | 1 | Velocidad comunicación |
| 09-03 | 0 | Bits de datos |
| 09-04 | 0 | Paridad |
| 09-05 | 0 | Stop bits |

### Configuración de comunicación

- Puerto: `/dev/ttyUSB0`
- Baudrate: 9600
- Paridad: N
- Stopbits: 1
- Bytesize: 8

### Registros usados

- 9473 → RUN / STOP / DIRECCIÓN
- 9474 → FRECUENCIA
- 9504 → ESTADO
- 9505 → ERROR
- 9507 → FRECUENCIA COMANDADA
- 9508 → FRECUENCIA REAL
- 9511 → CORRIENTE

---

## Instalación

### Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

---

### Entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

---

### Dependencias

```bash
pip install -r requirements.txt
```

---

### Compilar

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

---

## ROS2 RUN

### Banda (dashboard)

```bash
ros2 run conveyor_dashboard l510_node
ros2 run conveyor_dashboard webcam_node
ros2 run conveyor_dashboard dashboard_node
```

---

### Control directo

```bash
ros2 run l510_controller l510_node
ros2 run l510_controller l510_topic_node
```

---

### Interfaz táctil

```bash
ros2 run touch_hmi touch_hmi_node
```

---

### Joystick

```bash
ros2 run joy_mapper joy_mapper_node
```

---

## ROS2 LAUNCH

### Sistema completo banda

```bash
ros2 launch conveyor_dashboard dashboard.launch.py
```

---

### Simulación

```bash
ros2 launch robotino_webots robotino.launch.py
```

---

## Acceso remoto (Cloudflare)

Para exponer el dashboard públicamente:

```bash
cloudflared tunnel --url http://localhost:8000
```

Esto generará una URL pública accesible desde cualquier red.

---

## Uso recomendado

### Ejecutar sistema completo

```bash
ros2 launch conveyor_dashboard dashboard.launch.py
```

Abrir en navegador:

```
http://localhost:8000
```

---

### Acceso remoto

```bash
cloudflared tunnel --url http://localhost:8000
```

---

## Notas

- Usar ROS2 Jazzy
- Verificar permisos de `/dev/ttyUSB0`
- Usar entorno virtual
- Mantener consistencia entre `/l510_cmd` y `/conveyor/cmd`

---

## Estado

- Banda: funcional
- Dashboard: funcional
- Comunicación RS485: funcional
- Cloudflare: funcional
