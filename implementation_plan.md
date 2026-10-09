# Plan d'implémentation — Assistant Domestique ROS 2

Développement complet des packages restants pour le projet **Assistant Domestique ROS 2** sous ROS 2 Humble et Gazebo Fortress.

## User Review Required

> [!IMPORTANT]
> **Gazebo Fortress & Python 3.10** : Tous les nœuds et configurations sont préparés spécifiquement pour ROS 2 Humble sur Ubuntu 22.04 / Windows ROS 2 workspace (bridges `ros_gz_bridge`, paquets `nav2`, `slam_toolbox`, `ultralytics`, `pydantic`).

> [!NOTE]
> Nous allons créer les packages structurés et modulaires afin que chaque partie puisse être compilée et testée indépendamment avec `colcon build`.

---

## Proposed Changes

### 1. `robot_description` (Finalisation de la Phase 1)

#### [NEW] [sensors.xacro](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_description/urdf/sensors.xacro)
- Définition des macros Xacro `lidar` (`base_laser_link`), `camera` (`camera_link` + optical frame), et `imu` (`imu_link`).
- Configuration des capteurs pour Gazebo Fortress (`gpu_lidar`, `camera`, `imu`).

#### [NEW] [display.launch.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_description/launch/display.launch.py)
- Script de lancement RViz2 avec `joint_state_publisher_gui` et `robot_state_publisher`.

#### [NEW] [urdf.rviz](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_description/rviz/urdf.rviz)
- Fichier de configuration RViz pour inspecter l'URDF et l'arbre TF.

---

### 2. `simulation` (Monde Gazebo Fortress + Bridge ROS 2)

#### [NEW] [package.xml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/package.xml)
#### [NEW] [CMakeLists.txt](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/CMakeLists.txt)
#### [NEW] [appartement.sdf](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/worlds/appartement.sdf)
- Monde Gazebo Fortress représentant un appartement avec pièces (Cuisine, Salon, Couloir, Station/Dock), murs et éclairage.

#### [NEW] [ros_gz_bridge.yaml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/config/ros_gz_bridge.yaml)
- Mappage des topics entre Gazebo et ROS 2 (`/scan`, `/odom`, `/cmd_vel`, `/camera/image_raw`, `/camera/camera_info`, `/imu/data`, `/tf`, `/tf_static`).

#### [NEW] [simulation.launch.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/launch/simulation.launch.py)
- Lancement de `ros_gz_sim`, génération (spawn) du robot depuis le Xacro, démarrage de `robot_state_publisher` et du `ros_gz_bridge`.

---

### 3. `robot_navigation` (SLAM + Nav2 + Configuration des Pièces)

#### [NEW] [package.xml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/package.xml)
#### [NEW] [CMakeLists.txt](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/CMakeLists.txt)
#### [NEW] [nav2_params.yaml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/config/nav2_params.yaml)
- Paramètres Nav2 (AMCL, Costmaps globale/locale, RegulatedPurePursuit/DWB Controller, NavFn Planner, Behavior Server).

#### [NEW] [slam_toolbox_params.yaml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/config/slam_toolbox_params.yaml)
- Configuration SLAM Toolbox pour la cartographie 2D online.

#### [NEW] [room_poses.yaml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/config/room_poses.yaml)
- Coordonnées 2D pré-enregistrées des pièces (kitchen, living_room, corridor, dock).

#### [NEW] [slam.launch.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/launch/slam.launch.py)
#### [NEW] [navigation.launch.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_navigation/launch/navigation.launch.py)

---

### 4. `robot_perception` (Détection YOLO & Serveur Action SearchObject — basé sur Mike Likes Robots)

#### [NEW] [package.xml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/package.xml)
#### [NEW] [setup.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/setup.py)
#### [NEW] [detector_node.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/robot_perception/detector_node.py)
- Nœud ROS 2 sous-crivant à `/camera/image_raw`, exécutant la détection en temps réel Ultralytics YOLO via `cv_bridge`, publiant `/detected_objects` (`vision_msgs/Detection2DArray`) et `/perception/image_annotated` pour le debug visuel (pattern `yolo26_ros2` de Mike Likes Robots).

#### [NEW] [search_object_server.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/robot_perception/search_object_server.py)
- Serveur d'action ROS 2 pour `robot_interfaces/action/SearchObject`.

#### [NEW] [yolo_params.yaml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/config/yolo_params.yaml)
#### [NEW] [perception.launch.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_perception/launch/perception.launch.py)

---

### 5. `robot_memory` (BDD SQLite & Services de mémoire)

#### [NEW] [package.xml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_memory/package.xml)
#### [NEW] [setup.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_memory/setup.py)
#### [NEW] [db_schema.sql](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_memory/robot_memory/db_schema.sql)
- Schéma SQL pour enregistrer les pièces et la localisation des objets détectés.

#### [NEW] [memory_node.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_memory/robot_memory/memory_node.py)
- Serveur de services ROS 2 implémentant `QueryRoomPose.srv` et `UpdateObject.srv`.

---

### 6. `robot_llm` (Passerelle LLM & Traduction de commandes — basé sur Mike Likes Robots `llm-robot-control`)

#### [NEW] [package.xml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_llm/package.xml)
#### [NEW] [setup.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_llm/setup.py)
#### [NEW] [schema.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_llm/robot_llm/schema.py)
- Schémas Pydantic pour valider la structure JSON extraite du LLM (Anthropic / OpenAI / Ollama fallback).

#### [NEW] [prompt_template.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_llm/robot_llm/prompt_template.py)
- Prompt système guidant le LLM à décomposer les intentions utilisateur en sous-tâches concrètes (`go_to`, `search`, `return_home`).

#### [NEW] [llm_bridge_node.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_llm/robot_llm/llm_bridge_node.py)
- Nœud ROS 2 sous-crivant à `/user_command`, appelant l'API LLM (avec fallback local/mock), validant le schéma et publiant `TaskPlan.msg` sur `/task_plan`.

---

### 7. `robot_planner` (Planificateur FSM & Exécution)

#### [NEW] [package.xml](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_planner/package.xml)
#### [NEW] [setup.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_planner/setup.py)
#### [NEW] [task_planner_node.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/robot_planner/robot_planner/task_planner_node.py)
- Automate d'états FSM coordonnant le décodage du plan, les requêtes mémoire, la navigation Nav2, la détection perception et le compte-rendu de mission `MissionReport.msg`.

---

### 8. `simulation/launch/bringup_all.launch.py` (Lancement Global)

#### [NEW] [bringup_all.launch.py](file:///c:/Users/Gaspard/Projects/domestic-assistant-ros2/src/simulation/launch/bringup_all.launch.py)
- Fichier de lancement global intégrant la simulation, la navigation, la perception, la mémoire, le LLM bridge et le planner.

---

## Verification Plan

### Automated Tests / Validation de compilation
1. Vérification de la structure du workspace et de l'intégrité Xacro / Launch.
2. Validation que chaque package s'interface correctement avec `robot_interfaces`.

### Manual Verification
1. `colcon build` sur l'ensemble des packages du workspace.
2. Inspecter les fichiers créés et valider leur conformité avec la spécification du projet.
