import streamlit as st
import random
import pandas as pd
from utils import (
    load_vector_db, 
    get_all_documents_metadata, 
    get_source_content, 
    get_llm, 
    perform_rag, 
    TECHNIQUE_INFO
)

# --- Page Config ---
st.set_page_config(page_title="RAGScope Pro", page_icon="🧙‍♂️", layout="wide")

# --- Custom CSS (Clean Business Look) ---
st.markdown("""
<style>
    /* Card Container */
    .tech-card {
        background-color: #ffffff; 
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 8px; 
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Badges */
    .status-badge {
        background-color: #d1fae5; color: #065f46; 
        padding: 4px 12px; border-radius: 16px; font-weight: 600; margin-right: 8px;
        border: 1px solid #a7f3d0;
    }
    .db-badge {
        background-color: #eff6ff; color: #1e40af; 
        padding: 4px 12px; border-radius: 16px; font-weight: 600;
        border: 1px solid #bfdbfe;
    }
    
    /* Metrics Box */
    .metric-box {
        background-color: #f9fafb; padding: 10px; border-radius: 8px; 
        text-align: center; color: #374151; border: 1px solid #e5e7eb;
        font-family: monospace; font-size: 0.9em; margin-bottom: 10px;
    }
    
    /* Source Card (White with Red Accent) */
    .source-card {
        background-color: #ffffff; 
        padding: 12px; 
        margin-bottom: 12px; 
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #ef4444; /* Red Border */
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .source-header {
        font-weight: bold; color: #111827; margin-bottom: 4px; display: block; font-size: 0.95em;
    }
    .source-content {
        font-size: 0.9em; color: #4b5563; line-height: 1.5;
    }
    
    /* Log Style */
    .log-entry {
        font-family: monospace; font-size: 0.85em; color: #2563eb; 
        background-color: #eff6ff; padding: 5px 10px; border-radius: 4px; margin-bottom: 4px;
        border-left: 3px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def render_tech_selector(key_prefix):
    selected = []
    for tech_name, info in TECHNIQUE_INFO.items():
        with st.container():
            c1, c2 = st.columns([0.1, 0.9])
            with c1:
                if st.checkbox("", key=f"{key_prefix}_{tech_name}"):
                    selected.append(tech_name)
            with c2:
                st.markdown(f"**{tech_name}**")
                st.caption(info['desc'])
            st.markdown("---")
    return selected

def render_relevance_bar(score):
    # Dynamic Color based on score
    color = "#10b981" if score > 75 else "#f59e0b" if score > 50 else "#ef4444"
    st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <div style="display:flex; justify-content:space-between; font-size:0.75em; color:#6b7280; margin-bottom:2px;">
                <span>Match Confidence</span>
                <span>{score}%</span>
            </div>
            <div style="background-color: #f3f4f6; border-radius: 10px; height: 6px; width: 100%;">
                <div style="background-color: {color}; border-radius: 10px; height: 6px; width: {score}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎛️ RAG Control Panel")
    
    # 1. Mode Selection
    mode = st.radio("Select Mode", ["💬 Chat & Explore", "⚖️ Side-by-Side Compare"], index=0)
    st.divider()
    
    # 2. Connection Settings
    api_key = st.text_input("🔑 Groq API Key", type="password")
    
    # DB Selector (Updated for Harry Potter context)
    available_dbs = ["harry_potter_lore", "rag_demo"] 
    selected_db_name = st.selectbox("📚 Knowledge Base", available_dbs, index=0)
    
    # Load DB
    vector_db = load_vector_db(selected_db_name)
    df_meta = get_all_documents_metadata(vector_db)
    st.caption(f"Status: Connected to {len(df_meta)} chunks")
    
    # 3. Knowledge Explorer (Feature ที่ user ชอบ)
    with st.expander("📖 Knowledge Explorer"):
        if not df_meta.empty and 'source_doc' in df_meta.columns:
            unique_docs = df_meta['source_doc'].unique()
            selected_doc = st.selectbox("View File Content:", unique_docs)
            
            if st.button("Read Content"):
                chunks = get_source_content(vector_db, selected_doc)
                st.success(f"Found {len(chunks)} chunks")
                for i, chunk in enumerate(chunks):
                    st.text_area(f"Chunk {i+1}", chunk, height=120)
        else:
            st.warning("No documents found in this DB.")

    st.divider()
    
    # 4. Pipeline Configuration
    st.subheader("🛠️ Pipeline Builder")
    if mode == "💬 Chat & Explore":
        st.caption("Configure your active pipeline:")
        selected_techs_chat = render_tech_selector("chat")
    else:
        st.caption("Configure A/B pipelines:")
        t1, t2 = st.tabs(["Pipeline A", "Pipeline B"])
        with t1: selected_techs_a = render_tech_selector("pipe_a")
        with t2: selected_techs_b = render_tech_selector("pipe_b")

# --- MAIN APP LOGIC ---

# === MODE 1: CHAT ===
if mode == "💬 Chat & Explore":
    st.title("🧙‍♂️ Hogwarts Archives (RAG Chat)")
    
    # Status Bar
    active_techs = ", ".join(selected_techs_chat) if selected_techs_chat else "Basic RAG"
    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <span class="status-badge">⚡ Pipeline: {active_techs}</span>
            <span class="db-badge">📚 DB: {selected_db_name}</span>
        </div>
    """, unsafe_allow_html=True)

    # Initialize History
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Welcome to the archives! Ask me about spells, history, or character relationships. 📜"
        }]

    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Display Metadata if available
            if "metadata" in msg:
                m = msg['metadata']
                # Expander for Analysis
                with st.expander(f"📊 Analysis (Latency: {m['lat']:.4f}s | Cost: ${m['cost']:.6f})"):
                    
                    # TABS: Logs vs Context
                    tab_logs, tab_context = st.tabs(["🛠️ Execution Logs", "📄 Retrieved Context"])
                    
                    with tab_logs:
                        if m.get('logs'):
                            for log in m['logs']:
                                st.markdown(f"<div class='log-entry'>{log}</div>", unsafe_allow_html=True)
                        else:
                            st.info("No complex steps recorded (Basic Retrieval).")
                        
                        st.divider()
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Time", f"{m['lat']:.4f}s")
                        c2.metric("Tokens", f"{m['tokens']}")
                        c3.metric("Cost", f"${m['cost']:.6f}")

                    with tab_context:
                        for i, d in enumerate(m['docs']):
                            # Mock Score for visual demo (In prod, use vector distance)
                            score = random.randint(70, 99) - (i*3)
                            
                            st.markdown(f"""
                            <div class="source-card">
                                <span class="source-header">📄 Source {i+1}: {d.metadata.get('source_doc', 'Unknown')}</span>
                                <div class="source-content">{d.page_content[:350]}...</div>
                            </div>
                            """, unsafe_allow_html=True)
                            render_relevance_bar(score)

    # Chat Input
    if prompt := st.chat_input("Ask a question (e.g., 'Compare Snape and Sirius')..."):
        # User Message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Assistant Response
        with st.chat_message("assistant"):
            if not api_key:
                st.error("Please enter your Groq API Key in the Sidebar!")
            else:
                with st.spinner("Consulting the archives..."):
                    llm = get_llm(api_key)
                    # 🔥 Call RAG with unpack (6 values)
                    ans, docs, lat, tok, cost, logs = perform_rag(prompt, vector_db, llm, selected_techs_chat)
                    
                    st.markdown(ans)
                    
                    # Analysis Expander (Real-time)
                    with st.expander(f"📊 Analysis (Latency: {lat:.4f}s | Cost: ${cost:.6f})"):
                        tab_logs, tab_context = st.tabs(["🛠️ Execution Logs", "📄 Retrieved Context"])
                        
                        with tab_logs:
                            if logs:
                                for log in logs:
                                    st.markdown(f"<div class='log-entry'>{log}</div>", unsafe_allow_html=True)
                            else:
                                st.caption("Basic retrieval pipeline executed.")
                            
                            st.divider()
                            # Metrics Row
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Latency", f"{lat:.4f}s")
                            m2.metric("Est. Tokens", f"{tok}")
                            m3.metric("Est. Cost", f"${cost:.6f}")

                        with tab_context:
                            for i, d in enumerate(docs):
                                score = random.randint(75, 99) - (i*3)
                                st.markdown(f"""
                                <div class="source-card">
                                    <span class="source-header">📄 Source {i+1}: {d.metadata.get('source_doc')}</span>
                                    <div class="source-content">{d.page_content[:350]}...</div>
                                </div>
                                """, unsafe_allow_html=True)
                                render_relevance_bar(score)
                    
                    # Save to History
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": ans, 
                        "metadata": {
                            "lat": lat, "docs": docs, "cost": cost, 
                            "tokens": tok, "logs": logs, "pipe": selected_techs_chat
                        }
                    })

