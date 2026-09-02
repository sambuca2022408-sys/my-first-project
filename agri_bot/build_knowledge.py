from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbeddings

print("Reading data/output_nepali.txt...")
with open("data/output_nepali.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = splitter.create_documents([text])

print("Building brain with AI embeddings... this takes 1-2 min")
embeddings = FastEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
db = FAISS.from_documents(docs, embeddings)
db.save_local("faiss_index")

print("Brain built! Saved to faiss_index folder. Total chunks:", len(docs))