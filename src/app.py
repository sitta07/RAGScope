import streamlit as st
import random
from utils import (
    load_vector_db, 
    get_full_file_content,
    get_llm, 
    perform_rag, 
    TECHNIQUE_INFO,
    PIPELINE_PRESETS
)

# --- Config ---
st.set_page_config(page_title="RAGScope Pro", page_icon="⚡", layout="wide")
st.markdown("""
<style>
    div.stButton > button { width: 100%; border-radius: 6px; font-weight: 500; height: 3em; }
    .active-status { background-color: #ecfdf5; border: 1px solid #10b981; color: #064e3b; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; }
    .source-card { background: #fff; padding: 10px; border: 1px solid #eee; border-left: 4px solid #ef4444; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .log-box { font-family: monospace; font-size: 0.8em; background: #f8fafc; padding: 8px; border-radius: 4px; color: #334155; border: 1px solid #e2e8f0; margin-bottom: 4px; }
    .grid-desc { font-size: 0.75em; color: #64748b; line-height: 1.2; }
</style>
""", unsafe_allow_html=True)

# --- Helpers ---
def set_preset(name):
    st.session_state["active_mode"] = name
    for t in TECHNIQUE_INFO: st.session_state[f"chk_{t}"] = False
    for t in PIPELINE_PRESETS[name]["techs"]: st.session_state[f"chk_{t}"] = True

def get_selected_techs():
    return [t for t in TECHNIQUE_INFO if st.session_state.get(f"chk_{t}", False)]

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ System Control")
    api_key = st.text_input("Groq API Key", type="password")
    
    db_name = st.selectbox("Database", ["harry_potter_lore", "rag_demo"])
    vector_db = load_vector_db(db_name)
    
    with st.expander("📂 Data Explorer (Full Text)"):
        import os
        if os.path.exists("./data"):
            files = [f for f in os.listdir("./data") if f.endswith(".txt")]
            if files:
                f_sel = st.selectbox("File:", files)
                if st.button("Read"):
                    st.text_area("Content", get_full_file_content(f_sel), height=300)
        else:
            st.error("No files found in ./data")

# --- Tabs ---
t1, t2, t3 = st.tabs(["💬 Chat", "⚖️ Compare", "🎓 Learn RAG"])

# === TAB 1: CHAT ===
with t1:
    c_conf, c_chat = st.columns([0.4, 0.6])
    
    with c_conf:
        st.subheader("Pipeline Configuration")
        if "active_mode" not in st.session_state: st.session_state["active_mode"] = "Custom Manual"
        st.markdown(f"<div class='active-status'>✅ Strategy: {st.session_state['active_mode']}</div>", unsafe_allow_html=True)
        
        st.caption("⚡ Presets")
        cols = st.columns(2)
        for i, (k, v) in enumerate(PIPELINE_PRESETS.items()):
            if cols[i%2].button(k, help=v['desc']): 
                set_preset(k)
                st.rerun()
        
        st.caption("🎛️ Manual")
        g_cols = st.columns(2)
        for i, (k, v) in enumerate(TECHNIQUE_INFO.items()):
            with g_cols[i%2]:
                def on_change(): st.session_state["active_mode"] = "Custom Manual"
                st.checkbox(k, key=f"chk_{k}", on_change=on_change)
                st.markdown(f"<div class='grid-desc'>{v['desc']}</div><div style='height:8px'></div>", unsafe_allow_html=True)

    with c_chat:
        st.subheader("RAGScope Chat")
        if "msgs" not in st.session_state: st.session_state.msgs = [{"role": "assistant", "content": "Ready."}]
        
        for m in st.session_state.msgs:
            with st.chat_message(m["role"]):
                st.markdown(m["content"], unsafe_allow_html=True)
                if "meta" in m:
                    with st.expander(f"Analysis ({m['meta']['lat']:.2f}s | ${m['meta']['cost']:.5f})"):
                        tab_l, tab_c = st.tabs(["Logs", "Context"])
                        with tab_l: 
                            for l in m['meta']['logs']: st.markdown(f"<div class='log-box'>{l}</div>", unsafe_allow_html=True)
                        with tab_c:
                            for d in m['meta']['docs']:
                                st.markdown(f"<div class='source-card'><b>{d.metadata.get('source_doc')}</b><br><small>{d.page_content[:200]}...</small></div>", unsafe_allow_html=True)

        if q := st.chat_input("Query..."):
            st.chat_message("user").markdown(q)
            st.session_state.msgs.append({"role": "user", "content": q})
            
            with st.chat_message("assistant"):
                if not api_key: st.error("No API Key")
                else:
                    with st.spinner("Processing..."):
                        llm = get_llm(api_key)
                        sel_techs = get_selected_techs()
                        ans, docs, lat, tok, cost, logs = perform_rag(q, vector_db, llm, sel_techs)
                        
                        strat = st.session_state["active_mode"]
                        tech_str = ", ".join(sel_techs)
                        final = f"{ans}\n\n---\n<small style='color:grey'>**Strategy:** {strat} [{tech_str}]</small>"
                        
                        st.markdown(final, unsafe_allow_html=True)
                        st.session_state.msgs.append({
                            "role": "assistant", "content": final,
                            "meta": {"lat": lat, "docs": docs, "cost": cost, "logs": logs}
                        })
                        st.rerun()

