import chromadb
chroma_client = chromadb.PersistentClient(path="agri_knowledge_db")
collection = chroma_client.get_or_create_collection(name="nepal_krishi_knowledge")
