import sys
from chatbot.feedback_analytics import feedback_analytics


def show_summary(days: int = 7) -> None:
    summary = feedback_analytics.get_feedback_summary(days=days)

    print(f"\nFeedback Summary (last {summary['period_days']} days)")
    print("=" * 50)
    print(f"Total feedback: {summary['total_feedback']}")
    print(f"Thumbs up: {summary['thumbs_up']}")
    print(f"Thumbs down: {summary['thumbs_down']}")
    print(f"Satisfaction rate: {summary['satisfaction_rate']}%")
    print(f"As of: {summary['as_of']}")
    print("=" * 50)


def show_worst_messages(limit: int = 5) -> None:
    worst = feedback_analytics.get_worst_performing_messages(limit)

    if not worst:
        print("\nNo negative feedback found!")
        return

    print(f"\nTop {limit} Worst Performing Messages")
    print("=" * 50)

    for i, msg in enumerate(worst, 1):
        print(f"\n{i}. Message ID: {msg['message_id']}")
        print(f"   Negative feedback count: {msg['negative_feedback_count']}")
        print(f"   Conversation ID: {msg['conversation_id']}")
        print(f"   Content: {msg['content']}")


def show_conversation_feedback(conversation_id: int) -> None:
    feedback = feedback_analytics.get_conversation_feedback(conversation_id)

    if not feedback:
        print(f"\nNo feedback found for conversation {conversation_id}")
        return

    print(f"\nFeedback for Conversation {conversation_id}")
    print("=" * 50)

    for fb in feedback:
        emoji = "👍" if fb['feedback_type'] == "thumbs_up" else "👎"
        print(f"\n{emoji} {fb['feedback_type']} - {fb['created_at']}")
        print(f"   Message ({fb['message_role']}): {fb['message_content']}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m chatbot.feedback_cli summary [days]")
        print("  python -m chatbot.feedback_cli worst [limit]")
        print("  python -m chatbot.feedback_cli conversation <id>")
        return

    command = sys.argv[1]

    if command == "summary":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        show_summary(days)

    elif command == "worst":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        show_worst_messages(limit)

    elif command == "conversation" and len(sys.argv) > 2:
        conversation_id = int(sys.argv[2])
        show_conversation_feedback(conversation_id)

    else:
        print("Invalid command. Run without arguments to see usage.")


if __name__ == "__main__":
    main()
