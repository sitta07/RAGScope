import os
import sys
import uuid

# Fix path to allow importing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from modules.config import DATA_FOLDER, DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL

def main():
    print("🚀 Starting Ingestion...")
    
    if not os.path.exists(DATA_FOLDER):
        print(f"❌ Error: {DATA_FOLDER} not found.")
        return

    # Load
    loader = DirectoryLoader(DATA_FOLDER, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"📂 Loaded {len(documents)} files.")

    # Chunk
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    
    # Metadata for Parent-Doc
    for chunk in chunks:
        chunk.metadata['source_doc'] = os.path.basename(chunk.metadata.get('source', ''))
        chunk.metadata['chunk_id'] = str(uuid.uuid4())

    print(f"✂️ Created {len(chunks)} chunks.")

    # Save
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function, collection_name=COLLECTION_NAME)
    
    # Batch add
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        vector_db.add_documents(chunks[i:i + batch_size])
        
    print("✅ Ingestion Complete!")

if __name__ == "__main__":
    main()