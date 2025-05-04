from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

import os

def load_documents():
    docs = []
    with open("app/data/demo.txt", "r") as f:
        text = f.read()
        docs.append(Document(page_content=text))
    return docs

def split_documents(docs, chunk_size=500, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)

def embed_and_save(docs, persist_path="vectorstore"):
    os.makedirs(persist_path, exist_ok=True)
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(docs, embedding_model)
    vectordb.save_local(persist_path)

if __name__ == "__main__":
    raw_docs = load_documents()
    chunks = split_documents(raw_docs)
    embed_and_save(chunks)
    print("✅ Vector store created and saved.")
