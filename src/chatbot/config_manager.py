from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .db.database import db
from .db.models import Configuration
from .config_schemas import ChatbotConfiguration


class ConfigurationManager:
    def create_configuration(
            self,
            config_data: ChatbotConfiguration,
            activate: bool = False
    ) -> Dict[str, Any]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            existing = session.query(Configuration).filter_by(
                name=config_data.name
            ).first()

            if existing:
                raise ValueError(f"Configuration '{config_data.name}' already exists")

            if activate:
                session.query(Configuration).update({Configuration.is_active: False})

            config = Configuration(
                name=config_data.name,
                description=config_data.description,
                config_json=config_data.model_dump(),
                is_active=activate
            )
            config.tag_list = config_data.tags

            session.add(config)
            session.commit()

            return {
                "id": config.id,
                "name": config.name,
                "version": config.version,
                "is_active": config.is_active,
                "created_at": config.created_at.isoformat()
            }
        finally:
            session.close()

    def get_active_configuration(self) -> Optional[ChatbotConfiguration]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            active_config = session.query(Configuration).filter_by(
                is_active=True
            ).first()

            if active_config:
                return ChatbotConfiguration(**active_config.config_json)

            return ChatbotConfiguration(name="default")
        finally:
            session.close()

    def get_configuration(self, config_id: int) -> Optional[Dict[str, Any]]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            config = session.query(Configuration).filter_by(id=config_id).first()

            if not config:
                return None

            return {
                "id": config.id,
                "name": config.name,
                "description": config.description,
                "config": config.config_json,
                "version": config.version,
                "is_active": config.is_active,
                "tags": config.tag_list,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            }
        finally:
            session.close()

    def update_configuration(
            self,
            config_id: int,
            config_data: ChatbotConfiguration
    ) -> Dict[str, Any]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            config = session.query(Configuration).filter_by(id=config_id).first()

            if not config:
                raise ValueError(f"Configuration {config_id} not found")

            config.config_json = config_data.model_dump()
            config.version += 1
            config.tag_list = config_data.tags

            session.commit()

            return {
                "id": config.id,
                "name": config.name,
                "version": config.version,
                "updated_at": config.updated_at.isoformat()
            }
        finally:
            session.close()

    def activate_configuration(self, config_id: int) -> Dict[str, Any]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            config = session.query(Configuration).filter_by(id=config_id).first()

            if not config:
                raise ValueError(f"Configuration {config_id} not found")

            session.query(Configuration).update({Configuration.is_active: False})

            config.is_active = True
            session.commit()

            return {
                "id": config.id,
                "name": config.name,
                "activated": True
            }
        finally:
            session.close()

    def list_configurations(
            self,
            tags: Optional[List[str]] = None,
            active_only: bool = False
    ) -> List[Dict[str, Any]]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            query = session.query(Configuration)

            if active_only:
                query = query.filter_by(is_active=True)

            if tags:
                tag_conditions = [Configuration.tags.contains(tag) for tag in tags]
                query = query.filter(and_(*tag_conditions))

            configs = query.order_by(Configuration.updated_at.desc()).all()

            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "version": c.version,
                    "is_active": c.is_active,
                    "tags": c.tag_list,
                    "updated_at": c.updated_at.isoformat()
                }
                for c in configs
            ]
        finally:
            session.close()

    def delete_configuration(self, config_id: int) -> bool:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            config = session.query(Configuration).filter_by(id=config_id).first()

            if not config:
                return False

            if config.is_active:
                raise ValueError("Cannot delete active configuration")

            session.delete(config)
            session.commit()
            return True
        finally:
            session.close()


config_manager = ConfigurationManager()
