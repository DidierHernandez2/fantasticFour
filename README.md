# Sistema Robótico ROS2 con Banda Transportadora, Robotino y Simulación

<div align="center">
  <img width="331" height="496" src="https://github.com/user-attachments/assets/935a6e47-0d9a-458d-832b-6bb80e144825" />
</div>

---
## Miembros:
- **Alonso Guerrero Fong** *A01657743*
- **Didier Aarón Ricardo Hernández Ferreira** *A01663817*
- **Mariana Edith Ramírez Navarrete** *A01662169*
- **Patricio Maldonado Poiré** *A01664661*

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

# Requisitos

- Ubuntu 24.04
- ROS2 Jazzy
- Python 3
- pip
- rosdep
- Webots (opcional para simulación)

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

# Instalación

## Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

---

## Clonar repositorio

```bash
git clone https://github.com/DidierHernandez2/fantasticFour.git src/fantasticFour
```

---

## Dependencias del sistema

```bash
sudo apt update

sudo apt install -y \
python3-pip \
python3-venv \
python3-rosdep
```

---

## Inicializar rosdep

```bash
sudo rosdep init
rosdep update
```

---

## Entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
```

---

## Dependencias Python

```bash
pip install -r requirements_python.txt
```

---

## Dependencias ROS2

```bash
rosdep install --from-paths src --ignore-src -r -y
```

---

## Compilar

```bash
cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash

colcon build --symlink-install

source install/setup.bash
```

---

# Generar archivos de dependencias automáticamente

## Generar requirements_python.txt

```bash
pipreqs . --force && \
grep -viE "(rclpy|geometry_msgs|sensor_msgs|std_msgs|std_srvs|nav_msgs|vision_msgs|tf2|launch_ros|cv_bridge|webots_ros2_driver|rosidl|ament|example_interfaces|service_msgs|visualization_msgs|nav2_msgs|control_msgs|controller|pytest|setuptools|testpath)" requirements.txt | \
cut -d '=' -f1 | \
sort -u > requirements_python.txt && \
echo -e "pyserial\npython-dotenv\nwebsockets" >> requirements_python.txt && \
sort -u requirements_python.txt -o requirements_python.txt
```

---

## Generar ros2_requirements.txt

```bash
grep -R -E "<depend>|<exec_depend>|<build_depend>" src/ \
| sed -E 's/.*<(depend|exec_depend|build_depend)>(.*)<\/(depend|exec_depend|build_depend)>.*/\2/' \
| grep -viE "(python3-pymodbus|python3-yaml|py_trees)" \
| sort -u > ros2_requirements.txt
```

---

# ROS2 RUN

## Banda (dashboard)

```bash
ros2 run conveyor_dashboard l510_node
ros2 run conveyor_dashboard webcam_node
ros2 run conveyor_dashboard dashboard_node
```

---

## Control directo

```bash
ros2 run l510_controller l510_node
ros2 run l510_controller l510_topic_node
```

---

## Interfaz táctil

```bash
ros2 run touch_hmi touch_hmi_node
```

---

## Joystick

```bash
ros2 run joy_mapper joy_mapper_node
```

---

# ROS2 LAUNCH

## Sistema completo banda

```bash
ros2 launch conveyor_dashboard dashboard.launch.py
```

---

## Simulación

```bash
ros2 launch robotino_webots robotino.launch.py
```

---

# Acceso remoto (Cloudflare)

Para exponer el dashboard públicamente:

```bash
cloudflared tunnel --url http://localhost:8000
```

Esto generará una URL pública accesible desde cualquier red.

---

# Uso recomendado

## Ejecutar sistema completo

```bash
ros2 launch conveyor_dashboard dashboard.launch.py
```

Abrir en navegador:

```txt
http://localhost:8000
```

---

## Acceso remoto

```bash
cloudflared tunnel --url http://localhost:8000
```

---

# Notas

- Usar ROS2 Jazzy
- Verificar permisos de `/dev/ttyUSB0`
- Usar entorno virtual
- Mantener consistencia entre `/l510_cmd` y `/conveyor/cmd`

---

# Estado

- Banda: funcional
- Dashboard: funcional
- Comunicación RS485: funcional
- Cloudflare: funcional
- Webots: funcional
- Robotino: funcional
