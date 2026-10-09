import json
import re
import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot_interfaces.msg import TaskPlan, TaskAction
from robot_llm.prompt_template import SYSTEM_PROMPT, build_user_prompt

# ==============================================================================
# VERSION 1 : NATIVE ROS 2 LLM BRIDGE (ACTIVE DEFAULT)
# ==============================================================================
# Cette version traduit directement les commandes en langage naturel en un plan
# de tâches structuré (TaskPlan.msg) exécutable par la FSM robot_planner.
# ==============================================================================

class LlmBridgeNode(Node):
    def __init__(self):
        super().__init__('llm_bridge_node')

        self.declare_parameter('api_provider', 'mock')  # Options: 'anthropic', 'openai', 'ollama', 'mock'
        self.declare_parameter('api_key', '')

        self.provider = self.get_parameter('api_provider').get_parameter_value().string_value
        self.api_key = self.get_parameter('api_key').get_parameter_value().string_value

        self.sub_command = self.create_subscription(
            String,
            '/user_command',
            self.command_callback,
            10
        )

        self.pub_plan = self.create_publisher(
            TaskPlan,
            '/task_plan',
            10
        )

        self.get_logger().info(f"LLM Bridge Node (Version 1 Négociée) démarré avec provider: '{self.provider}'")

    def command_callback(self, msg: String):
        raw_cmd = msg.data.strip()
        self.get_logger().info(f"Commande reçue: '{raw_cmd}'")

        plan_dict = self.parse_command_with_llm(raw_cmd)
        if plan_dict is None:
            self.get_logger().error(f"Échec de génération du plan pour: '{raw_cmd}'")
            return

        task_plan_msg = TaskPlan()
        task_plan_msg.raw_command = raw_cmd

        for act in plan_dict.get('actions', []):
            action_msg = TaskAction()
            action_msg.action_type = str(act.get('action_type', ''))
            action_msg.params = [str(p) for p in act.get('params', [])]
            task_plan_msg.actions.append(action_msg)

        self.pub_plan.publish(task_plan_msg)
        self.get_logger().info(f"Publication de TaskPlan ({len(task_plan_msg.actions)} actions) sur /task_plan.")

    def parse_command_with_llm(self, command: str) -> dict:
        """Décode la commande en langage naturel via l'API LLM configurée ou le fallback local."""
        cmd_lower = command.lower()

        # En cas d'utilisation d'une clé API réelle (ex: Anthropic Claude / OpenAI) :
        if self.provider == 'anthropic' and self.api_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=self.api_key)
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": build_user_prompt(command)}]
                )
                content = response.content[0].text
                return json.loads(content)
            except Exception as e:
                self.get_logger().warn(f"Erreur API Anthropic: {e}. Bascule sur le fallback local.")

        # Fallback basé sur des règles pour le test local et hors-ligne
        actions = []
        if 'cuisine' in cmd_lower or 'kitchen' in cmd_lower:
            actions.append({"action_type": "go_to", "params": ["kitchen"]})
        elif 'salon' in cmd_lower or 'living' in cmd_lower:
            actions.append({"action_type": "go_to", "params": ["living_room"]})
        elif 'couloir' in cmd_lower or 'corridor' in cmd_lower:
            actions.append({"action_type": "go_to", "params": ["corridor"]})
        elif 'dock' in cmd_lower or 'home' in cmd_lower:
            actions.append({"action_type": "go_to", "params": ["dock"]})

        if 'bouteille' in cmd_lower or 'bottle' in cmd_lower:
            actions.append({"action_type": "search", "params": ["bottle"]})
        elif 'cherche' in cmd_lower or 'search' in cmd_lower:
            actions.append({"action_type": "search", "params": ["object"]})

        if 'photo' in cmd_lower or 'image' in cmd_lower:
            actions.append({"action_type": "take_photo", "params": []})

        if 'reviens' in cmd_lower or 'return' in cmd_lower:
            actions.append({"action_type": "return_home", "params": []})

        if not actions:
            actions.append({"action_type": "go_to", "params": ["kitchen"]})

        return {
            "actions": actions,
            "raw_command": command
        }


# ==============================================================================
# VERSION 2 : AGENT ROSA (NASA JPL / LANGCHAIN) (COMMENTÉE)
# ==============================================================================
# Pour activer la version ROSA :
# 1. Installer les dépendances : pip install rosa langchain-anthropic langchain-community
# 2. Décommenter le bloc ci-dessous et commenter la classe LlmBridgeNode ci-dessus.
# 3. Exécuter le nœud normalement via ros2 run robot_llm llm_bridge_node
# ==============================================================================
"""
from rosa import ROSA, RobotSystemPrompts
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool

# --- Définition des outils ROSA personnalisés ---
@tool
def navigate_to_room(room_name: str) -> str:
    \"\"\"Navigue vers une pièce spécifiée (kitchen, living_room, corridor, dock).\"\"\"
    # Code d'interaction ROS 2 avec Nav2 ou la mémoire
    return f"Navigation initiée vers {room_name}."

@tool
def search_object_in_room(label: str) -> str:
    \"\"\"Recherche un objet spécifique (ex: bottle) avec le module perception YOLO.\"\"\"
    return f"Recherche de l'objet {label} en cours."

class RosaBridgeNode(Node):
    def __init__(self):
        super().__init__('rosa_bridge_node')

        self.declare_parameter('anthropic_api_key', '')
        api_key = self.get_parameter('anthropic_api_key').get_parameter_value().string_value or os.environ.get('ANTHROPIC_API_KEY', '')

        # Initialisation du modèle de langage LangChain
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=api_key,
            temperature=0
        )

        # Définition des prompts système spécifiques au robot domestique
        prompts = RobotSystemPrompts(
            robot_name="Domestic Assistant Robot",
            embodiment="Diff-drive mobile robot with LiDAR, RGB camera, Nav2 and YOLO perception",
            about_your_capabilities="Tu peux naviguer entre les pièces (kitchen, living_room, corridor, dock) et rechercher des objets avec YOLO."
        )

        # Instanciation de l'agent ROSA (NASA JPL)
        self.rosa_agent = ROSA(
            ros_version=2,
            llm=llm,
            tools=[navigate_to_room, search_object_in_room],
            prompts=prompts
        )

        self.sub_command = self.create_subscription(
            String,
            '/user_command',
            self.command_callback,
            10
        )

        self.get_logger().info("ROSA Agent Bridge Node (NASA JPL) initialisé avec succès.")

    def command_callback(self, msg: String):
        command_text = msg.data.strip()
        self.get_logger().info(f"[ROSA Agent] Traitement de la commande : '{command_text}'")

        # Exécution de l'agent ReAct ROSA
        response = self.rosa_agent.invoke(command_text)
        self.get_logger().info(f"[ROSA Agent] Réponse : {response}")
"""


def main(args=None):
    rclpy.init(args=args)
    node = LlmBridgeNode()
    # Pour utiliser ROSA, remplacer LlmBridgeNode() par RosaBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
