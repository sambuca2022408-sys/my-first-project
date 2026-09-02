from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

COLLECTION_NAME = "agri_docs_nepal"
qdrant = QdrantClient(host="localhost", port=6333)

def simple_embed(text):
    vec = [0.0] * 384
    for word in text.lower().split():
        hash_val = hash(word) % 384
        vec[hash_val] += 1.0
    total = sum([x*x for x in vec]) ** 0.5
    if total > 0:
        vec = [x/total for x in vec]
    return vec

print("Agri Bot Ready. 'exit' lekhda banda hunchha.\n")

while True:
    query = input("Timi: ")
    if query.lower() == 'exit': break
    
    query_vector = simple_embed(query)
    
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=3
    )

    print("\nBot: Yo jankari maile Norms Book 2080 bata paye:")
    for res in results:
        print(f"\n- Page {res.payload['page']}: {res.payload['text'][:300]}...")
    print("\n" + "-"*40)