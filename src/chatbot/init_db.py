from chatbot.db.database import db


def init_database() -> None:
    print("Creating database tables...")
    db.create_tables()
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_database()
