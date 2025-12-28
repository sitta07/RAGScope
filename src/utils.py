import streamlit as st
import time
import pandas as pd
import random

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

# Constants
DB_PATH = "./processed_data/chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Metadata (เหมือนเดิม)
TECHNIQUE_INFO = {
    "Hybrid Search": { "desc": "ผสม Vector + Keyword", "suitable": "ศัพท์เฉพาะ", "popularity": "⭐⭐⭐⭐⭐", "pair_with": "Reranking" },
    "Reranking": { "desc": "จัดลำดับใหม่ด้วยบริบท", "suitable": "ความแม่นยำสูง", "popularity": "⭐⭐⭐⭐⭐", "pair_with": "Hybrid" },
    "Parent-Document": { "desc": "ดึงบริบทกว้างขึ้น", "suitable": "ข้อมูลซับซ้อน", "popularity": "⭐⭐⭐⭐", "pair_with": "Compression" },
    "Multi-Query": { "desc": "แตกคำถามหลากหลาย", "suitable": "คำถามกำกวม", "popularity": "⭐⭐⭐", "pair_with": "Reranking" },
    "Query Rewriting": { "desc": "ปรับแก้คำถามให้ชัด", "suitable": "User ทั่วไป", "popularity": "⭐⭐⭐⭐", "pair_with": "All" }
}

@st.cache_resource
def load_vector_db(collection_name="harry_potter_lore"):
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return Chroma(persist_directory=DB_PATH, embedding_function=embedding_function, collection_name=collection_name)

@st.cache_resource
def get_all_documents_metadata(_vector_db):
    try:
        data = _vector_db.get(include=["metadatas"])
        return pd.DataFrame(data['metadatas'])
    except:
        return pd.DataFrame(columns=["source_doc"])

def get_source_content(_vector_db, source_name):
    try:
        results = _vector_db.get(where={"source_doc": source_name})
        return results['documents']
    except:
        return []

def calculate_cost(text):
    tokens = len(text) / 4
    cost = (tokens / 1000) * 0.0005 
    return int(tokens), cost

def get_llm(api_key):
    if not api_key: return None
    # เพิ่ม temperature นิดหน่อยเพื่อให้มีความคิดสร้างสรรค์ในการ Rewrite
    return ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0.3)

def format_docs(docs):
    # ใส่ชื่อ Source เข้าไปใน Context ด้วย เพื่อให้ AI อ้างอิงได้
    return "\n\n".join(f"[Source: {d.metadata.get('source_doc', 'Unknown')}] {d.page_content}" for d in docs)

def merge_documents(vector_docs, keyword_docs):
    # Logic: เอา Vector ขึ้นก่อน แล้วเติมด้วย Keyword ที่ไม่ซ้ำ
    seen = set()
    unique_docs = []
    for d in vector_docs:
        if d.page_content not in seen:
            unique_docs.append(d)
            seen.add(d.page_content)
    for d in keyword_docs:
        if d.page_content not in seen:
            unique_docs.append(d)
            seen.add(d.page_content)
    return unique_docs[:5] # เอา Top 5

# 🔥 Core Pipeline Logic (Updated)
def perform_rag(query, vector_db, llm, selected_techniques):
    start_time = time.time()
    current_query = query
    docs = []
    log_steps = [] # เก็บ Log การทำงานไว้โชว์ user

    if not llm:
        return "⚠️ Please provide API Key", [], 0.0, 0, 0.0

    # 1. Query Transformation (ทำงานจริงแล้ว!)
    if "Query Rewriting" in selected_techniques:
        rewrite_prompt = ChatPromptTemplate.from_template(
            "Rephrase the following question to be more specific and optimized for a search engine. Question: {q}"
        )
        chain = rewrite_prompt | llm | StrOutputParser()
        original_query = current_query
        current_query = chain.invoke({"q": query})
        log_steps.append(f"🔄 Rewrote query: '{original_query}' -> '{current_query}'")

    if "Multi-Query" in selected_techniques:
        mq_prompt = ChatPromptTemplate.from_template(
            "Generate 3 different versions of this question to retrieve better information. Separate them by newlines. Question: {q}"
        )
        chain = mq_prompt | llm | StrOutputParser()
        variations = chain.invoke({"q": current_query}).split("\n")
        log_steps.append(f"🔀 Multi-Query generated: {variations}")
        # ใน Demo นี้เราจะใช้ Query ตัวแรกสุดที่ Gen มาเพื่อความง่ายในการ flow
        if variations: current_query = variations[0]

    # 2. Retrieval
    all_data = vector_db.get()
    all_docs_list = [Document(page_content=t, metadata=m) for t, m in zip(all_data['documents'], all_data['metadatas'])]
    
    # Base Search
    v_retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    bm25_retriever = BM25Retriever.from_documents(all_docs_list)
    bm25_retriever.k = 5

    if "Hybrid Search" in selected_techniques:
        v_docs = v_retriever.invoke(current_query)
        k_docs = bm25_retriever.invoke(current_query)
        docs = merge_documents(v_docs, k_docs)
        log_steps.append(f"⚡ Hybrid merged {len(v_docs)} vector results with {len(k_docs)} keyword results.")
    else:
        # Default Semantic
        docs = v_retriever.invoke(current_query)

    # 3. Post-Processing
    if "Reranking" in selected_techniques:
        # 💡 Logic จริง: ให้ LLM เป็นคน Judge ว่า Document ไหนตรงคำถามที่สุด (LLM-based Reranking)
        # วิธีนี้ช้าหน่อยแต่แม่นและเห็นผลชัดกว่า Mock
        rerank_prompt = ChatPromptTemplate.from_template(
            """Rank these documents based on relevance to the query: '{q}'. 
            Return only the indices of the top 3 most relevant documents (e.g., 0, 2, 1).
            Documents:
            {docs_str}
            """
        )
        docs_str = "\n".join([f"[{i}] {d.page_content[:100]}..." for i, d in enumerate(docs)])
        try:
            indices_str = (rerank_prompt | llm | StrOutputParser()).invoke({"q": current_query, "docs_str": docs_str})
            # พยายามแกะตัวเลขออกมา
            import re
            indices = [int(s) for s in re.findall(r'\b\d+\b', indices_str)][:3]
            if indices:
                docs = [docs[i] for i in indices if i < len(docs)]
                log_steps.append(f"🥇 Reranked top documents: {indices}")
        except:
            log_steps.append("⚠️ Reranking failed, using original order.")

    # 4. Generation (Prompt แบบ Senior)
    template = """
    You are an expert Historian and Analyst of the Wizarding World.
    Your goal is to provide a comprehensive, detailed, and well-structured answer.
    
    Guidelines:
    - Use the Context provided below to answer the user's question.
    - If the context mentions specific details (spells, dates, relationships), cite them.
    - Explain the "Why" and "How", not just the "What".
    - If different sources in the context say different things, mention the conflict.
    - Use bullet points for clarity if listing items.
    
    Context:
    {context}
    
    Question: {question}
    
    Detailed Answer:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = {"context": lambda x: format_docs(docs), "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    
    try:
        answer = chain.invoke(current_query)
    except Exception as e:
        answer = f"Error: {e}"
    
    latency = time.time() - start_time
    total_text = current_query + format_docs(docs) + answer
    tokens, cost = calculate_cost(total_text)
    
    # แนบ Log Steps ไปกับ docs เพื่อเอาไปโชว์ใน UI
    return answer, docs, latency, tokens, cost, log_steps