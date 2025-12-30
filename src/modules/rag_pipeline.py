import time
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

from .database import get_full_file_content
from .config import DATA_FOLDER

def calculate_cost(text):
    tokens = len(text) / 4
    cost = (tokens / 1000) * 0.0005 
    return int(tokens), cost

def format_docs(docs):
    return "\n\n".join(f"[Source: {d.metadata.get('source_doc', 'Unknown')}] {d.page_content}" for d in docs)

def merge_documents(v_docs, k_docs):
    seen = set()
    merged = []
    max_len = max(len(v_docs), len(k_docs))
    for i in range(max_len):
        if i < len(v_docs):
            d = v_docs[i]
            if d.page_content not in seen:
                merged.append(d)
                seen.add(d.page_content)
        if i < len(k_docs):
            d = k_docs[i]
            if d.page_content not in seen:
                merged.append(d)
                seen.add(d.page_content)
    return merged

def perform_rag(query, vector_db, llm, selected_techniques):
    start_time = time.time()
    current_query = query
    docs = []
    log_steps = []

    if not llm: return "API Key Missing", [], 0, 0, 0, []

    # 1. Query Rewriting (Real)
    if "Query Rewriting" in selected_techniques:
        prompt = ChatPromptTemplate.from_template(
            """Rewrite this query to be specific and keyword-rich for a database search.
            Output ONLY the query string. No quotes.
            Query: {q}"""
        )
        new_query = (prompt | llm | StrOutputParser()).invoke({"q": query}).strip()
        if len(new_query) < len(query) * 3: 
            log_steps.append(f"🔄 Rewrote: '{query}' -> '{new_query}'")
            current_query = new_query
        else:
            log_steps.append("⚠️ Rewrite ignored (too long).")

    # 2. HyDE (Real)
    if "HyDE" in selected_techniques:
        prompt = ChatPromptTemplate.from_template("Write a concise hypothetical answer to: {q}")
        fake_ans = (prompt | llm | StrOutputParser()).invoke({"q": current_query})
        log_steps.append("👻 HyDE: Generated hypothetical answer.")
        current_query = f"{current_query} {fake_ans}"

    # 3. Multi-Query / Sub-Query (Real Loop)
    queries_to_run = [current_query]
    
    if "Multi-Query" in selected_techniques:
        prompt = ChatPromptTemplate.from_template("Generate 2 alternative search queries for: {q}. Sep by newline.")
        vars = (prompt | llm | StrOutputParser()).invoke({"q": current_query}).split("\n")
        cleaned_vars = [v.strip() for v in vars if v.strip()]
        queries_to_run.extend(cleaned_vars[:2])
        log_steps.append(f"🔀 Multi-Query: Added {len(cleaned_vars)} variations.")

    if "Sub-Query" in selected_techniques:
        prompt = ChatPromptTemplate.from_template("Break down '{q}' into 2 sub-questions. Sep by newline.")
        vars = (prompt | llm | StrOutputParser()).invoke({"q": query}).split("\n")
        cleaned_vars = [v.strip() for v in vars if v.strip()]
        queries_to_run.extend(cleaned_vars[:2])
        log_steps.append(f"🧱 Sub-Query: Added {len(cleaned_vars)} steps.")

    # --- RETRIEVAL PHASE ---
    all_data = vector_db.get()
    all_docs_objs = [Document(page_content=t, metadata=m) for t, m in zip(all_data['documents'], all_data['metadatas'])]
    
    temp_docs = []
    INITIAL_K = 10 if ("Reranking" in selected_techniques) else 5
    
    for q in queries_to_run:
        # Vector
        v_res = vector_db.as_retriever(search_kwargs={"k": INITIAL_K}).invoke(q)
        # Keyword
        k_res = []
        if "Hybrid Search" in selected_techniques:
            bm25 = BM25Retriever.from_documents(all_docs_objs)
            bm25.k = INITIAL_K
            k_res = bm25.invoke(q)
        
        merged = merge_documents(v_res, k_res)
        temp_docs.extend(merged)

    docs = merge_documents(temp_docs, [])
    log_steps.append(f"🔍 Retrieval: Pool of {len(docs)} docs from {len(queries_to_run)} queries.")

    # --- POST-PROCESSING ---

    # 4. Reranking (Real LLM Scoring)
    if "Reranking" in selected_techniques and docs:
        log_steps.append("🥇 Reranking: LLM Scoring...")
        scored = []
        for d in docs:
            prompt = ChatPromptTemplate.from_template(
                """Rate relevance (0-10) of the text to query '{q}'. 
                If the text contains a direct definition, biography, or exact answer, give 10.
                Output ONLY the number.
                Text: {t}"""
            )
            try:
                res = (prompt | llm | StrOutputParser()).invoke({"q": query, "t": d.page_content[:500]})
                score = float(re.search(r'\d+', res).group())
            except:
                score = 5.0
            d.metadata['score'] = score
            scored.append(d)
        
        docs = sorted(scored, key=lambda x: x.metadata.get('score', 0), reverse=True)[:5]

    # 5. Parent-Document (Real File I/O)
    if "Parent-Document" in selected_techniques and docs:
        log_steps.append("📂 Parent-Document: Fetching FULL files...")
        new_docs = []
        processed_files = set()
        for d in docs:
            fname = d.metadata.get('source_doc')
            if fname and fname not in processed_files:
                full_text = get_full_file_content(fname)
                if not full_text.startswith("[Error"):
                    new_d = Document(page_content=full_text, metadata=d.metadata)
                    new_docs.append(new_d)
                    processed_files.add(fname)
        if new_docs:
            docs = new_docs[:2]

    # 6. Context Compression (Real Extraction)
    if "Context Compression" in selected_techniques and docs:
        log_steps.append("✂️ Compression: Extracting key info...")
        compressed = []
        for d in docs:
            if len(d.page_content) > 500:
                prompt = ChatPromptTemplate.from_template(
                    "Extract sentences answering '{q}' from text. Keep names/dates. Text: {t}"
                )
                extracted = (prompt | llm | StrOutputParser()).invoke({"q": query, "t": d.page_content[:1500]})
                d.page_content = extracted
            compressed.append(d)
        docs = compressed

    # --- GENERATION ---
    template = """
    Answer clearly based ONLY on context. If context is missing, say "I don't know".
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = {"context": lambda x: format_docs(docs), "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    
    try:
        answer = chain.invoke(query)
    except Exception as e:
        answer = f"Error: {e}"

    lat = time.time() - start_time
    tokens, cost = calculate_cost(query + format_docs(docs) + answer)

    return answer, docs, lat, tokens, cost, log_steps