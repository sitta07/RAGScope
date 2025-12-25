import os
import shutil
import numpy as np
import pandas as pd
import umap.umap_ as umap
from tqdm import tqdm
from uuid import uuid4

# LangChain Imports
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Configuration
DATA_PATH = "./data"
DB_PATH = "./processed_data/chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# 1. Setup Embeddings 
print("Initializing Embedding Model...")
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def load_documents():
    """Load documents from data folder"""
    print(f"📂 Loading documents from {DATA_PATH}...")
    
    # รองรับทั้ง txt และ pdf
    loaders = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader
    }
    
    docs = []
    for filename in os.listdir(DATA_PATH):
        ext = os.path.splitext(filename)[1]
        if ext in loaders:
            loader = loaders[ext](os.path.join(DATA_PATH, filename))
            loaded_docs = loader.load()
            # เพิ่มชื่อไฟล์เป็น metadata เพื่อใช้ filter ภายหลัง
            for doc in loaded_docs:
                doc.metadata["source_doc"] = filename
            docs.extend(loaded_docs)
            print(f"   - Loaded: {filename}")
            
    return docs

def process_chunks(documents):
    print("Splitting documents...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"   - Generated {len(chunks)} chunks.")
    return chunks

def compute_umap_coords(embeddings):
    """
    ลดมิติของ Vector จาก 384 dimensions -> 2 dimensions (x, y)
    เพื่อนำไปพล็อตลง Scatter Plot
    """
    print("Computing UMAP 2D projections (Pre-calculation)...")
    
    reducer = umap.UMAP(
        n_neighbors=15,
        n_components=2,
        metric='cosine',
        random_state=42 # Fix seed เพื่อให้ผลเหมือนเดิมทุกครั้ง
    )
    
    # แปลง List of Vectors เป็น Numpy Array
    embeddings_array = np.array(embeddings)
    
    # Fit และ Transform
    umap_coords = reducer.fit_transform(embeddings_array)
    
    return umap_coords

def main():
    # Clear DB เก่าทิ้งก่อน (Idempotency)
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        
    # 1. Load Data
    raw_docs = load_documents()
    if not raw_docs:
        print("❌ No documents found in data/ folder!")
        return

    # 2. Chunking
    chunks = process_chunks(raw_docs)
    
    # 3. Generate Embeddings for ALL chunks
    print("Generating Embeddings...")
    # ดึงเฉพาะ Text ออกมาทำ Embedding
    chunk_texts = [doc.page_content for doc in chunks]
    embeddings = embedding_model.embed_documents(chunk_texts)
    
    # 4. Pre-compute Visualization Coordinates
    umap_coords = compute_umap_coords(embeddings)
    
    # 5. Save to ChromaDB with Metadata
    print("💾 Saving to Persistent Vector DB...")
    
    # เตรียม Client แบบ Persistent
    vector_db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_model,
        collection_name="rag_demo"
    )
    
    # เตรียมข้อมูลที่จะ add เข้า DB
    ids = [str(uuid4()) for _ in range(len(chunks))]
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        meta = chunk.metadata.copy()
        # Add UMAP coordinates to metadata
        meta["umap_x"] = float(umap_coords[i][0])
        meta["umap_y"] = float(umap_coords[i][1])
        metadatas.append(meta)

    # Add to Chroma (Batch processing is handled by Langchain usually, but direct add is fine for small data)
    BATCH_SIZE = 100
    total_batches = len(chunks) // BATCH_SIZE + 1
    
    for i in tqdm(range(total_batches), desc="Upserting to DB"):
        start = i * BATCH_SIZE
        end = start + BATCH_SIZE
        if start >= len(chunks): break
        
        vector_db.add_texts(
            texts=chunk_texts[start:end],
            metadatas=metadatas[start:end],
            ids=ids[start:end]
        )
        
    print(f"✅ Success! Ingested {len(chunks)} chunks into {DB_PATH}")
    print("➡️ Next Step: Build the Streamlit App to visualize this.")

if __name__ == "__main__":
    main()