import sys
from chatbot.ab_test_manager import ab_test_manager


def main():
    if len(sys.argv) < 4:
        print("Usage: python -m chatbot.ab_test_cli create <control_id> <treatment_id> [traffic_percentage]")
        return

    command = sys.argv[1]

    if command == "create":
        control_id = int(sys.argv[2])
        treatment_id = int(sys.argv[3])
        traffic = int(sys.argv[4]) if len(sys.argv) > 4 else 50

        result = ab_test_manager.create_ab_test(
            name=f"Test_{control_id}_vs_{treatment_id}",
            control_config_id=control_id,
            treatment_config_id=treatment_id,
            traffic_percentage=traffic
        )
        print(f"Created A/B test: {result}")


if __name__ == "__main__":
    main()
