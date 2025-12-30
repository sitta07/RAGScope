import streamlit as st
import time

# --- Modular Imports ---
from modules.config import TECHNIQUE_INFO, PIPELINE_PRESETS
from modules.database import load_vector_db, get_full_file_content, get_file_list
from modules.llm import get_llm
from modules.rag_pipeline import perform_rag
from modules.languages import get_text, get_lesson
from modules.visuals import render_tech_flowchart

# --- Page Config ---
st.set_page_config(page_title="RAGScope Pro", page_icon="", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    /* 🔥 HIDDEN STREAMLIT HEADER 🔥 */
    /* ซ่อนแถบด้านบนสุด (Deploy button & Menu) */
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* ขยับเนื้อหาขึ้นไปชิดขอบจอสุดๆ (เพราะไม่มี Header แล้ว) */
    .block-container { padding-top: 1rem !important; }
    
    /* ปรับแต่งปุ่มกดทั่วไป */
    div.stButton > button { 
        width: 100%; border-radius: 8px; font-weight: 600; height: 3.2em; 
        background-color: #f8fafc; border: 1px solid #cbd5e1; color: #334155;
        transition: all 0.2s;
    }
    div.stButton > button:hover { background-color: #e2e8f0; transform: translateY(-1px); }
    
    /* Custom Title Class */
    .custom-title { 
        font-size: 2.5rem; font-weight: 800; color: #1e293b; 
        margin: 0; padding: 0; line-height: 1.2;
    }
    .custom-welcome-title {
        font-size: 3.5rem; font-weight: 800; color: #1e293b; 
        text-align: center; margin-top: 20px;
    }
    
    /* Welcome Styles */
    .welcome-subtitle { font-size: 1.3rem; color: #64748b; text-align: center; margin-bottom: 3rem;}
    .feature-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; height: 100%; }
    .feature-icon { font-size: 2.5rem; margin-bottom: 15px; }
    .feature-title { font-weight: bold; color: #0f172a; font-size: 1.1rem; margin-bottom: 8px; }
    .feature-desc { font-size: 0.95rem; color: #475569; line-height: 1.6; }
    
    /* Dashboard Styles */
    .active-status { background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 12px; border-radius: 6px; text-align: center; font-weight: 600; margin-bottom: 20px; }
    .source-ref { font-size: 0.85em; background: #fff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #10b981; }
    .log-entry { font-family: 'Courier New', monospace; font-size: 0.8em; background: #f1f5f9; padding: 8px; margin-bottom: 4px; border-radius: 4px; }
    .lesson-container { border: 1px solid #e2e8f0; border-radius: 8px; padding: 25px; background-color: #ffffff; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .process-box { background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 0 4px 4px 0; white-space: pre-line; color: #334155; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "groq_api_key" not in st.session_state: st.session_state["groq_api_key"] = ""
if "lang" not in st.session_state: st.session_state["lang"] = "en"

# ==========================================
# 🏠 PART 1: WELCOME PAGE
# ==========================================
def render_welcome_page():
    # --- Top Bar ---
    c_spacer, c_lang = st.columns([0.85, 0.15])
    with c_lang:
        l_opt = st.selectbox("Lang", ["🇺🇸 EN", "🇹🇭 TH"], 
                             index=0 if st.session_state["lang"]=="en" else 1, 
                             key="welcome_lang", label_visibility="collapsed")
        new_lang = "en" if "🇺🇸" in l_opt else "th"
        if new_lang != st.session_state["lang"]:
            st.session_state["lang"] = new_lang
            st.rerun()

    lang = st.session_state["lang"]
    
    # Hero Section
    st.markdown(f"<div class='custom-welcome-title'> {get_text(lang, 'welcome_title')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='welcome-subtitle'>{get_text(lang, 'welcome_sub')}</div>", unsafe_allow_html=True)

    # Features
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class='feature-card'>
            <div class='feature-icon'></div>
            <div class='feature-title'>{get_text(lang, 'feat_1_title')}</div>
            <div class='feature-desc'>{get_text(lang, 'feat_1_desc')}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='feature-card'>
            <div class='feature-icon'></div>
            <div class='feature-title'>{get_text(lang, 'feat_2_title')}</div>
            <div class='feature-desc'>{get_text(lang, 'feat_2_desc')}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='feature-card'>
            <div class='feature-icon'></div>
            <div class='feature-title'>{get_text(lang, 'feat_3_title')}</div>
            <div class='feature-desc'>{get_text(lang, 'feat_3_desc')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Login
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.markdown(f"#### {get_text(lang, 'get_started')}")
        st.info(get_text(lang, 'api_req'))
        api_input = st.text_input(get_text(lang, 'enter_key'), type="password", placeholder="gsk_...")
        
        if st.button(get_text(lang, 'btn_enter'), type="primary"):
            if api_input.startswith("gsk_"):
                st.session_state["groq_api_key"] = api_input
                st.success(get_text(lang, 'access_granted'))
                time.sleep(1)
                st.rerun()
            else:
                st.error(get_text(lang, 'invalid_key'))

# ==========================================
# 🖥️ PART 2: DASHBOARD
# ==========================================
def render_dashboard():
    # --- Top Bar ---
    c_title, c_lang = st.columns([0.85, 0.15])
    
    with c_title:
        st.markdown(f"<div class='custom-title'>{get_text(st.session_state['lang'], 'title')}</div>", unsafe_allow_html=True)
        
    with c_lang:
        l_opt = st.selectbox("Lang", ["🇺🇸 EN", "🇹🇭 TH"], 
                             index=0 if st.session_state["lang"]=="en" else 1, 
                             key="dash_lang", label_visibility="collapsed")
        new_lang = "en" if "🇺🇸" in l_opt else "th"
        if new_lang != st.session_state["lang"]:
            st.session_state["lang"] = new_lang
            st.rerun()
            
    lang = st.session_state["lang"]

    # --- Sidebar & Logic ---
    with st.sidebar:
        st.header("System Config")
        st.success("✅ API Key Configured")
        if st.button("Logout"):
            st.session_state["groq_api_key"] = ""
            st.rerun()
        st.markdown("---")
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
    def set_preset(name):
        st.session_state["active_mode"] = name
        for t in TECHNIQUE_INFO: st.session_state[f"chk_{t}"] = False
        for t in PIPELINE_PRESETS[name]["techs"]: st.session_state[f"chk_{t}"] = True

    def get_selected_techs():
        return [t for t in TECHNIQUE_INFO if st.session_state.get(f"chk_{t}", False)]

    t1, t2, t3 = st.tabs([get_text(lang, 'subheader_chat'), get_text(lang, 'subheader_ab'), get_text(lang, 'subheader_learn')])

    # Tab 1: Chat
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
                if col.button(k): set_preset(k); st.rerun()
            st.markdown("---")
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
                        api_key = st.session_state["groq_api_key"]
                        with st.spinner(get_text(lang, 'running')):
                            llm = get_llm(api_key)
                            techs = get_selected_techs()
                            ans, docs, lat, tok, cost, logs = perform_rag(st.session_state.msgs[-1]["content"], vector_db, llm, techs)
                            final = f"{ans}\n\n---\n<small style='color:grey'>Strategy: {st.session_state['active_mode']}</small>"
                            st.markdown(final, unsafe_allow_html=True)
                            st.session_state.msgs.append({"role": "assistant", "content": final, "meta": {"lat": lat, "docs": docs, "cost": cost, "logs": logs}})
                            st.rerun()

    # Tab 2: A/B
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
            api_key = st.session_state["groq_api_key"]
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

    # Tab 3: Learn
    with t3:
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
                <div><b> Problem:</b> {lesson.get('problem', '')}</div>
                <div class="process-box"><b> Process Flow:</b><br>{lesson.get('process', '')}</div>
                <div style="font-size:0.9em; color:#64748b; margin-top:10px;">
                    <b>⚙️ Technical Implementation:</b> {lesson.get('technical', '')}
                </div>
            </div>""", unsafe_allow_html=True)
            render_tech_flowchart(tech_name)
            st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# Main
if not st.session_state["groq_api_key"]:
    render_welcome_page()
else:
    render_dashboard()