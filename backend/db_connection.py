import psycopg2
import os
from dotenv import load_dotenv
from gemini_models import embedd_query
load_dotenv()
def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def store_chunk(id:str,source_document: str, content: str, embedding: list[float]):
    """Insert one chunk + its embedding into knowledge_chunks."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO knowledge_base (id, source, content, embedding)
        VALUES (%s, %s, %s, %s)
        """,
        (id, source_document, content, embedding)
    )
    conn.commit()
    cur.close()
    conn.close()


def retrive_content():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id,content from knowledge_base")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieve_embedding(question: str, top_k: int = 30):
    """Embed the question and find the top_k most similar chunks."""
    query_vector = embedd_query(question)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, source, content,
               embedding <=> %s::vector AS distance
        FROM knowledge_base
        ORDER BY distance
        LIMIT %s
        """,
        (query_vector, top_k)
    )
    rows = cur.fetchall()
    ids=[r[0] for r in rows]
    cur.close()
    conn.close()
    return ids