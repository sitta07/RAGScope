import streamlit as st
import os
import time
import pandas as pd

# --- Modern LangChain Stack (LCEL) ---
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# --- Retrieval Tools ---
from langchain_community.retrievers import BM25Retriever

# --- Constants ---
DB_PATH = "./processed_data/chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# --- 1. Technique Descriptions (สำหรับ UI) ---
TECHNIQUE_DESCRIPTIONS = {
    "Hybrid Search": "ผสมผสาน Vector Search (ความหมาย) และ Keyword Search (คำเป๊ะ) เพื่อความแม่นยำสูงสุด",
    "Reranking": "จัดลำดับผลลัพธ์ใหม่ด้วย AI (Cross-Encoder) เพื่อคัดของดีที่สุดขึ้นบน",
    "Parent-Document Retrieval": "ค้นหาจากชิ้นส่วนเล็ก (Child) แต่ส่งบริบทเต็ม (Parent) ให้ AI อ่าน",
    "Multi-Query Retrieval": "แตกคำถามเป็นหลายรูปแบบ เพื่อค้นหาข้อมูลได้ครอบคลุมขึ้น",
    "Sub-Query Decomposition": "แยกคำถามซับซ้อนเป็นข้อย่อยๆ แล้วค้นหาทีละเรื่อง",
    "HyDE": "ให้ AI มโนคำตอบขึ้นมาก่อน แล้วเอาคำตอบนั้นไปค้นหา (ช่วยเรื่อง Semantic)",
    "Context Compression": "ตัดส่วนที่ไม่จำเป็นออก ให้เหลือแต่เนื้อๆ ก่อนส่งเข้า LLM",
    "Query Rewriting": "ปรับแก้คำถามให้ชัดเจนขึ้น (แก้คำผิด, ขยายความ) ก่อนค้นหา",
    "GraphRAG": "ใช้ความสัมพันธ์ของข้อมูล (Graph) มาช่วยตอบคำถามที่ซับซ้อน",
    "Self-RAG": "ให้ AI ตรวจสอบตัวเองว่าข้อมูลที่ได้มาเชื่อถือได้หรือไม่"
}

# --- 2. Database & Model Loading ---
@st.cache_resource
def load_vector_db():
    """โหลด Vector DB (Chroma) และสร้าง Embedding Function"""
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return Chroma(
        persist_directory=DB_PATH, 
        embedding_function=embedding_function, 
        collection_name="rag_demo"
    )

@st.cache_resource
def get_all_documents_metadata(_vector_db):
    """ดึง Metadata ทั้งหมดมาทำ Dataframe สำหรับ Plot กราฟ"""
    try:
        data = _vector_db.get(include=["metadatas"])
        return pd.DataFrame(data['metadatas'])
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return pd.DataFrame(columns=["source_doc", "umap_x", "umap_y"])

def get_llm(api_key):
    """Initialize Groq LLM ด้วยรุ่นล่าสุด (Llama 3.3)"""
    if not api_key: return None
    return ChatGroq(
        groq_api_key=api_key, 
        model_name="llama-3.3-70b-versatile", 
        temperature=0.0
    )

def format_docs(docs):
    """รวมเนื้อหา Doc เป็น String เดียว"""
    return "\n\n".join(doc.page_content for doc in docs)

def merge_documents(vector_docs, keyword_docs, k=4):
    """
    Manual Hybrid Merge: รวมเอกสารจาก 2 แหล่งและตัดตัวซ้ำ (De-duplication)
    โดยให้ความสำคัญกับ Vector Doc ก่อน
    """
    all_docs = vector_docs + keyword_docs
    unique_docs = []
    seen_content = set()
    
    for doc in all_docs:
        if doc.page_content not in seen_content:
            unique_docs.append(doc)
            seen_content.add(doc.page_content)
            
    return unique_docs[:k]

# --- 3. The Modular RAG Pipeline ---
def perform_rag(query, vector_db, llm, selected_techniques):
    """
    Dynamic Pipeline: ทำงานตามเทคนิคที่ผู้ใช้เลือก (List of strings)
    """
    start_time = time.time()
    current_query = query
    docs = []

    # --- A. Pre-Retrieval (Transformation) ---
    if "Query Rewriting" in selected_techniques and llm:
        # จำลองการ Rewrite (ใน Production จะใช้ Prompt จริงจังกว่านี้)
        rewrite_prompt = ChatPromptTemplate.from_template("Rewrite this query to be more specific/formal: {q}")
        chain = rewrite_prompt | llm | StrOutputParser()
        current_query = chain.invoke({"q": query})
        # (Optional) แสดงผล Query ใหม่ใน Console หรือ Log
        print(f"Rewritten Query: {current_query}")

    # --- B. Retrieval Strategy ---
    # เตรียมข้อมูลสำหรับ BM25 (ถ้าจำเป็น)
    need_keyword = "Hybrid Search" in selected_techniques or "Keyword Search" in selected_techniques
    
    if need_keyword:
        all_docs_raw = vector_db.get()
        all_docs = [
            Document(page_content=t, metadata=m) 
            for t, m in zip(all_docs_raw['documents'], all_docs_raw['metadatas'])
        ]
        bm25_retriever = BM25Retriever.from_documents(all_docs)
        bm25_retriever.k = 3

    # Execute Retrieval
    if "Hybrid Search" in selected_techniques:
        # 1. Vector Search
        v_docs = vector_db.as_retriever(search_kwargs={"k": 3}).invoke(current_query)
        # 2. Keyword Search
        kw_docs = bm25_retriever.invoke(current_query)
        # 3. Merge
        docs = merge_documents(v_docs, kw_docs)
        
    elif "Keyword Search" in selected_techniques: # ถ้าเลือก Keyword อย่างเดียว (สมมติว่าทำเป็น Checkbox แยก)
        docs = bm25_retriever.invoke(current_query)
        
    else:
        # Default: Semantic Vector Search
        docs = vector_db.as_retriever(search_kwargs={"k": 4}).invoke(current_query)

    # --- C. Post-Retrieval (Reranking/Filtering) ---
    if "Reranking" in selected_techniques:
        docs = sorted(docs, key=lambda x: len(x.page_content), reverse=True)
        
    if "Context Compression" in selected_techniques:
        # [Simulation] ตัด Text ให้สั้นลง
        for doc in docs:
            doc.page_content = doc.page_content[:300] + "..."

    # --- D. Generation ---
    if not llm:
        return "N/A (No API Key provided)", docs, time.time() - start_time

    # Standard RAG Prompt
    template = """You are a professional AI assistant. Answer the question based ONLY on the following context.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # LCEL Chain
    rag_chain = (
        {"context": lambda x: format_docs(docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = rag_chain.invoke(current_query)
    latency = time.time() - start_time
    
    return answer, docs, latency