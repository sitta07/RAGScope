import streamlit as st
import os
import time
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Constants
DB_PATH = "./processed_data/chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

@st.cache_resource
def load_vector_db():
    print("🔄 Loading Vector DB...")
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    vector_db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_function,
        collection_name="rag_demo"
    )
    return vector_db

@st.cache_resource
def get_all_documents_metadata(_vector_db):
    """
    ดึง Metadata ทั้งหมด (x, y, source) เพื่อนำไป plot ลงกราฟ
    โดยไม่ดึง Vector (เพื่อประหยัด RAM)
    """
    data = _vector_db.get(include=["metadatas"])
    df = pd.DataFrame(data['metadatas'])
    return df

def get_llm(api_key):
    """Initialize Groq LLM (Llama3-70b)"""
    if not api_key:
        return None
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama3-70b-8192",
        temperature=0.0
    )

def perform_rag(query, vector_db, llm, strategy="basic"):
    """
    ฟังก์ชัน RAG แบบเลือก Strategy ได้
    - Basic: Similarity Search ธรรมดา
    - Advanced: MMR (Maximal Marginal Relevance) เพื่อลดความซ้ำซ้อนของข้อมูล
    """
    start_time = time.time()
    
    # 1. Retrieval Strategy
    if strategy == "advanced":
        # MMR ช่วยหาข้อมูลที่หลากหลาย ไม่กระจุกตัว
        retriever = vector_db.as_retriever(
            search_type="mmr", 
            search_kwargs={"k": 4, "fetch_k": 10, "lambda_mult": 0.5}
        )
    else:
        # Basic Similarity Search
        retriever = vector_db.as_retriever(search_kwargs={"k": 4})
        
    # 2. Get Documents
    docs = retriever.invoke(query)
    
    # 3. Generation (ถ้ามี LLM)
    answer = "N/A (No API Key)"
    if llm:
        # Simple Prompt
        template = """Answer the question based only on the context below. 
        If you don't know, say "I don't know". Keep it professional.
        
        Context: {context}
        
        Question: {question}
        """
        prompt = PromptTemplate.from_template(template)
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        # Run Chain
        result = chain.invoke({"query": query})
        answer = result['result']
        docs = result['source_documents'] # Update docs from chain result
        
    latency = time.time() - start_time
    return answer, docs, latency