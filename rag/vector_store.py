"""
PostgreSQL pgvector Semantic Search and Relational Retrieval Store for KrishiMitra AI.
Performs cosine similarity vector matching over extracted government document passages
and joins with schemes, benefits, eligibility, and official URLs.
"""

from typing import List, Dict, Any, Optional
from rag.embeddings import EmbeddingGenerator
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.rag.vector_store")

class VectorStore:
    def __init__(self, embedding_gen: Optional[EmbeddingGenerator] = None):
        self.embedding_gen = embedding_gen or EmbeddingGenerator()

    def search_similar_passages(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Embeds user query and searches PostgreSQL using cosine distance operator `<=>`
        on extracted_document_content, joining with schemes and documents.
        """
        logger.info(f"Executing semantic vector search for query: '{query}'")
        query_vec = self.embedding_gen.generate_embedding(query)
        vec_str = "[" + ",".join(f"{x:.6f}" for x in query_vec) + "]"

        results = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Semantic search with pgvector + relational join
                    cur.execute(
                        """
                        SELECT
                            c.id as chunk_id,
                            c.document_id,
                            c.page_number,
                            c.content_text,
                            d.title as document_title,
                            d.original_url as document_url,
                            d.verification_status,
                            s.id as scheme_id,
                            s.name as scheme_name,
                            s.classification,
                            s.official_portal_url,
                            s.last_verified_at as scheme_verified_at
                        FROM extracted_document_content c
                        JOIN scheme_documents d ON c.document_id = d.id
                        LEFT JOIN schemes s ON c.scheme_id = s.id OR d.scheme_id = s.id
                        WHERE c.embedding IS NOT NULL
                        ORDER BY c.embedding <=> %s::vector
                        LIMIT %s;
                        """,
                        (vec_str, top_k)
                    )
                    rows = cur.fetchall()
                    for r in rows:
                        results.append(dict(r))

        except Exception as e:
            logger.warning(f"Vector search exception (falling back to full-text search): {e}")
            results = self._fallback_fulltext_search(query, top_k)

        # If vector search returned 0 results (e.g. embeddings not populated yet), fall back to keyword search
        if not results:
            results = self._fallback_fulltext_search(query, top_k)

        logger.info(f"Retrieved {len(results)} relevant passages for query.")
        return results

    def _fallback_fulltext_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Keyword and ILIKE search fallback across schemes and passages."""
        results = []
        terms = [t for t in query.lower().split() if len(t) > 3]
        if not terms:
            terms = [query.lower()]

        pattern = f"%{terms[0]}%"
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            s.id as scheme_id,
                            s.name as scheme_name,
                            s.classification,
                            s.description as content_text,
                            s.official_portal_url,
                            s.last_verified_at as scheme_verified_at,
                            d.id as document_id,
                            d.title as document_title,
                            d.original_url as document_url,
                            1 as page_number
                        FROM schemes s
                        LEFT JOIN scheme_documents d ON s.id = d.scheme_id
                        WHERE LOWER(s.name) LIKE %s OR LOWER(s.description) LIKE %s
                        LIMIT %s;
                        """,
                        (pattern, pattern, top_k)
                    )
                    rows = cur.fetchall()
                    for r in rows:
                        results.append(dict(r))
        except Exception as e:
            logger.error(f"Fallback fulltext search error: {e}")
        return results
