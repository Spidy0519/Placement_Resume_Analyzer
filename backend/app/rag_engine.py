# app/rag_engine.py
# -------------------------------------------------------
# RAG Layer: Embeds resume chunks + compares with
# ideal resume format using pure NumPy similarity
# (Removed FAISS to avoid Windows DLL issues)
# -------------------------------------------------------

import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from app.keywords_config import IDEAL_RESUME_FORMAT

logger = logging.getLogger(__name__)

# Cache model and knowledge base
_model = None
_kb_cache = None

def get_embedding_model():
    global _model
    if _model is None:
        try:
            # Small, fast model - good for local use
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
            raise
    return _model


def build_knowledge_base() -> tuple:
    """
    Build knowledge base from ideal resume format.
    Returns: (ideal_embeddings, ideal_chunks)
    """
    global _kb_cache
    if _kb_cache is not None:
        return _kb_cache

    model = get_embedding_model()

    # Split ideal format into chunks
    ideal_chunks = [
        chunk.strip()
        for chunk in IDEAL_RESUME_FORMAT.split("\n\n")
        if chunk.strip() and len(chunk.strip()) > 20
    ]

    # Embed ideal chunks
    ideal_embeddings = model.encode(ideal_chunks, convert_to_numpy=True)
    ideal_embeddings = ideal_embeddings.astype("float32")

    # Normalize for cosine similarity: v / ||v||
    norms = np.linalg.norm(ideal_embeddings, axis=1, keepdims=True)
    ideal_embeddings = ideal_embeddings / (norms + 1e-10)

    _kb_cache = (ideal_embeddings, ideal_chunks)
    return _kb_cache


def compute_rag_similarity(resume_chunks: list[str], top_k: int = 3) -> dict:
    """
    Compare resume chunks against ideal resume knowledge base.
    Returns similarity scores and matched sections.
    """
    try:
        model = get_embedding_model()
        ideal_embeddings, ideal_chunks = build_knowledge_base()

        if not resume_chunks:
            return {"rag_similarity_score": 0, "rag_grade": "N/A", "potential_gaps": []}

        # Embed resume chunks
        resume_embeddings = model.encode(resume_chunks, convert_to_numpy=True)
        resume_embeddings = resume_embeddings.astype("float32")
        
        # Normalize resume embeddings
        r_norms = np.linalg.norm(resume_embeddings, axis=1, keepdims=True)
        resume_embeddings = resume_embeddings / (r_norms + 1e-10)

        # Compute Cosine Similarity using Dot Product (since both are unit vectors)
        # Resulting shape: (num_resume_chunks, num_ideal_chunks)
        similarity_matrix = np.dot(resume_embeddings, ideal_embeddings.T)

        all_scores = []
        matched_pairs = []

        for i in range(len(resume_chunks)):
            # Get top scores for this resume chunk
            chunk_similarities = similarity_matrix[i]
            top_indices = np.argsort(chunk_similarities)[-top_k:][::-1]
            
            top_score = float(chunk_similarities[top_indices[0]])
            avg_top_score = float(np.mean(chunk_similarities[top_indices]))
            
            all_scores.append(avg_top_score)

            # Store best match for first few resume chunks
            if i < 5:
                best_ideal_idx = top_indices[0]
                best_ideal = ideal_chunks[best_ideal_idx]
                matched_pairs.append({
                    "resume_chunk": resume_chunks[i][:150] + "..." if len(resume_chunks[i]) > 150 else resume_chunks[i],
                    "best_match_ideal": best_ideal[:200] + "..." if len(best_ideal) > 200 else best_ideal,
                    "similarity_score": round(top_score, 3)
                })

        # Overall RAG similarity score (0-100)
        overall_similarity = float(np.mean(all_scores)) * 100

        # Find potential gaps (bottom 25% percentile)
        gap_chunks = []
        if len(all_scores) > 0:
            threshold = np.percentile(all_scores, 25)
            gap_chunks = [
                resume_chunks[i][:100]
                for i, score in enumerate(all_scores)
                if score <= threshold
            ][:5]

        return {
            "rag_similarity_score": round(overall_similarity, 1),
            "rag_grade": get_rag_grade(overall_similarity),
            "top_matches": matched_pairs,
            "potential_gaps": gap_chunks,
            "interpretation": interpret_rag_score(overall_similarity)
        }
    except Exception as e:
        logger.error(f"RAG similarity computation failed: {e}")
        return {
            "rag_similarity_score": 0,
            "rag_grade": "Error",
            "error": str(e),
            "interpretation": "RAG analysis failed due to system error."
        }


def get_rag_grade(score: float) -> str:
    if score >= 70: return "Highly Aligned"
    if score >= 50: return "Moderately Aligned"
    if score >= 30: return "Partially Aligned"
    return "Needs Major Improvement"


def interpret_rag_score(score: float) -> str:
    if score >= 70: return "Your resume structure closely follows best practices."
    if score >= 50: return "Your resume is reasonably well structured but has room for improvement."
    if score >= 30: return "Several sections are missing or poorly structured compared to ideal format."
    return "Resume needs significant restructuring. Consider rebuilding from a strong template."
