from sqlalchemy.orm import Session

from app.services.hybrid_search_service import hybrid_search
from app.services.llm_service import generate_answer


NO_DOCUMENTATION_MESSAGE = "No documentation is available for this question."


def answer_question(
    db: Session,
    question: str,
    team: str,
) -> dict:
    results = hybrid_search(
        db=db,
        query=question,
        team=team,
        limit=5,
    )

    if not results:
        return {
            "answer": NO_DOCUMENTATION_MESSAGE,
            "sources": [],
        }

    context_parts = []
    sources = []

    for result in results:
        chunk = result["chunk"]

        context_parts.append(chunk.content)

        sources.append(
            {
                "document_id": chunk.document_id,
                "filename": chunk.document.filename, 
                "chunk_index": chunk.chunk_index,
            }
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are AtlasIQ, an enterprise knowledge assistant.

Answer the user's question using ONLY the documentation provided below.

If the documentation does not contain enough information to answer,
respond exactly:

{NO_DOCUMENTATION_MESSAGE}

DOCUMENTATION:
{context}

QUESTION:
{question}

ANSWER:
"""

    answer = generate_answer(prompt).strip()

    if answer == NO_DOCUMENTATION_MESSAGE:
        return {
            "answer": answer,
            "sources": [],
        }

    return {
        "answer": answer,
        "sources": sources,
    }
