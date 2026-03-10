import os
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from .config import DB_PATH, EMBEDDING_MODEL, DATA_FOLDER


# -----------------------------
# EMBEDDING (cached)
# -----------------------------
@st.cache_resource
def get_embedding():
    """
    Load embedding model only once.
    Prevents Streamlit from reloading the model every refresh.
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# -----------------------------
# VECTOR DATABASE
# -----------------------------
@st.cache_resource
def load_vector_db(collection_name: str):
    """
    Load Chroma vector database with caching.
    """

    embedding_function = get_embedding()

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. "
            "Run ingest.py first to create the vector database."
        )

    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_function,
        collection_name=collection_name
    )


# -----------------------------
# FILE READING
# -----------------------------
def get_full_file_content(filename: str):
    """
    Read full text file from disk.
    """

    os.makedirs(DATA_FOLDER, exist_ok=True)

    path = os.path.join(DATA_FOLDER, filename)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    return "[Error: File not found]"


# -----------------------------
# FILE LIST
# -----------------------------
def get_file_list():
    """
    Return all .txt files in the data folder.
    """

    os.makedirs(DATA_FOLDER, exist_ok=True)

    files = [
        f for f in os.listdir(DATA_FOLDER)
        if f.endswith(".txt")
    ]

    return files