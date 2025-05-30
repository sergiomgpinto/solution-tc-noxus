import sys
import json
from chatbot.config_manager import config_manager
from chatbot.config_schemas import ChatbotConfiguration


def create_default_configs() -> None:
    configs = [
        {
            "name": "Friendly Assistant",
            "description": "Warm and helpful",
            "model_parameters": {"temperature": 0.8},
            "prompt_template": {
                "system_prompt": "You are a warm, friendly assistant. Be conversational and helpful."
            }
        },
        {
            "name": "Technical Expert",
            "description": "Precise and detailed",
            "model_parameters": {"temperature": 0.3},
            "prompt_template": {
                "system_prompt": "You are a technical expert. Provide detailed, accurate technical information."
            }
        },
        {
            "name": "Creative Writer",
            "description": "Creative and imaginative",
            "model_parameters": {"temperature": 1.2, "max_tokens": 1000},
            "prompt_template": {
                "system_prompt": "You are a creative writer. Be imaginative and engaging."
            }
        }
    ]

    for config_data in configs:
        try:
            config = ChatbotConfiguration(**config_data)
            result = config_manager.create_configuration(config)
            print(f"Created configuration: {result['name']}")
        except ValueError as e:
            print(f"Skipping {config_data['name']}: {e}")


def list_configs() -> None:
    configs = config_manager.list_configurations()

    if not configs:
        print("No configurations found.")
        return

    print("\nConfigurations:")
    print("=" * 80)
    for config in configs:
        active = "ACTIVE" if config['is_active'] else "NOT ACTIVE"
        print(f"{active} [{config['id']}] {config['name']} (v{config['version']})")
        if config['description']:
            print(f"     {config['description']}")
        if config['tags']:
            print(f"     Tags: {', '.join(config['tags'])}")
        print(f"     Updated: {config['updated_at']}")
        print()


def show_config(config_id: int) -> None:
    config = config_manager.get_configuration(config_id)

    if not config:
        print(f"Configuration {config_id} not found")
        return

    print(f"\nConfiguration: {config['name']}")
    print("=" * 50)
    print(json.dumps(config['config'], indent=2))


def activate_config(config_id: int) -> None:
    try:
        result = config_manager.activate_configuration(config_id)
        print(f"Activated configuration: {result['name']}")
    except ValueError as e:
        print(f"Error: {e}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m chatbot.config_cli init         # Create default configs")
        print("  python -m chatbot.config_cli list         # List all configs")
        print("  python -m chatbot.config_cli show <id>    # Show config details")
        print("  python -m chatbot.config_cli activate <id> # Activate a config")
        return

    command = sys.argv[1]

    if command == "init":
        create_default_configs()
    elif command == "list":
        list_configs()
    elif command == "show" and len(sys.argv) > 2:
        show_config(int(sys.argv[2]))
    elif command == "activate" and len(sys.argv) > 2:
        activate_config(int(sys.argv[2]))
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
