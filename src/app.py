import streamlit as st
import time
import os
import sys
from functools import lru_cache

# --- Lightweight Imports (โหลดเร็ว) ---
from modules.languages import get_text, get_lesson
from modules.ui import inject_custom_css, render_pro_credit

# --- Page Config ---
st.set_page_config(page_title="RAGScope Pro", layout="wide")
inject_custom_css()

# --- Caching Functions ---
@st.cache_resource(ttl=3600)
def get_cached_vector_db(db_name):
    """Cache vector database to avoid reloading"""
    from modules.database import load_vector_db
    return load_vector_db(db_name)

@st.cache_resource
def get_cached_llm(api_key):
    """Cache LLM instance"""
    from modules.llm import get_llm
    return get_llm(api_key)

@st.cache_data(ttl=600)
def get_cached_file_list():
    """Cache file list for 10 minutes"""
    from modules.database import get_file_list
    return get_file_list()

@st.cache_data(ttl=600)
def get_cached_file_content(filename):
    """Cache file content"""
    from modules.database import get_full_file_content
    return get_full_file_content(filename)

# --- Auto-Ingest Fail-safe (Utility) ---
@st.cache_resource
def ensure_database_exists():
    """Cache database initialization check"""
    if not os.path.exists("processed_data") or not os.listdir("processed_data"):
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            import ingest
            ingest.main()
        except Exception as e:
            st.error(f"Auto-ingestion failed: {e}")
    return True

