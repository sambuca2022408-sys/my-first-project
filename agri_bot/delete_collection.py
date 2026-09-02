import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

# Connect to Qdrant
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

COLLECTION_NAME = "agri_docs_nepal"

# Delete the old collection
qdrant.delete_collection(collection_name=COLLECTION_NAME)
print(f"✅ Collection '{COLLECTION_NAME}' deleted successfully")
print("Now run: py load_pdf.py to upload again")