# Sistema Robótico ROS2 con Banda Transportadora, Robotino, Visión, Audio y Simulación Webots

<div align="center">
  <img width="331" height="496" alt="Captura de pantalla 2026-03-17 a la(s) 9 47 18 p m" src="https://github.com/user-attachments/assets/935a6e47-0d9a-458d-832b-6bb80e144825" />
</div>

---

## Descripción general

Este repositorio implementa un sistema robótico completo basado en ROS2 que integra:

- Control de una banda transportadora mediante un variador TECO L510 (Modbus RTU sobre RS485)
- Interfaz gráfica web en tiempo real (dashboard)
- Interfaz táctil tipo HMI
- Control mediante joystick
- Simulación en Webots (banda y robot móvil)
- Robotino (simulación y robot real)
- Visión artificial (YOLO, segmentación, pose, reconocimiento facial)
- Audio (reconocimiento de voz y síntesis)
- Navegación autónoma (Nav2 + SLAM)
- Árboles de comportamiento

El sistema está diseñado de forma modular mediante paquetes ROS2.

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
Instalación
1. Crear workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

Copiar el repositorio dentro de src.

2. Crear ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools
3. Instalar dependencias Python
pip install pymodbus pyserial opencv-python fastapi uvicorn pyyaml numpy scipy ultralytics torch torchvision facenet-pytorch vosk py_trees py_trees_ros
4. Dependencias del sistema
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  ros-jazzy-joy \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-tf2-ros \
  ros-jazzy-webots-ros2-driver \
  espeak-ng
5. Permisos serial
sudo usermod -a -G dialout $USER

Reiniciar sesión.

6. Compilar
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source venv/bin/activate
colcon build --symlink-install
source install/setup.bash
Paquetes principales
conveyor_dashboard

Control completo de la banda con interfaz web.

Nodos:

ros2 run conveyor_dashboard l510_node
ros2 run conveyor_dashboard webcam_node
ros2 run conveyor_dashboard dashboard_node

Funciones:

Control de banda
Telemetría en tiempo real
Video en vivo
Interfaz web (FastAPI)

Abrir:

http://localhost:8000
l510_controller

Control directo del variador.

ros2 run l510_controller l510_node
ros2 run l510_controller l510_topic_node

Comandos:

run
reverse
stop
freq 20
touch_hmi

Interfaz táctil industrial.

ros2 run touch_hmi touch_hmi_node
joy_mapper

Control con joystick.

ros2 run joy joy_node
ros2 run joy_mapper joy_mapper_node
conveyor_webots

Simulación de banda.

ros2 launch conveyor_webots conveyor_launch.py
robotino_webots

Simulación y robot real.

Ejemplos:

ros2 launch robotino_webots robotino.launch.py
ros2 launch robotino_webots nav_robotino.launch.py
ros2 launch robotino_webots slam_mapping.launch.py
ros2 launch robotino_webots real_robotino.launch.py
vision

Percepción completa.

ros2 run vision vision_node
ros2 run vision yolo_person_node
ros2 run vision obstacle_avoidance_node
robotino_audio

Reconocimiento de voz.

ros2 run robotino_audio vosk_node
robotino_tts

Síntesis de voz.

ros2 run robotino_tts espeak_tts_node
robotino_bts

Árboles de comportamiento.

ros2 run robotino_bts task_manager
known_locations_tf_server

Ubicaciones conocidas.

ros2 run known_locations_tf_server known_locations_server
Launch principales
Banda real (RECOMENDADO)
ros2 launch conveyor_dashboard dashboard.launch.py
Banda simulada
ros2 launch conveyor_webots conveyor_launch.py
Robotino simulación
ros2 launch robotino_webots robotino.launch.py
Navegación
ros2 launch robotino_webots nav_robotino.launch.py
SLAM
ros2 launch robotino_webots slam_mapping.launch.py
Robot real
ros2 launch robotino_webots real_robotino.launch.py
Tópicos principales
/conveyor/cmd
/conveyor/telemetry
/l510_cmd
/camera/image/compressed
/conveyor_speed
Comandos útiles

Ver nodos:

ros2 node list

Ver tópicos:

ros2 topic list

Telemetría:

ros2 topic echo /conveyor/telemetry

Enviar comando:

ros2 topic pub --once /conveyor/cmd std_msgs/msg/String "{data: '{\"action\":\"forward\"}'}"
Recomendación de uso

Para operación completa de la banda:

ros2 launch conveyor_dashboard dashboard.launch.py

Para pruebas rápidas:

ros2 run l510_controller l510_topic_node

Para simulación:

ros2 launch robotino_webots robotino.launch.py
Notas
Existen dos sistemas de comandos (/l510_cmd y /conveyor/cmd)
Se recomienda unificarlos en producción
El sistema está modularizado para pruebas independientes
Estado del proyecto
Banda transportadora: funcional con ROS2
Dashboard web: funcional
Interfaz táctil: funcional
Simulación Webots: funcional
Robotino: integración completa
Visión: múltiples módulos disponibles
Audio: integrado
Navegación: funcional

Proyecto listo para integración avanzada y despliegue en robot real.
```
