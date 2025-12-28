import streamlit as st
import os
import time
import pandas as pd

# --- Import เฉพาะส่วนที่จำเป็นจริงๆ ---
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Constants
DB_PATH = "./processed_data/chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

@st.cache_resource
def load_vector_db():
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return Chroma(persist_directory=DB_PATH, embedding_function=embedding_function, collection_name="rag_demo")

@st.cache_resource
def get_all_documents_metadata(_vector_db):
    data = _vector_db.get(include=["metadatas"])
    return pd.DataFrame(data['metadatas'])

def get_llm(api_key):
    if not api_key: return None
    return ChatGroq(groq_api_key=api_key, model_name="llama3-70b-8192", temperature=0.0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def perform_rag(query, vector_db, llm, strategy="basic"):
    start_time = time.time()
    
    # Setup Retriever
    if strategy == "advanced":
        retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 3})
    else:
        retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    # ดึงเอกสารมาก่อนเพื่อนำไปแสดงผลใน UI
    docs = retriever.invoke(query)
    
    if not llm:
        return "N/A (No API Key)", docs, time.time() - start_time

    # --- LCEL Implementation (The Senior Move 🛠️) ---
    template = """Answer the question based only on the following context:
    {context}
    
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # สร้าง Chain ด้วยเครื่องหมาย | (Pipe)
    # วิธีนี้ไม่ต้อง import langchain.chains เลย!
    rag_chain = (
        {"context": lambda x: format_docs(docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # รัน Chain
    answer = rag_chain.invoke(query)
    
    latency = time.time() - start_time
    return answer, docs, latency