# === TAB 2: COMPARE ===
with t2:
    st.title("A/B Testing")
    c1, c2 = st.columns(2)
    
    def render_mini_builder(prefix):
        if f"{prefix}_mode" not in st.session_state: st.session_state[f"{prefix}_mode"] = "Custom"
        st.info(f"Mode: {st.session_state[f'{prefix}_mode']}")
        p_cols = st.columns(2)
        for k in PIPELINE_PRESETS:
            if p_cols[0].button(f"Load {k}", key=f"btn_{prefix}_{k}"):
                 st.session_state[f"{prefix}_mode"] = k
                 for t in TECHNIQUE_INFO: st.session_state[f"{prefix}_{t}"] = (t in PIPELINE_PRESETS[k]['techs'])
                 st.rerun()
        sel = [t for t in TECHNIQUE_INFO if st.checkbox(t, key=f"{prefix}_{t}")]
        return sel

    with c1: 
        st.subheader("Pipeline A")
        techs_a = render_mini_builder("pipe_a")
    with c2: 
        st.subheader("Pipeline B")
        techs_b = render_mini_builder("pipe_b")

    q = st.text_input("Comparison Query", "Who is Harry Potter?")
    if st.button("Run Comparison"):
        if not api_key: st.error("No API Key")
        else:
            llm = get_llm(api_key)
            ca, cb = st.columns(2)
            def run(col, techs):
                with col:
                    with st.spinner("Processing..."):
                        a, d, l, t, c, logs = perform_rag(q, vector_db, llm, techs)
                        st.markdown(a)
                        st.caption(f"{l:.2f}s | ${c:.5f}")
                        with st.expander("Logs"): 
                             for log in logs: st.code(log, language='text')
            run(ca, techs_a)
            run(cb, techs_b)

# === TAB 3: LEARN RAG ===
with t3:
    st.title("🎓 RAG Academy: Feynman Style")
    st.markdown("Explaining complex techniques simply.")
    
    lessons = {
        "Hybrid Search": "Imagine a Librarian (Exact words) and a Psychologist (Intent) working together.",
        "Reranking": "Your assistant brings 100 papers. You (the Reranker) read them carefully and keep only the Top 5.",
        "Parent-Document": "Finding a highlight in a book is good, but reading the whole page is better for context.",
        "Multi-Query": "Instead of asking once, the AI brainstorms 3 variations of your question to cover all angles.",
        "Sub-Query": "For hard questions like 'Compare X and Y', the AI breaks it down: 1. Research X, 2. Research Y.",
        "HyDE": "The AI guesses the answer first, then searches for documents that look like its guess.",
        "Context Compression": "Like a highlighter pen. The AI reads the document and extracts only the key facts.",
        "Query Rewriting": "The AI acts as a translator, turning your messy question into a perfect search query."
    }
    
    cols = st.columns(2)
    for i, (k, v) in enumerate(lessons.items()):
        with cols[i%2]:
            st.info(f"**{k}**\n\n{v}")