# === MODE 2: COMPARE ===
else:
    st.title("⚖️ Magical Strategy Comparison")
    st.markdown("Test two different RAG pipelines side-by-side.")
    
    query = st.text_input("Enter test query:", "Compare the magical aptitude of Bellatrix and Molly.")
    
    if st.button("⚔️ Run Comparison", type="primary"):
        if not api_key: st.error("No API Key provided")
        else:
            col_a, col_b = st.columns(2)
            llm = get_llm(api_key)
            
            # Helper to run side
            def run_side(col, name, techs):
                with col:
                    st.subheader(name)
                    st.caption(f"Config: {techs if techs else 'Basic'}")
                    
                    with st.spinner(f"Running {name}..."):
                        # Unpack 6 values
                        ans, docs, lat, tok, cost, logs = perform_rag(query, vector_db, llm, techs)
                        
                        st.success(ans)
                        
                        # Metrics Box
                        st.markdown(f"""
                        <div class="metric-box">
                            ⏱️ {lat:.4f}s &nbsp;|&nbsp; 💰 ${cost:.6f} &nbsp;|&nbsp; 📝 {tok} Toks
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Details Expander
                        with st.expander("🔍 Deep Dive"):
                            t_log, t_ctx = st.tabs(["Logs", "Context"])
                            with t_log:
                                for l in logs: st.code(l, language="text")
                            with t_ctx:
                                for i, d in enumerate(docs):
                                    st.markdown(f"**Src {i+1}:** {d.metadata.get('source_doc')}")
                                    st.caption(d.page_content[:200]+"...")

            run_side(col_a, "🟢 Pipeline A", selected_techs_a)
            run_side(col_b, "🔵 Pipeline B", selected_techs_b)