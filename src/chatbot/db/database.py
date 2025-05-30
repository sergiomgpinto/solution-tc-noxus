import os
from typing import Optional, Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from chatbot.db.models import Base

load_dotenv()


class Database:
    def __init__(self, database_url: Optional[str] = None) -> None:
        self.database_url: str = database_url or os.getenv("DATABASE_URL")

        if self.database_url.startswith("sqlite"):
            self.engine: Engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False}
            )
        else:
            self.engine: Engine = create_engine(self.database_url)

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


db = Database()
