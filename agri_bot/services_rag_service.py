from qdrant_client import QdrantClient
from qdrant_client.models import Filter

client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "krishi_books"

def load_krishi_book(pdf_path):
    # This function is actually in load_pdf.py, so we leave this empty
    pass

def search_chunks(query_vector, top_k=3):
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return [hit.payload["text"] for hit in results]