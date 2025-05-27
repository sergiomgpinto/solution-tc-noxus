import sys
from .knowledge.manager import knowledge_manager
from .db.database import db


def create_source(name: str, description: str = "") -> None:
    source = knowledge_manager.create_knowledge_source(name, description)
    print(f"Created knowledge source '{source['name']}' with ID {source['id']}")


def add_documents(source_id: int, *documents: str) -> None:
    count = knowledge_manager.add_documents(source_id, list(documents))
    print(f"Added {count} documents to knowledge source {source_id}")


def list_sources() -> None:
    sources = knowledge_manager.list_knowledge_sources()
    if not sources:
        print("No knowledge sources found.")
        return

    print("\nKnowledge Sources:")
    print("-" * 60)
    for source in sources:
        print(f"[{source['id']}] {source['name']} - {source['document_count']} documents")
        if source['description']:
            print(f"    {source['description']}")
    print("-" * 60)


def search(query: str) -> None:
    results = knowledge_manager.search(query)
    if not results:
        print("No results found.")
        return

    print(f"\nSearch results for '{query}':")
    print("-" * 60)
    for i, (doc, score, metadata) in enumerate(results, 1):
        print(f"{i}. (Score: {score:.3f})")
        print(f"   {doc[:200]}..." if len(doc) > 200 else f"   {doc}")
        print()


def main() -> None:
    db.create_tables()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m chatbot.knowledge_cli create <name> [description]")
        print("  python -m chatbot.knowledge_cli add <source_id> <document1> [document2] ...")
        print("  python -m chatbot.knowledge_cli list")
        print("  python -m chatbot.knowledge_cli search <query>")
        return

    command = sys.argv[1]

    if command == "create" and len(sys.argv) >= 3:
        name = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        create_source(name, description)

    elif command == "add" and len(sys.argv) >= 4:
        source_id = int(sys.argv[2])
        documents = sys.argv[3:]
        add_documents(source_id, *documents)

    elif command == "list":
        list_sources()

    elif command == "search" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        search(query)

    else:
        print("Invalid command. Run without arguments to see usage.")


if __name__ == "__main__":
    main()
