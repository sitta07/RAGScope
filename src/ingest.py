import os
import shutil
import uuid
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --- Configuration ---
DATA_PATH = "./data"
DB_PATH = "./processed_data/chroma_db"
COLLECTION_NAME = "harry_potter_lore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def main():
    print("🚀 Starting Ingestion (Real Parent-Document Setup)...")
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: {DATA_PATH} not found.")
        return

    loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"📂 Loaded {len(documents)} files.")

    # 2. Chunking (Small chunks for precise retrieval)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)

    # 3. Add Metadata for Parent Retrieval
    # เราจะเก็บ 'source_doc' ไว้ เพื่อให้ระบบรู้ว่า Chunk นี้มาจากไฟล์ไหน
    # เวลาทำ Parent-Document เราจะย้อนไปอ่านไฟล์เต็มจาก Disk
    for chunk in chunks:
        filename = os.path.basename(chunk.metadata.get('source', ''))
        chunk.metadata['source_doc'] = filename
        chunk.metadata['chunk_id'] = str(uuid.uuid4())

    print(f"🧩 Split into {len(chunks)} chunks.")

    # 4. Save to Chroma
    # Clear old DB for safety (Optional, be careful in prod)
    # if os.path.exists(DB_PATH): shutil.rmtree(DB_PATH)

    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_function,
        collection_name=COLLECTION_NAME
    )
    
    vector_db.add_documents(chunks)
    print(f"✅ Ingestion Complete! Data saved to {COLLECTION_NAME}")

if __name__ == "__main__":
    main()