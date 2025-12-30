import streamlit as st
import random

# --- Modular Imports ---
from modules.config import TECHNIQUE_INFO, PIPELINE_PRESETS
from modules.database import load_vector_db, get_full_file_content, get_file_list
from modules.llm import get_llm
from modules.rag_pipeline import perform_rag
from modules.languages import get_text, get_lesson
from modules.visuals import render_tech_flowchart

# --- Page Config ---
st.set_page_config(page_title="RAGScope Pro", page_icon="📝", layout="wide")

# --- Professional CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    div.stButton > button { 
        width: 100%; border-radius: 6px; font-weight: 600; height: 3em; 
        background-color: #f8fafc; border: 1px solid #cbd5e1; color: #334155;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover { background-color: #e2e8f0; transform: translateY(-1px); }
    .active-status { background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 12px; border-radius: 6px; text-align: center; font-weight: 600; margin-bottom: 20px; }
    .lesson-container {
        border: 1px solid #e2e8f0; border-radius: 8px; padding: 25px;
        background-color: #ffffff; margin-bottom: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .lesson-header { 
        display: flex; align-items: center; margin-bottom: 15px; 
        border-bottom: 2px solid #f1f5f9; padding-bottom: 10px;
    }
    .lesson-number {
        background: #3b82f6; color: white; width: 32px; height: 32px; 
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-weight: bold; margin-right: 15px; flex-shrink: 0;
    }
    .lesson-title { color: #1e293b; font-size: 1.25rem; font-weight: 700; }
    .process-box {
        background-color: #f8fafc; border-left: 4px solid #3b82f6;
        padding: 15px; margin: 15px 0; border-radius: 0 4px 4px 0;
        white-space: pre-line; color: #334155; line-height: 1.6;
    }
    .log-entry { font-family: 'Courier New', monospace; font-size: 0.8em; background: #f1f5f9; padding: 8px; margin-bottom: 4px; border-radius: 4px; }
    .source-ref { font-size: 0.85em; background: #fff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #10b981; }
</style>
""", unsafe_allow_html=True)

# --- Language Setup ---
if "lang" not in st.session_state: st.session_state["lang"] = "en"
col_h, col_l = st.columns([0.88, 0.12])
with col_h: st.title(f"{get_text(st.session_state['lang'], 'title')}")
with col_l:
    l_opt = st.selectbox("Lang", ["🇺🇸 EN", "🇹🇭 TH"], index=0 if st.session_state["lang"]=="en" else 1, label_visibility="collapsed")
    new_lang = "en" if "🇺🇸" in l_opt else "th"
    if new_lang != st.session_state["lang"]:
        st.session_state["lang"] = new_lang
        st.rerun()
lang = st.session_state["lang"]

# --- Helpers ---
def set_preset(name):
    st.session_state["active_mode"] = name
    for t in TECHNIQUE_INFO: st.session_state[f"chk_{t}"] = False
    for t in PIPELINE_PRESETS[name]["techs"]: st.session_state[f"chk_{t}"] = True

def get_selected_techs():
    return [t for t in TECHNIQUE_INFO if st.session_state.get(f"chk_{t}", False)]

# --- Sidebar ---
with st.sidebar:
    st.header("System Config")
    api_key = st.text_input("Groq API Key", type="password")
    try:
        vector_db = load_vector_db("harry_potter_lore")
        st.success("Database Connected")
    except:
        st.error("Database Error")
    with st.expander("Data Explorer"):
        files = get_file_list()
        if files:
            f = st.selectbox("File", files)
            if st.button(get_text(lang, 'btn_read')):
                st.text_area("Content", get_full_file_content(f), height=300)

# --- Tabs ---
t1, t2, t3 = st.tabs([get_text(lang, 'subheader_chat'), get_text(lang, 'subheader_ab'), get_text(lang, 'subheader_learn')])

# ================= TAB 1: CHAT =================
with t1:
    c_conf, c_chat = st.columns([0.35, 0.65])
    
    with c_conf:
        st.subheader(get_text(lang, 'subheader_config'))
        if "active_mode" not in st.session_state: st.session_state["active_mode"] = "Custom Manual"
        st.markdown(f"<div class='active-status'>✅ {get_text(lang, 'active_strategy')}: {st.session_state['active_mode']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"**{get_text(lang, 'presets')}**")
        pc1, pc2 = st.columns(2)
        for i, (k, v) in enumerate(PIPELINE_PRESETS.items()):
            if (i % 2 == 0): col = pc1 
            else: col = pc2
            if col.button(k): 
                set_preset(k)
                st.rerun()
        
        st.markdown("---")
        
        # Manual Grid 4x4
        st.markdown(f"**{get_text(lang, 'manual')}**")
        all_techs = list(TECHNIQUE_INFO.keys())
        mid = 4
        cl, cr = st.columns(2)
        with cl:
            for t in all_techs[:mid]:
                def cb(): st.session_state["active_mode"] = "Custom Manual"
                st.checkbox(t, key=f"chk_{t}", on_change=cb)
        with cr:
            for t in all_techs[mid:]:
                def cb(): st.session_state["active_mode"] = "Custom Manual"
                st.checkbox(t, key=f"chk_{t}", on_change=cb)

    with c_chat:
        chat_box = st.container(height=600)
        if "msgs" not in st.session_state: st.session_state.msgs = [{"role": "assistant", "content": "System Ready."}]
        
        with chat_box:
            for m in st.session_state.msgs:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"], unsafe_allow_html=True)
                    if "meta" in m:
                        meta = m['meta']
                        with st.expander(f"📊 {get_text(lang, 'analysis')} ({meta['lat']:.2f}s | ${meta['cost']:.5f})"):
                            tabs = st.tabs([get_text(lang, 'logs'), get_text(lang, 'context')])
                            with tabs[0]: 
                                for l in meta['logs']: st.markdown(f"<div class='log-entry'>{l}</div>", unsafe_allow_html=True)
                            with tabs[1]:
                                for d in meta['docs']:
                                    sc = d.metadata.get('score', 0)
                                    st.markdown(f"<div class='source-ref'><b>{d.metadata.get('source_doc')}</b> <span style='float:right;color:#059669'>Score: {sc:.1f}</span><br>{d.page_content[:250]}...</div>", unsafe_allow_html=True)

        if q := st.chat_input(get_text(lang, 'placeholder')):
            st.session_state.msgs.append({"role": "user", "content": q})
            st.rerun()

        if st.session_state.msgs[-1]["role"] == "user":
            with chat_box:
                with st.chat_message("assistant"):
                    if not api_key: st.error(get_text(lang, 'no_api'))
                    else:
                        with st.spinner(get_text(lang, 'running')):
                            llm = get_llm(api_key)
                            techs = get_selected_techs()
                            ans, docs, lat, tok, cost, logs = perform_rag(st.session_state.msgs[-1]["content"], vector_db, llm, techs)
                            
                            final = f"{ans}\n\n---\n<small style='color:grey'>Strategy: {st.session_state['active_mode']}</small>"
                            st.markdown(final, unsafe_allow_html=True)
                            st.session_state.msgs.append({
                                "role": "assistant", "content": final, 
                                "meta": {"lat": lat, "docs": docs, "cost": cost, "logs": logs}
                            })
                            st.rerun()

# ================= TAB 2: A/B =================
with t2:
    st.subheader(get_text(lang, 'subheader_ab'))
    c1, c2 = st.columns(2)
    
    def render_ab_col(prefix, title):
        st.markdown(f"**{title}**")
        if f"{prefix}_mode" not in st.session_state: st.session_state[f"{prefix}_mode"] = "Custom"
        
        cols = st.columns(2)
        for k in PIPELINE_PRESETS:
            if cols[0].button(k, key=f"btn_{prefix}_{k}"):
                st.session_state[f"{prefix}_mode"] = k
                for t in TECHNIQUE_INFO: st.session_state[f"{prefix}_{t}"] = (t in PIPELINE_PRESETS[k]['techs'])
                st.rerun()
        
        with st.expander("Customize"):
            return [t for t in TECHNIQUE_INFO if st.checkbox(t, key=f"{prefix}_{t}")]

    with c1: techs_a = render_ab_col("pipe_a", "Pipeline A")
    with c2: techs_b = render_ab_col("pipe_b", "Pipeline B")
    
    st.divider()
    q_ab = st.text_input("Query", key="ab_query")
    if st.button(get_text(lang, 'btn_compare'), type="primary"):
        if not api_key: st.error("No API Key")
        else:
            llm = get_llm(api_key)
            ca, cb = st.columns(2)
            def run_side(col, techs):
                with col:
                    with st.spinner("Processing..."):
                        a, d, l, t, c, logs = perform_rag(q_ab, vector_db, llm, techs)
                        st.markdown(a)
                        st.caption(f"{l:.2f}s | ${c:.5f}")
                        with st.expander("Logs"):
                            for log in logs: st.code(log)
            run_side(ca, techs_a)
            run_side(cb, techs_b)

# ================= TAB 3: LEARN (Sequential List) =================
with t3:
    st.header(get_text(lang, 'subheader_learn'))
    st.markdown(get_text(lang, 'learn_intro'))
    st.divider()
    
    # Iterate through all techniques SEQUENTIALLY (No Grid)
    all_techs = list(TECHNIQUE_INFO.keys())
    
    for i, tech_name in enumerate(all_techs):
        lesson = get_lesson(lang, tech_name)
        
        # Container for each lesson
        st.markdown(f"""
        <div class="lesson-container">
            <div class="lesson-header">
                <div class="lesson-number">{i+1}</div>
                <div class="lesson-title">{tech_name} ({lesson.get('concept', '')})</div>
            </div>
            <div><b>🚨 Problem:</b> {lesson.get('problem', '')}</div>
            <div class="process-box"><b>⚡ Process Flow:</b><br>{lesson.get('process', '')}</div>
            <div style="font-size:0.9em; color:#64748b; margin-top:10px;">
                <b>⚙️ Technical Implementation:</b> {lesson.get('technical', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Flowchart (Full Width)
        render_tech_flowchart(tech_name)
        st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)