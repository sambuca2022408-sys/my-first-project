from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from fastembed import TextEmbedding
import fitz
import uuid

PDF_PATH = "KrishiBook.pdf"
COLLECTION_NAME = "krishi_book"

client = QdrantClient(host="localhost", port=6333)
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

doc = fitz.open(PDF_PATH)
points = []

print("Uploading started...")
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text = page.get_text("text")
    if text.strip():
        embeddings = list(model.embed([text]))
        vector = embeddings[0].tolist()
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": text, "page": page_num+1}
        ))
    print(f"Processing page {page_num+1}/{len(doc)}")

client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"Done! Uploaded {len(points)} pages to Qdrant")