# --- Session State Initialization (ปรับให้กระชับ) ---
def init_session_state():
    """Initialize all session state variables at once"""
    defaults = {
        "groq_api_key": "",
        "lang": "en",
        "msgs": [{"role": "assistant", "content": "System Ready."}],
        "active_mode": "Custom Manual"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==========================================
# 🏠 PART 1: WELCOME PAGE (Lightweight)
# ==========================================
def render_welcome_page():
    lang = st.session_state["lang"]
    
    # Top Right Language - Simplified
    _, c_lang = st.columns([0.85, 0.15])
    with c_lang:
        l_opt = st.selectbox("Lang", ["EN", "TH"], 
                             index=0 if lang == "en" else 1, 
                             key="welcome_lang", 
                             label_visibility="collapsed")
        new_lang = "en" if "EN" in l_opt else "th"
        if new_lang != lang:
            st.session_state["lang"] = new_lang
            st.rerun()
    
    # UI Rendering - ใช้ f-string แทน get_text ซ้ำซ้อน
    texts = {
        'title': get_text(lang, 'welcome_title'),
        'sub': get_text(lang, 'welcome_sub'),
        'feat_1_title': get_text(lang, 'feat_1_title'),
        'feat_1_desc': get_text(lang, 'feat_1_desc'),
        'feat_2_title': get_text(lang, 'feat_2_title'),
        'feat_2_desc': get_text(lang, 'feat_2_desc'),
        'feat_3_title': get_text(lang, 'feat_3_title'),
        'feat_3_desc': get_text(lang, 'feat_3_desc'),
    }
    
    st.markdown(f"<div class='custom-welcome-title'>{texts['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='welcome-subtitle'>{texts['sub']}</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='feature-card'><div class='feature-title'>{texts['feat_1_title']}</div><div class='feature-desc'>{texts['feat_1_desc']}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='feature-card'><div class='feature-title'>{texts['feat_2_title']}</div><div class='feature-desc'>{texts['feat_2_desc']}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='feature-card'><div class='feature-title'>{texts['feat_3_title']}</div><div class='feature-desc'>{texts['feat_3_desc']}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Centered form
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.markdown(f"#### {get_text(lang, 'get_started')}")
        st.info(get_text(lang, 'api_req'))
        api_input = st.text_input(get_text(lang, 'enter_key'), type="password", placeholder="gsk_...")
        st.markdown(f"<small>{get_text(lang, 'get_key_info')}</small>", unsafe_allow_html=True)
        st.markdown("")

        if st.button(get_text(lang, 'btn_enter'), type="primary"):
            if api_input.startswith("gsk_"):
                st.session_state["groq_api_key"] = api_input
                st.success(get_text(lang, 'access_granted'))
                time.sleep(0.5)  # ลดเวลาจาก 1 เป็น 0.5 วินาที
                st.rerun()
            else:
                st.error(get_text(lang, 'invalid_key'))
        
        render_pro_credit()

# ==========================================
# 🖥️ PART 2: DASHBOARD (Heavy Logic)
# ==========================================
def render_dashboard():
    lang = st.session_state["lang"]
    
    # ⚡ LAZY IMPORTS with caching
    if 'heavy_modules_loaded' not in st.session_state:
        with st.spinner("Initializing AI Core..."):
            from modules.config import TECHNIQUE_INFO, PIPELINE_PRESETS
            from modules.visuals import render_tech_flowchart
            
            # Store in session state to avoid re-importing
            st.session_state['TECHNIQUE_INFO'] = TECHNIQUE_INFO
            st.session_state['PIPELINE_PRESETS'] = PIPELINE_PRESETS
            st.session_state['render_tech_flowchart'] = render_tech_flowchart
            st.session_state['heavy_modules_loaded'] = True
            
            # Check DB (cached)
            ensure_database_exists()
    
    # Retrieve from session state
    TECHNIQUE_INFO = st.session_state['TECHNIQUE_INFO']
    PIPELINE_PRESETS = st.session_state['PIPELINE_PRESETS']
    render_tech_flowchart = st.session_state['render_tech_flowchart']
    
    # Header
    c_title, c_lang = st.columns([0.85, 0.15])
    with c_title:
        st.markdown(f"<div class='custom-title'>{get_text(lang, 'title')}</div>", unsafe_allow_html=True)
    with c_lang:
        l_opt = st.selectbox("Lang", ["EN", "TH"], 
                             index=0 if lang == "en" else 1, 
                             key="dash_lang", 
                             label_visibility="collapsed")
        new_lang = "en" if "EN" in l_opt else "th"
        if new_lang != lang:
            st.session_state["lang"] = new_lang
            st.rerun()

    # Sidebar
    with st.sidebar:
        st.header("System Config")
        st.success("API Key Configured")
        if st.button("Logout"):
            st.session_state["groq_api_key"] = ""
            st.rerun()
        st.markdown("---")
        
        # Use cached vector DB
        try:
            vector_db = get_cached_vector_db("harry_potter_lore")
            st.success("Database Connected")
        except Exception as e:
            st.error(f"Database Error: {str(e)}")
            vector_db = None
            
        with st.expander("Data Explorer"):
            files = get_cached_file_list()  # Cached
            if files:
                f = st.selectbox("File", files)
                if st.button(get_text(lang, 'btn_read')):
                    content = get_cached_file_content(f)  # Cached
                    st.text_area("Content", content, height=300)
        st.markdown("---")
        render_pro_credit(in_sidebar=True)

    # Helper Functions (ย้ายออกมาเพื่อไม่ให้ define ซ้ำ)
    def set_preset(name):
        st.session_state["active_mode"] = name
        for t in TECHNIQUE_INFO:
            st.session_state[f"chk_{t}"] = t in PIPELINE_PRESETS[name]["techs"]

    def get_selected_techs():
        return [t for t in TECHNIQUE_INFO if st.session_state.get(f"chk_{t}", False)]

    # Tabs
    t1, t2, t3 = st.tabs([
        get_text(lang, 'subheader_chat'), 
        get_text(lang, 'subheader_ab'), 
        get_text(lang, 'subheader_learn')
    ])

    with t1:  # Chat Tab
        render_chat_tab(lang, TECHNIQUE_INFO, PIPELINE_PRESETS, vector_db, set_preset, get_selected_techs)

    with t2:  # A/B Testing Tab
        render_ab_tab(lang, TECHNIQUE_INFO, PIPELINE_PRESETS, vector_db)

    with t3:  # Learning Tab
        render_learn_tab(lang, TECHNIQUE_INFO, render_tech_flowchart)

# ==========================================
# TAB RENDERING FUNCTIONS (แยกออกมาเพื่อความชัดเจน)
# ==========================================
def render_chat_tab(lang, TECHNIQUE_INFO, PIPELINE_PRESETS, vector_db, set_preset, get_selected_techs):
    """Render the chat interface tab"""
    c_conf, c_chat = st.columns([0.35, 0.65])
    
    with c_conf:
        st.subheader(get_text(lang, 'subheader_config'))
        st.markdown(f"<div class='active-status'>{get_text(lang, 'active_strategy')}: {st.session_state['active_mode']}</div>", unsafe_allow_html=True)
        
        # Presets
        st.markdown(f"**{get_text(lang, 'presets')}**")
        pc1, pc2 = st.columns(2)
        for i, (k, v) in enumerate(PIPELINE_PRESETS.items()):
            col = pc1 if i % 2 == 0 else pc2
            if col.button(k, key=f"preset_{k}"):
                set_preset(k)
                st.rerun()
        
        st.markdown("---")
        
        # Manual Selection
        st.markdown(f"**{get_text(lang, 'manual')}**")
        all_techs = list(TECHNIQUE_INFO.keys())
        mid = len(all_techs) // 2
        cl, cr = st.columns(2)
        
        def make_callback():
            return lambda: setattr(st.session_state, "active_mode", "Custom Manual")
        
        with cl:
            for t in all_techs[:mid]:
                st.checkbox(t, key=f"chk_{t}", on_change=make_callback())
        with cr:
            for t in all_techs[mid:]:
                st.checkbox(t, key=f"chk_{t}", on_change=make_callback())

    with c_chat:
        chat_box = st.container(height=600)
        
        # Display messages
        with chat_box:
            for m in st.session_state.msgs:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"], unsafe_allow_html=True)
                    if "meta" in m:
                        meta = m['meta']
                        with st.expander(f"{get_text(lang, 'analysis')} ({meta['lat']:.2f}s | ${meta['cost']:.5f})"):
                            tabs = st.tabs([get_text(lang, 'logs'), get_text(lang, 'context')])
                            with tabs[0]:
                                for l in meta['logs']:
                                    st.markdown(f"<div class='log-entry'>{l}</div>", unsafe_allow_html=True)
                            with tabs[1]:
                                for d in meta['docs']:
                                    sc = d.metadata.get('score', 0)
                                    src = d.metadata.get('source_doc', 'Unknown')
                                    content_preview = d.page_content[:250]
                                    st.markdown(f"<div class='source-ref'><b>{src}</b> <span style='float:right;color:#059669'>Score: {sc:.1f}</span><br>{content_preview}...</div>", unsafe_allow_html=True)
        
        # Chat input
        if q := st.chat_input(get_text(lang, 'placeholder')):
            st.session_state.msgs.append({"role": "user", "content": q})
            st.rerun()
        
        # Process new message
        if st.session_state.msgs[-1]["role"] == "user":
            with chat_box:
                with st.chat_message("assistant"):
                    api_key = st.session_state["groq_api_key"]
                    with st.spinner(get_text(lang, 'running')):
                        from modules.rag_pipeline import perform_rag
                        
                        llm = get_cached_llm(api_key)  # Use cached LLM
                        techs = get_selected_techs()
                        ans, docs, lat, tok, cost, logs = perform_rag(
                            st.session_state.msgs[-1]["content"], 
                            vector_db, 
                            llm, 
                            techs
                        )
                        
                        final = f"{ans}\n\n---\n<small style='color:grey'>Strategy: {st.session_state['active_mode']}</small>"
                        st.markdown(final, unsafe_allow_html=True)
                        
                        st.session_state.msgs.append({
                            "role": "assistant", 
                            "content": final, 
                            "meta": {
                                "lat": lat, 
                                "docs": docs, 
                                "cost": cost, 
                                "logs": logs
                            }
                        })
                        st.rerun()

def render_ab_tab(lang, TECHNIQUE_INFO, PIPELINE_PRESETS, vector_db):
    """Render A/B testing tab"""
    st.subheader(get_text(lang, 'subheader_ab'))
    c1, c2 = st.columns(2)
    
    def render_ab_col(prefix, title, col):
        with col:
            st.markdown(f"**{title}**")
            if f"{prefix}_mode" not in st.session_state:
                st.session_state[f"{prefix}_mode"] = "Custom"
            
            cols = st.columns(2)
            preset_keys = list(PIPELINE_PRESETS.keys())
            for i, k in enumerate(preset_keys):
                target_col = cols[i % 2]
                if target_col.button(k, key=f"btn_{prefix}_{k}"):
                    st.session_state[f"{prefix}_mode"] = k
                    for t in TECHNIQUE_INFO:
                        st.session_state[f"{prefix}_{t}"] = (t in PIPELINE_PRESETS[k]['techs'])
                    st.rerun()
            
            with st.expander("Customize"):
                selected = []
                for t in TECHNIQUE_INFO:
                    if st.checkbox(t, key=f"{prefix}_{t}"):
                        selected.append(t)
                return selected
    
    techs_a = render_ab_col("pipe_a", "Pipeline A", c1)
    techs_b = render_ab_col("pipe_b", "Pipeline B", c2)
    
    st.divider()
    q_ab = st.text_input("Query", key="ab_query")
    
    if st.button(get_text(lang, 'btn_compare'), type="primary") and q_ab:
        from modules.rag_pipeline import perform_rag
        
        api_key = st.session_state["groq_api_key"]
        llm = get_cached_llm(api_key)  # Use cached LLM
        ca, cb = st.columns(2)
        
        def run_side(col, techs, label):
            with col:
                st.markdown(f"### {label}")
                with st.spinner("Processing..."):
                    a, d, l, t, c, logs = perform_rag(q_ab, vector_db, llm, techs)
                    st.markdown(a)
                    st.caption(f"⏱️ {l:.2f}s | 💰 ${c:.5f}")
                    with st.expander("Logs"):
                        for log in logs:
                            st.code(log, language="text")
        
        run_side(ca, techs_a, "Pipeline A")
        run_side(cb, techs_b, "Pipeline B")

def render_learn_tab(lang, TECHNIQUE_INFO, render_tech_flowchart):
    """Render learning/tutorial tab"""
    st.header(get_text(lang, 'subheader_learn'))
    st.markdown(get_text(lang, 'learn_intro'))
    st.divider()
    
    all_techs = list(TECHNIQUE_INFO.keys())
    for i, tech_name in enumerate(all_techs):
        lesson = get_lesson(lang, tech_name)
        
        st.markdown(f"""
        <div class="lesson-container">
            <div class="lesson-header">
                <div class="lesson-number">{i+1}</div>
                <div class="lesson-title">{tech_name} ({lesson.get('concept', '')})</div>
            </div>
            <div><b>Problem:</b> {lesson.get('problem', '')}</div>
            <div class="process-box"><b>Process Flow:</b><br>{lesson.get('process', '')}</div>
            <div style="font-size:0.9em; color:#64748b; margin-top:10px;">
                <b>Technical Implementation:</b> {lesson.get('technical', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        render_tech_flowchart(tech_name)
        st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# ==========================================
# MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    if not st.session_state["groq_api_key"]:
        render_welcome_page()
    else:
        render_dashboard()