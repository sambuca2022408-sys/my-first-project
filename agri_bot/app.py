import os
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding
import uuid

app = FastAPI(title="Krishi WhatsApp Bot")

# MODEL FOR REQUEST BODY
class Message(BaseModel):
    message: str

# USE RAILWAY ENV VARS - WORKS LOCALLY TOO
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "krishi_book"

print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

# CREATE COLLECTION IF NOT EXISTS
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print(f"Collection {COLLECTION_NAME} created")

# FUNCTION 1: ANSWER QUESTIONS
async def answer_question(question: str):
    embeddings = list(model.embed([question]))
    query_vector = embeddings[0].tolist()

    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    ).points

    if not search_result:
        return "Maile book ma tyo jankari fela parena. Kripaya arko prashna sodhnuhos."

    context = "\n---\n".join([hit.payload["text"] for hit in search_result])
    return f"Timro prashna: {question}\n\nBook bata payeko jankari:\n{context}"

# FUNCTION 2: UPLOAD BOOK DATA - USE THIS ONCE TO LOAD YOUR BOOK
@app.post("/upload")
async def upload_text(data: dict):
    """
    Send JSON like: {"texts": ["Chapter 1 text...", "Chapter 2 text..."]}
    """
    texts = data.get("texts", [])
    if not texts:
        return {"error": "No texts provided"}

    embeddings = list(model.embed(texts))

    points = []
    for i, (text, embedding) in enumerate(zip(texts, embeddings)):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload={"text": text}
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"status": f"{len(texts)} chunks uploaded to {COLLECTION_NAME}"}

# FUNCTION 3: WHATSAPP WEBHOOK
@app.post("/webhook")
async def webhook(data: Message):
    user_message = data.message
    result = await answer_question(user_message)
    return {"answer": result}

# FUNCTION 4: HEALTH CHECK
@app.get("/")
def root():
    count = client.count(collection_name=COLLECTION_NAME).count
    return {
        "message": "Krishi Bot is running",
        "documents_in_db": count
    }