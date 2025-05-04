from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# === STEP 1: Load all 3 PDFs ===
filenames = [
    "./data/Dementia_World_Health_Organization.pdf",
    "./data/Dementia- Information for caregivers_World_Health_Organization.pdf",
    "./data/Expert Q&A- Dementia and Alzheimer's Disease_World_Health_Organization.pdf"
]

all_docs = []
for file in filenames:
    loader = PyPDFLoader(file)
    docs = loader.load()
    all_docs.extend(docs)

print(f"✅ Loaded {len(all_docs)} raw pages from {len(filenames)} PDFs")

# === STEP 2: Chunk the text ===
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(all_docs)
print(f"✅ Rechunked into {len(chunks)} chunks")

# === STEP 3: Embed and save to FAISS ===
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embedding_model)
vectorstore.save_local("vectorstore")
print("✅ FAISS vectorstore saved to 'vectorstore/'")
