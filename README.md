# Assistant Domestique Autonome — ROS 2 Humble

Robot domestique simulé (Gazebo Fortress) capable de comprendre une commande en langage naturel, planifier une mission, naviguer, détecter des objets et rendre compte du résultat.

## Prérequis

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Fortress via `ros-humble-ros-gz`

```bash
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh
source /opt/ros/humble/setup.bash
```

## Build

```bash
cd ~/ros2_ws   # or clone/symlink this repo into ~/ros2_ws/src/
colcon build --symlink-install
source install/setup.bash
```

## Lancement rapide

### Simulation seule (Phase 1)

```bash
ros2 launch simulation simulation.launch.py
# Terminal 2:
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### SLAM (Phase 2 — cartographie)

```bash
ros2 launch simulation simulation.launch.py
ros2 launch robot_navigation slam.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# Sauvegarder la carte:
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \
  "{name: {data: '$(pwd)/src/robot_navigation/maps/appartement'}}"
```

### Navigation autonome (Phase 2)

```bash
ros2 launch simulation simulation.launch.py
ros2 launch robot_navigation navigation.launch.py
# Envoyer un goal via RViz (Nav2 Goal) ou:
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 2.0, y: 1.5}, orientation: {w: 1.0}}}}"
```

### Perception YOLO (Phase 3)

```bash
ros2 launch robot_perception perception.launch.py
ros2 topic echo /detected_objects
ros2 action send_goal /search_object robot_interfaces/action/SearchObject "{label: bottle}"
```

### Mission complète (Phase 9)

```bash
ros2 launch simulation bringup_all.launch.py
# Taper une commande dans le terminal du command_listener, ex.:
# Va dans la cuisine
# kitchen
```

Variables d'environnement LLM (Phase 6) :

```bash
export LLM_PROVIDER=anthropic   # ou ollama
export ANTHROPIC_API_KEY=sk-...
export OLLAMA_MODEL=llama3.2
```

## Architecture des packages

| Package | Rôle |
|---|---|
| `robot_interfaces` | Messages, services et actions custom |
| `robot_description` | URDF/Xacro du robot |
| `simulation` | Monde Gazebo + launch global |
| `robot_navigation` | SLAM Toolbox + Nav2 + AMCL |
| `robot_perception` | YOLO + action `search_object` |
| `robot_control` | Suivi PID de personne (optionnel) |
| `robot_llm` | Pont LLM → plan JSON |
| `robot_planner` | Orchestrateur FSM de mission |
| `robot_memory` | Mémoire persistante SQLite |

## Scénario de démonstration

> *Va dans le salon, cherche une bouteille, prends une photo et reviens.*

Flux : `command_listener` → `llm_bridge` → `task_planner` → Nav2 / perception / mémoire → `mission_report`.

## Pièges fréquents

1. Aligner les QoS caméra (`best_effort`) entre Gazebo et les subscribers.
2. Ne pas mélanger Gazebo installé manuellement avec `ros-humble-ros-gz`.
3. Installer `ultralytics` dans le même Python que `rclpy` (pas de venv isolé).
4. Ajuster `inflation_radius` dans Nav2 si le robot bloque dans les couloirs.
