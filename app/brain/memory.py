import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings

class MemoryBank:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.emb_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="argus_logs",
            embedding_function=self.emb_fn
        )

    def store(self, text: str, meta: dict):
        self.collection.add(
            documents=[text],
            metadatas=[meta],
            ids=[f"{meta['source']}_{meta['timestamp']}"]
        )

    def recall(self, query: str, n=3):
        results = self.collection.query(query_texts=[query], n_results=n)
        return results["documents"][0] if results["documents"] else []