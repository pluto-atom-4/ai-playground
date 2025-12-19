"""Embeddings module for semantic similarity using ChromaDB and Transformers."""

from typing import Optional


class EmbeddingsManager:
    """
    Manages text embeddings and semantic similarity using ChromaDB.

    Uses Hugging Face Transformers to generate embeddings and stores them
    in ChromaDB for efficient semantic search.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        """
        Initialize the embeddings manager.

        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        self._embedder = None
        self._client = None

    @property
    def embedder(self):
        """Lazy load the embedding model."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._embedder = SentenceTransformer(self.model_name)
            except ImportError as e:
                raise ImportError(
                    "sentence-transformers is required for embeddings"
                ) from e
        return self._embedder

    @property
    def client(self):
        """Lazy load ChromaDB client."""
        if self._client is None:
            try:
                import chromadb

                self._client = chromadb.Client()
            except ImportError as e:
                raise ImportError("chromadb is required for storing embeddings") from e
        return self._client

    def generate_embeddings(self, texts: list[str]) -> list:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        embeddings = self.embedder.encode(texts)
        return embeddings.tolist()

    def store_embeddings(
        self, collection_name: str, texts: list[str], ids: list[str], metadata: Optional[list] = None
    ) -> None:
        """
        Store embeddings in ChromaDB.

        Args:
            collection_name: Name of the collection to store embeddings
            texts: List of text strings
            ids: List of unique IDs for each text
            metadata: Optional list of metadata dictionaries
        """
        collection = self.client.get_or_create_collection(name=collection_name)
        embeddings = self.generate_embeddings(texts)
        collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadata)

    def search_similar(
        self,
        collection_name: str,
        query_text: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search for similar texts in a collection.

        Args:
            collection_name: Name of the collection to search
            query_text: Query text to find similar documents
            top_k: Number of top results to return

        Returns:
            List of similar documents with scores
        """
        collection = self.client.get_collection(name=collection_name)
        results = collection.query(query_texts=[query_text], n_results=top_k)

        # Format results
        similar_items = []
        for idx, doc_id in enumerate(results["ids"][0]):
            similar_items.append(
                {
                    "id": doc_id,
                    "document": results["documents"][0][idx],
                    "distance": results["distances"][0][idx],
                    "metadata": results["metadatas"][0][idx] if results["metadatas"] else None,
                }
            )

        return similar_items

    def semantic_match_score(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity score between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError as e:
            raise ImportError("scikit-learn is required for similarity calculation") from e

        embedding1 = self.embedder.encode([text1])
        embedding2 = self.embedder.encode([text2])
        similarity = cosine_similarity(embedding1, embedding2)[0][0]

        return float(similarity)

