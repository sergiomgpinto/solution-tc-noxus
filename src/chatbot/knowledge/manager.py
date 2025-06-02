import os
import chromadb
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from chromadb.config import Settings
from sqlalchemy.orm import Session
from chatbot.db.database import db
from chatbot.db.models import KnowledgeSource


class KnowledgeManager:
    def __init__(self) -> None:
        persist_directory: str = os.getenv("CHROMA_PERSIST_DIR")

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

    def create_knowledge_source(
            self,
            name: str,
            description: Optional[str] = None
    ) -> Dict[str, any]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        collection_name: str = f"ks_{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"

        self.client.create_collection(
            name=collection_name,
            metadata={"name": name, "description": description or ""}
        )

        knowledge_source = KnowledgeSource(
            name=name,
            description=description,
            collection_name=collection_name
        )
        session.add(knowledge_source)
        session.commit()

        result = {
            "id": knowledge_source.id,
            "name": knowledge_source.name,
            "description": knowledge_source.description,
            "collection_name": knowledge_source.collection_name
        }

        session.close()

        return result

    def add_documents(
            self,
            knowledge_source_id: int,
            documents: List[str],
            metadatas: Optional[List[Dict]] = None
    ) -> int:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        knowledge_source = session.query(KnowledgeSource).filter_by(
            id=knowledge_source_id
        ).first()

        if not knowledge_source:
            session.close()
            raise ValueError(f"Knowledge source {knowledge_source_id} not found")

        collection = self.client.get_collection(knowledge_source.collection_name)

        ids: List[str] = [
            f"doc_{knowledge_source.document_count + i}"
            for i in range(len(documents))
        ]

        # Ensure non-empty metadata for each document
        if metadatas is None:
            metadatas = []
            for i, doc in enumerate(documents):
                metadatas.append({
                    "source": knowledge_source.name,
                    "doc_id": ids[i],
                    "created_at": datetime.now().isoformat()
                })
        else:
            # Ensure all metadata dicts have at least one field
            for i, metadata in enumerate(metadatas):
                if not metadata:
                    metadatas[i] = {
                        "source": knowledge_source.name,
                        "doc_id": ids[i],
                        "created_at": datetime.now().isoformat()
                    }

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        knowledge_source.document_count += len(documents)
        session.commit()
        session.close()

        return len(documents)

    def search(
            self,
            query: str,
            knowledge_source_ids: Optional[List[int]] = None,
            n_results: int = 3
    ) -> List[Tuple[str, float, Dict]]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        if knowledge_source_ids:
            knowledge_sources = session.query(KnowledgeSource).filter(
                KnowledgeSource.id.in_(knowledge_source_ids),
                KnowledgeSource.is_active
            ).all()
        else:
            knowledge_sources = session.query(KnowledgeSource).filter_by(
                is_active=True
            ).all()

        all_results: List[Tuple[str, float, Dict]] = []

        for ks in knowledge_sources:
            try:
                collection = self.client.get_collection(ks.collection_name)
                results = collection.query(
                    query_texts=[query],
                    n_results=min(n_results, ks.document_count or 1)
                )

                if results["documents"] and results["documents"][0]:
                    for doc, distance, metadata in zip(
                            results["documents"][0],
                            results["distances"][0],
                            results["metadatas"][0]
                    ):
                        all_results.append((doc, distance, metadata))
            except Exception as e:
                print(f"Error searching {ks.name}: {str(e)}")

        session.close()

        all_results.sort(key=lambda x: x[1])
        return all_results[:n_results]

    def list_knowledge_sources(self) -> List[Dict[str, any]]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        sources = session.query(KnowledgeSource).filter_by(is_active=True).all()

        result = []
        for source in sources:
            result.append({
                "id": source.id,
                "name": source.name,
                "description": source.description,
                "document_count": source.document_count
            })

        session.close()

        return result

    def update_knowledge_source(
            self,
            knowledge_source_id: int,
            name: Optional[str] = None,
            description: Optional[str] = None,
            is_active: Optional[bool] = None
    ) -> Dict[str, any]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            ks = session.query(KnowledgeSource).filter_by(id=knowledge_source_id).first()

            if not ks:
                raise ValueError(f"Knowledge source {knowledge_source_id} not found")

            if name:
                ks.name = name
            if description is not None:
                ks.description = description
            if is_active is not None:
                ks.is_active = is_active

            session.commit()

            return {
                "id": ks.id,
                "name": ks.name,
                "description": ks.description,
                "is_active": ks.is_active
            }
        finally:
            session.close()

    def delete_knowledge_source(self, knowledge_source_id: int) -> bool:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            ks = session.query(KnowledgeSource).filter_by(id=knowledge_source_id).first()

            if not ks:
                return False

            try:
                self.client.delete_collection(ks.collection_name)
            except:
                raise ValueError(f"Error deleting knowledge source {knowledge_source_id}")

            session.delete(ks)
            session.commit()
            return True
        finally:
            session.close()


knowledge_manager = KnowledgeManager()
