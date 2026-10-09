# Walkthrough — Assistant Domestique ROS 2

L'ensemble des packages du projet **Assistant Domestique ROS 2** a été développé et intégré en suivant l'architecture cible et les principes issus des articles de Mike Likes Robots (*LLM Robot Control* & *Ultralytics YOLO Computer Vision*).

---

## 📦 Packages Créés & Structure du Projet

```text
domestic-assistant-ros2/src/
├── robot_interfaces/     # Messages custom (TaskPlan, TaskAction, MissionReport, QueryRoomPose, SearchObject)
├── robot_description/    # URDF Xacro complet (Base + Roues + LiDAR + Caméra + IMU + Config RViz)
├── simulation/           # Monde Gazebo Fortress (appartement.sdf) + Bridge ROS 2 + Bringup global
├── robot_navigation/     # Configurations SLAM Toolbox, Nav2 (AMCL, costmaps, pure pursuit) & Poses des pièces
├── robot_perception/     # Détection temps réel Ultralytics YOLO via cv_bridge + Serveur action SearchObject
├── robot_memory/         # Base SQLite persistence (Pièces, Objets) & Services ROS 2
├── robot_llm/            # Passerelle LLM, validation Pydantic/JSON & conversion de commandes vers TaskPlan
└── robot_planner/        # Planificateur FSM coordonnant la mission complète LLM → Navigation → Perception → Rapport
```

---

## 🛠️ Détails des Implémentations

### 1. `robot_description`
- [`sensors.xacro`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_description/urdf/sensors.xacro) : Capteurs `gpu_lidar`, `camera` (avec repère optique ROS/OpenCV) et `imu`.
- [`display.launch.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_description/launch/display.launch.py) & [`urdf.rviz`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_description/rviz/urdf.rviz) : Inspection et validation interactive du robot dans RViz.

### 2. `simulation`
- [`appartement.sdf`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/worlds/appartement.sdf) : Modèle du monde en appartement avec murs, pièces (cuisine, salon, couloir, station) et objet cible (bouteille).
- [`ros_gz_bridge.yaml`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/config/ros_gz_bridge.yaml) : Mappage bidirectionnel ROS 2 / Gazebo (`/scan`, `/odom`, `/cmd_vel`, `/camera/image_raw`, `/imu/data`).
- [`simulation.launch.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/launch/simulation.launch.py) : Lancement de Gazebo Fortress, génération du robot et du pont.

### 3. `robot_navigation`
- [`nav2_params.yaml`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/config/nav2_params.yaml) & [`slam_toolbox_params.yaml`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/config/slam_toolbox_params.yaml) : Paramétrage Nav2 AMCL et cartographie.
- [`room_poses.yaml`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/config/room_poses.yaml) : Poses prédéfinies des pièces.
- [`slam.launch.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/launch/slam.launch.py) & [`navigation.launch.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/launch/navigation.launch.py) : Lancement de la cartographie et du stack de navigation.

### 4. `robot_perception` *(Inspire de Mike Likes Robots - yolo26_ros2)*
- [`detector_node.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/robot_perception/detector_node.py) : Inférence Ultralytics YOLO temps réel avec conversion `cv_bridge`, publication de `/detected_objects` (`Detection2DArray`) et du flux annoté visuel `/perception/image_annotated`.
- [`search_object_server.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/robot_perception/search_object_server.py) : Serveur d'action `SearchObject` pour la recherche d'objets.
- [`dataset_generator.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/robot_perception/dataset_generator.py) : Script de génération automatique de datasets d'entraînement synthétiques YOLO en simulation.

### 5. `robot_memory`
- [`db_schema.sql`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_memory/robot_memory/db_schema.sql) & [`memory_node.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_memory/robot_memory/memory_node.py) : Base SQLite gérant les services `/memory/query_room_pose` et `/memory/update_object`.

### 6. `robot_llm` *(Inspiré de Mike Likes Robots - llm-robot-control & ROSA NASA JPL)*
- [`schema.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_llm/robot_llm/schema.py) & [`prompt_template.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_llm/robot_llm/prompt_template.py) : Validation Pydantic et prompts structurés d'extraction d'actions.
- [`llm_bridge_node.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_llm/robot_llm/llm_bridge_node.py) : Contient **2 versions** :
  1. **Version 1 (Active)** : Passerelle ROS 2 natif traduisant directement en `TaskPlan.msg` (découplage et sécurité garantie).
  2. **Version 2 (Commentée)** : Agent ReAct ROSA (NASA JPL / LangChain) permettant une interaction agentique directe via des outils ROS 2 (`@tool`).

### 7. `robot_planner`
- [`task_planner_node.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_planner/robot_planner/task_planner_node.py) : Automate FSM coordonnant les requêtes mémoire, la navigation Nav2, la détection perception et publiant le bilan de mission `/mission_report`.

### 8. Integration Globale
- [`bringup_all.launch.py`](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/launch/bringup_all.launch.py) : Fichier de lancement unifié démarrant la chaîne complète.

---

## 🚀 Commandes de Compilation et Validation

Pour compiler le workspace colcon :
```bash
cd ~/ros2_ws # ou le chemin vers le workspace ROS 2
colcon build
source install/setup.bash
```

Pour lancer la simulation complète :
```bash
ros2 launch simulation bringup_all.launch.py
```

Pour envoyer une commande en langage naturel :
```bash
ros2 topic pub --once /user_command std_msgs/msg/String "{data: 'Va dans la cuisine et cherche une bouteille'}"
```

---

## 📸 Génération Automatique de Dataset Synthétique & Entraînement YOLO

Pour générer automatiquement un dataset d'entraînement YOLO sans annotation manuelle :

1. **Lancer la simulation Gazebo** :
   ```bash
   ros2 launch simulation simulation.launch.py
   ```

2. **Lancer le générateur automatique dans un second terminal** :
   ```bash
   ros2 run robot_perception dataset_generator --ros-args -p num_samples:=200 -p output_dir:=my_bottle_dataset
   ```

3. **Lancer l'entraînement du modèle YOLO** :
   ```python
   from ultralytics import YOLO

   model = YOLO("yolo11n.pt")
   model.train(data="my_bottle_dataset/dataset.yaml", epochs=30, imgsz=640)
   ```

