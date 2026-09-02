from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from fastembed import TextEmbedding

app = FastAPI(title="Krishi WhatsApp Bot")

# MODEL FOR REQUEST BODY
class Message(BaseModel):
    message: str

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "krishi_book"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

async def answer_question(question: str):
    embeddings = list(model.embed([question]))
    query_vector = embeddings[0].tolist()

    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    ).points

    if not search_result:
        return "Maile book ma tyo jankari fela parena."

    context = "\n---\n".join([hit.payload["text"] for hit in search_result])
    return f"Timro prashna: {question}\n\nBook bata payeko jankari:\n{context}"

@app.post("/webhook")
async def webhook(data: Message): # Request body ko lagi yo line
    user_message = data.message
    result = await answer_question(user_message)
    return {"answer": result}

@app.get("/")
def root():
    return {"message": "Krishi Bot is running"}