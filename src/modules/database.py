import os
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from .config import DB_PATH, EMBEDDING_MODEL, DATA_FOLDER

@st.cache_resource
def load_vector_db(collection_name):
    """Load ChromaDB with caching to speed up reload."""
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run ingest.py first.")
    return Chroma(persist_directory=DB_PATH, embedding_function=embedding_function, collection_name=collection_name)

def get_full_file_content(filename):
    """Read full text file from disk (Real I/O)."""
    path = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "[Error: File not found]"

def get_file_list():
    """List all .txt files in data folder."""
    if os.path.exists(DATA_FOLDER):
        return [f for f in os.listdir(DATA_FOLDER) if f.endswith(".txt")]
    return []