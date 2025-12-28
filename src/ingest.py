import os
import shutil
import numpy as np
import pandas as pd
import umap
from tqdm import tqdm
from uuid import uuid4

# LangChain & Chroma Stack
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# --- Configuration ---
# 🔥 ปรับ Path ให้ตรงกับโฟลเดอร์ Harry Potter ที่เราสร้าง
DATA_PATH = "./data"
DB_PATH = "./processed_data/chroma_db"
COLLECTION_NAME = "harry_potter_lore" # ตั้งชื่อให้ชัดเจน แยกจากโปรเจกต์อื่น
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# 1. Setup Embeddings 
print(f"🔮 Initializing Embedding Model ({EMBEDDING_MODEL_NAME})...")
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def load_documents():
    """Load documents from data folder"""
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Folder '{DATA_PATH}' not found. Please create it and add .txt files.")
        return []

    print(f"📂 Loading documents from {DATA_PATH}...")
    
    loaders = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader
    }
    
    docs = []
    # วนลูปอ่านไฟล์ในโฟลเดอร์
    for filename in os.listdir(DATA_PATH):
        ext = os.path.splitext(filename)[1]
        if ext in loaders:
            try:
                loader = loaders[ext](os.path.join(DATA_PATH, filename))
                loaded_docs = loader.load()
                # เพิ่มชื่อไฟล์เป็น metadata เพื่อใช้ filter/โชว์ใน UI
                for doc in loaded_docs:
                    doc.metadata["source_doc"] = filename
                docs.extend(loaded_docs)
                print(f"   - ✅ Loaded: {filename}")
            except Exception as e:
                print(f"   - ⚠️ Failed to load {filename}: {e}")
            
    return docs

def process_chunks(documents):
    print("⚔️ Splitting documents into chunks...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,      # ขนาดกำลังดีสำหรับ Lore
        chunk_overlap=100,   # กันข้อความขาดตอน
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"   - Generated {len(chunks)} magical chunks.")
    return chunks

def compute_umap_coords(embeddings):
    """
    ลดมิติ Vector (384) -> 2D (x,y) สำหรับ Plot Graph
    """
    print("🗺️ Computing UMAP 2D projections...")
    
    # Safety Check: UMAP ต้องการข้อมูลจำนวนหนึ่ง ถ้าข้อมูลน้อยกว่า n_neighbors จะ error
    n_samples = len(embeddings)
    n_neighbors = 15
    
    if n_samples <= 15:
        n_neighbors = max(2, n_samples - 1)
        print(f"   - ⚠️ Data is small ({n_samples}), adjusting n_neighbors to {n_neighbors}")

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=2,
        metric='cosine',
        random_state=42 # Fix seed ให้กราฟหน้าตาเหมือนเดิมทุกครั้ง
    )
    
    embeddings_array = np.array(embeddings)
    umap_coords = reducer.fit_transform(embeddings_array)
    
    return umap_coords

def main():
    # Clear DB เก่าเฉพาะ Collection นี้ (ถ้าทำได้) แต่ Chroma แบบ Local ลบโฟลเดอร์ง่ายกว่า
    # ในที่นี้เราจะลบ DB_PATH ทิ้งเพื่อ Clean Start (ระวังถ้ามี Collection อื่นรวมอยู่)
    # แต่เพื่อความชัวร์ใน Demo นี้ เราจะถือว่า folder นี้มีแค่โปรเจกต์เรา
    # if os.path.exists(DB_PATH):
    #     shutil.rmtree(DB_PATH)
    #     print("🧹 Cleared old database.")

    # 1. Load Data
    raw_docs = load_documents()
    if not raw_docs:
        return

    # 2. Chunking
    chunks = process_chunks(raw_docs)
    if not chunks:
        print("❌ No chunks created.")
        return
    
    # 3. Generate Embeddings for ALL chunks
    print("🧠 Generating Embeddings (Focusing logic)...")
    chunk_texts = [doc.page_content for doc in chunks]
    embeddings = embedding_model.embed_documents(chunk_texts)
    
    # 4. Pre-compute Visualization Coordinates (UMAP)
    umap_coords = compute_umap_coords(embeddings)
    
    # 5. Save to ChromaDB with Metadata
    print(f"💾 Saving to Vector DB (Collection: {COLLECTION_NAME})...")
    
    # เตรียม Client
    vector_db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_model,
        collection_name=COLLECTION_NAME
    )
    
    # เตรียม Data สำหรับ Upsert
    ids = [str(uuid4()) for _ in range(len(chunks))]
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        meta = chunk.metadata.copy()
        # Add UMAP coordinates to metadata (สำคัญมากสำหรับหน้าเว็บ)
        meta["umap_x"] = float(umap_coords[i][0])
        meta["umap_y"] = float(umap_coords[i][1])
        metadatas.append(meta)

    # Batch Upsert (เพื่อความเร็วและเสถียร)
    BATCH_SIZE = 100
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in tqdm(range(total_batches), desc="Upserting chunks"):
        start = i * BATCH_SIZE
        end = start + BATCH_SIZE
        
        batch_texts = chunk_texts[start:end]
        batch_metadatas = metadatas[start:end]
        batch_ids = ids[start:end]
        
        vector_db.add_texts(
            texts=batch_texts,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        
    print(f"✅ Mischief Managed! Ingested {len(chunks)} chunks into {DB_PATH}")
    print("➡️ Ready to run app.py")

if __name__ == "__main__":
    main()