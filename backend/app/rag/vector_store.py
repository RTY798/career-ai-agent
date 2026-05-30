"""ChromaDB 向量数据库封装"""

import os
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


class VectorStore:
    """ChromaDB 向量数据库封装（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        persist_dir = settings.chroma_persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, documents: list[str], metadatas: Optional[list[dict]] = None):
        """添加文档到向量库"""
        ids = [f"doc_{i}" for i in range(len(documents))]
        self._collection.add(
            documents=documents,
            metadatas=metadatas or [{}] * len(documents),
            ids=ids,
        )

    def similarity_search(self, query: str, k: int = 5) -> list[dict]:
        """向量相似度检索"""
        results = self._collection.query(query_texts=[query], n_results=k)
        docs = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                docs.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": 1 - (results["distances"][0][i] if results["distances"] else 0),
                })
        return docs

    def count(self) -> int:
        return self._collection.count()

    def delete_all(self):
        """清空集合（用于重新 seeding）"""
        self._client.delete_collection(settings.chroma_collection_name)
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
        )


vector_store = VectorStore()
