import streamlit as st
import random

# --- Imports from New Modules ---
from modules.config import TECHNIQUE_INFO, PIPELINE_PRESETS
from modules.database import load_vector_db, get_full_file_content, get_file_list
from modules.llm import get_llm
from modules.rag_pipeline import perform_rag

# --- Page Configuration ---
st.set_page_config(page_title="RAGScope Pro", page_icon="⚡", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    /* Buttons */
    div.stButton > button { 
        width: 100%; border-radius: 6px; font-weight: 500; height: 3em; 
        transition: all 0.2s;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    /* Active Status Box */
    .active-status { 
        background-color: #ecfdf5; border: 1px solid #10b981; color: #064e3b; 
        padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;
    }
    
    /* Source Card */
    .source-card { 
        background: #fff; padding: 12px; border: 1px solid #e5e7eb; 
        border-left: 4px solid #ef4444; margin-bottom: 8px; border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Logs Box */
    .log-box { 
        font-family: 'Courier New', monospace; font-size: 0.85em; 
        background: #f8fafc; padding: 10px; border-radius: 4px; 
        color: #334155; border: 1px solid #e2e8f0; margin-bottom: 5px; 
    }
    
    /* Grid Text */
    .grid-desc { font-size: 0.75em; color: #64748b; line-height: 1.3; }
    
    /* Learn RAG Section */
    .lesson-box {
        background-color: #f9fafb; border: 1px solid #e5e7eb; padding: 20px;
        border-radius: 8px; margin-bottom: 20px;
    }
    .lesson-header { color: #1e40af; font-size: 1.1em; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def set_preset(name):
    st.session_state["active_mode"] = name
    for t in TECHNIQUE_INFO: 
        st.session_state[f"chk_{t}"] = False
    for t in PIPELINE_PRESETS[name]["techs"]: 
        st.session_state[f"chk_{t}"] = True

def get_selected_techs():
    return [t for t in TECHNIQUE_INFO if st.session_state.get(f"chk_{t}", False)]

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ System Control")
    api_key = st.text_input("Groq API Key", type="password")
    
    db_name = st.selectbox("Database Collection", ["harry_potter_lore", "rag_demo"])
    
    try:
        vector_db = load_vector_db(db_name)
        st.success(f"Connected to {db_name}")
    except Exception as e:
        st.error(f"DB Error: {e}")
    
    with st.expander("📂 Data Explorer (Full Text)"):
        files = get_file_list()
        if files:
            f_sel = st.selectbox("Select File:", files)
            if st.button("Read Content"):
                content = get_full_file_content(f_sel)
                st.text_area("File Content", content, height=300)
        else:
            st.warning("No .txt files found.")

# --- MAIN TABS ---
t1, t2, t3 = st.tabs(["💬 Chat & Debug", "⚖️ A/B Testing", "🎓 Learn RAG"])

# ==========================================
# TAB 1: CHAT INTERFACE (With Scrollbar)
# ==========================================
with t1:
    c_conf, c_chat = st.columns([0.35, 0.65])
    
    # --- Left: Configuration ---
    with c_conf:
        st.subheader("Pipeline Configuration")
        
        if "active_mode" not in st.session_state: st.session_state["active_mode"] = "Custom Manual"
        st.markdown(f"<div class='active-status'>✅ Strategy: {st.session_state['active_mode']}</div>", unsafe_allow_html=True)
        
        st.caption("⚡ Quick Presets")
        cols = st.columns(2)
        for i, (k, v) in enumerate(PIPELINE_PRESETS.items()):
            if cols[i%2].button(k, help=v['desc']): 
                set_preset(k)
                st.rerun()
        
        st.markdown("---")
        
        st.caption("🎛️ Manual Customization")
        g_cols = st.columns(2)
        for i, (k, v) in enumerate(TECHNIQUE_INFO.items()):
            with g_cols[i%2]:
                def on_change_manual(): st.session_state["active_mode"] = "Custom Manual"
                st.checkbox(k, key=f"chk_{k}", on_change=on_change_manual)
                st.markdown(f"<div class='grid-desc'>{v['desc']}</div><div style='height:12px'></div>", unsafe_allow_html=True)

    # --- Right: Chat (Fixed Height Container) ---
    with c_chat:
        st.subheader("RAGScope Chat")
        
        # Initialize History
        if "msgs" not in st.session_state: 
            st.session_state.msgs = [{"role": "assistant", "content": "Ready. Configure the pipeline and ask away!"}]
        
        # 🔥 SCROLLABLE CONTAINER START 🔥
        # กำหนดความสูง 550px ถ้าข้อความเกินจะมี Scrollbar ขึ้นมาเอง
        chat_container = st.container(height=550)
        
        with chat_container:
            for m in st.session_state.msgs:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"], unsafe_allow_html=True)
                    
                    if "meta" in m:
                        meta = m['meta']
                        with st.expander(f"📊 Analysis (Latency: {meta['lat']:.2f}s | Cost: ${meta['cost']:.5f})"):
                            tab_logs, tab_ctx = st.tabs(["🛠️ Execution Logs", "📄 Retrieved Context"])
                            
                            with tab_logs: 
                                for log in meta['logs']: 
                                    st.markdown(f"<div class='log-box'>{log}</div>", unsafe_allow_html=True)
                            
                            with tab_ctx:
                                for d in meta['docs']:
                                    score = d.metadata.get('score', 0)
                                    st.markdown(
                                        f"<div class='source-card'>"
                                        f"<b>Source: {d.metadata.get('source_doc', 'Unknown')}</b> "
                                        f"<span style='float:right; color:#10b981; font-weight:bold'>Score: {score:.1f}</span>"
                                        f"<br><small style='color:#555'>{d.page_content[:300]}...</small>"
                                        f"</div>", 
                                        unsafe_allow_html=True
                                    )
        # 🔥 SCROLLABLE CONTAINER END 🔥

        # Input Area (อยู่นอก Container เพื่อให้ติดด้านล่างตลอด)
        if q := st.chat_input("Ask a question about Harry Potter..."):
            st.session_state.msgs.append({"role": "user", "content": q})
            # บังคับ Rerun เพื่อให้ข้อความ User ไปโผล่ใน Container ก่อน
            st.rerun()

        # Logic ส่วนประมวลผล (ทำงานหลัง Rerun แล้วเจอข้อความใหม่จาก User)
        if st.session_state.msgs[-1]["role"] == "user":
            last_msg = st.session_state.msgs[-1]["content"]
            # เช็คว่าข้อความล่าสุดยังไม่ได้ตอบ (ป้องกันรันซ้ำ)
            if len(st.session_state.msgs) % 2 == 0: 
                with chat_container: # แสดง Spinner ในกล่องแชท
                    with st.chat_message("assistant"):
                        if not api_key:
                            st.error("Please enter your Groq API Key.")
                        else:
                            with st.spinner("Running RAG Pipeline..."):
                                llm = get_llm(api_key)
                                selected_techs = get_selected_techs()
                                ans, docs, lat, tok, cost, logs = perform_rag(last_msg, vector_db, llm, selected_techs)
                                
                                strategy_name = st.session_state["active_mode"]
                                tech_list = ", ".join(selected_techs)
                                final_response = f"{ans}\n\n---\n<small style='color:grey'>**Strategy:** {strategy_name} [{tech_list}]</small>"
                                
                                st.markdown(final_response, unsafe_allow_html=True)
                                
                                st.session_state.msgs.append({
                                    "role": "assistant", 
                                    "content": final_response,
                                    "meta": {"lat": lat, "docs": docs, "cost": cost, "logs": logs}
                                })
                                st.rerun()

# ==========================================
# TAB 2: A/B TESTING
# ==========================================
with t2:
    st.title("⚖️ A/B Strategy Comparison")
    st.markdown("Compare two different RAG configurations side-by-side.")
    
    col_a, col_b = st.columns(2)
    
    def render_mini_builder(prefix):
        if f"{prefix}_mode" not in st.session_state: st.session_state[f"{prefix}_mode"] = "Custom"
        st.info(f"Pipeline {prefix.upper()[-1]}: {st.session_state[f'{prefix}_mode']}")
        
        p_cols = st.columns(2)
        for k in PIPELINE_PRESETS:
            if p_cols[0].button(f"Load {k}", key=f"btn_{prefix}_{k}"):
                 st.session_state[f"{prefix}_mode"] = k
                 for t in TECHNIQUE_INFO: 
                     st.session_state[f"{prefix}_{t}"] = (t in PIPELINE_PRESETS[k]['techs'])
                 st.rerun()
        
        with st.expander("Customize Configuration"):
            selected = []
            for t in TECHNIQUE_INFO:
                if f"{prefix}_{t}" not in st.session_state: st.session_state[f"{prefix}_{t}"] = False
                if st.checkbox(t, key=f"{prefix}_{t}"): selected.append(t)
            return selected

    with col_a: 
        st.subheader("🟢 Pipeline A")
        techs_a = render_mini_builder("pipe_a")
    with col_b: 
        st.subheader("🔵 Pipeline B")
        techs_b = render_mini_builder("pipe_b")

    st.divider()
    query_comp = st.text_input("Enter Comparison Query:", "Who is Harry Potter?")
    
    if st.button("⚔️ Run Comparison", type="primary"):
        if not api_key: 
            st.error("No API Key provided.")
        else:
            llm = get_llm(api_key)
            res_a, res_b = st.columns(2)
            
            def run_pipeline_view(col, techs, name):
                with col:
                    with st.spinner(f"Running {name}..."):
                        ans, docs, lat, tok, cost, logs = perform_rag(query_comp, vector_db, llm, techs)
                        st.success("Complete")
                        st.markdown(ans)
                        st.caption(f"⏱️ {lat:.4f}s | 💰 ${cost:.5f}")
                        with st.expander("View Logs"):
                            for l in logs: st.code(l, language='text')
            
            run_pipeline_view(res_a, techs_a, "Pipeline A")
            run_pipeline_view(res_b, techs_b, "Pipeline B")

# ==========================================
# TAB 3: LEARN RAG (Detailed Version)
# ==========================================
with t3:
    st.title("🎓 RAG Academy: Deep Dive")
    st.markdown("""
    ยินดีต้อนรับสู่คลาสเรียน RAGScope Academy! ในหน้านี้เราจะเจาะลึกเทคนิคทั้ง 8 อย่างที่ระบบใช้อย่างละเอียด 
    เพื่อให้คุณเข้าใจไม่เพียงแค่ "มันคืออะไร" แต่รวมถึง "ทำไมต้องใช้" และ "มันทำงานอย่างไร"
    """)
    st.divider()
    
    # Detailed Explanation Data
    lessons = {
        "Hybrid Search": {
            "icon": "🔍",
            "concept": "การค้นหาแบบผสมผสาน (Keyword + Vector)",
            "problem": "การค้นหาแบบเก่า (Keyword) แม่นเรื่องคำเฉพาะแต่ไม่เข้าใจบริบท ส่วนการค้นหาแบบใหม่ (Vector) เข้าใจบริบทแต่ชอบพลาดคำเฉพาะ (เช่น รหัสสินค้า, ชื่อเฉพาะ)",
            "analogy": "เปรียบเสมือนการจ้างนักสืบ 2 คนทำงานพร้อมกัน: \n1. **บรรณารักษ์ (Keyword):** วิ่งไปดูดัชนีท้ายเล่ม หาคำที่ตรงเป๊ะๆ \n2. **นักจิตวิทยา (Vector):** ไม่สนคำพูด แต่สน 'เจตนา' ของคุณ ว่าคุณกำลังมองหาอะไร \nเมื่อทั้งสองคนเอางานมารวมกัน คุณจึงได้ข้อมูลที่ครบถ้วนที่สุด",
            "technical": "ระบบจะรัน `BM25Retriever` (Sparse) และ `VectorStore` (Dense) ขนานกัน แล้วนำผลลัพธ์มาทำ Weighted Fusion เพื่อจัดลำดับความสำคัญใหม่"
        },
        "Reranking": {
            "icon": "🥇",
            "concept": "การจัดลำดับความสำคัญใหม่ด้วย AI (Re-scoring)",
            "problem": "ขั้นตอนการค้นหา (Retrieval) เน้นความเร็ว ทำให้มักจะได้เอกสารขยะติดมาด้วย หรือเอกสารที่ดีที่สุดอาจจะอยู่อันดับที่ 5-10 ทำให้ AI ไม่ได้อ่านมัน",
            "analogy": "เหมือนการประกวดนางงาม รอบแรก (Retrieval) คือการคัดคน 100 คนจากรูปถ่ายอย่างรวดเร็ว ซึ่งอาจมีพลาดบ้าง \nรอบที่สอง (**Reranking**) คือการให้กรรมการ (AI) มานั่งสัมภาษณ์ 10 คนสุดท้ายอย่างละเอียด เพื่อหาคนมงลงตัวจริงเพียงหนึ่งเดียว",
            "technical": "เราใช้ LLM หรือ Cross-Encoder Model อ่าน Query คู่กับ Document ทีละใบ แล้วให้คะแนนความเกี่ยวข้อง (0-10) จากนั้นเรียงลำดับใหม่และตัดให้เหลือแค่ Top-N ที่ดีที่สุด"
        },
        "Parent-Document": {
            "icon": "📄",
            "concept": "การดึงข้อมูลบริบทแม่ (Full Context Retrieval)",
            "problem": "AI เก็บข้อมูลเป็นชิ้นเล็กๆ (Chunks) เพื่อให้ค้นหาเจอได้ง่าย แต่เวลาดึงมาใช้ บางทีได้มาแค่ประโยคสั้นๆ ที่ขาดประธาน หรือขาดบริบทก่อนหน้า/ตามหลัง ทำให้ AI ตอบมั่ว",
            "analogy": "เหมือนคุณเจอประโยคเด็ดในหนังสือที่ถูกไฮไลท์ไว้ (Chunk) แทนที่คุณจะฉีกหน้านั้นมาแค่ประโยคเดียว คุณกลับ **ถ่ายเอกสารทั้งหน้านั้น (Parent Document)** มาด้วย เพื่อให้รู้ว่าใครพูด พูดที่ไหน และพูดทำไม",
            "technical": "ตอน Ingest เราเก็บ Metadata ID ของไฟล์ต้นฉบับไว้ เมื่อค้นหาเจอ Chunk เล็กๆ ระบบจะใช้ ID นั้นวิ่งไปโหลดไฟล์ต้นฉบับเต็มๆ จาก Disk มาแทนที่ Chunk นั้นก่อนส่งให้ AI"
        },
        "Multi-Query": {
            "icon": "🔀",
            "concept": "การแตกคำถามหลากหลายมุมมอง (Query Expansion)",
            "problem": "ผู้ใช้งานมักถามคำถามไม่เก่ง ใช้คำกำกวม หรือถามสั้นเกินไป ทำให้ Database หาไม่เจอ",
            "analogy": "เหมือนคุณไปถามทางคนแถวนั้น ถ้าคุณถามแค่ว่า 'ไปไง?' เขาอาจงง \nแต่ถ้าคุณมี AI ช่วย AI จะตะโกนถามแทนคุณ 3 แบบ: 'ทางไปวัดพระแก้ว?', 'รถเมล์สายไหนผ่านสนามหลวง?', 'แผนที่เขตพระนคร' \nการถามหลายแบบทำให้โอกาสได้รับคำตอบที่ถูกต้องมีสูงขึ้นมหาศาล",
            "technical": "ใช้ LLM สร้างคำถาม Variations 3-5 รูปแบบ แล้วนำทุกคำถามไปค้นหาใน Database พร้อมกัน (Parallel Execution) แล้วรวมผลลัพธ์ทั้งหมดเข้าด้วยกัน"
        },
        "Sub-Query": {
            "icon": "🧱",
            "concept": "การแตกปัญหาใหญ่เป็นปัญหาย่อย (Decomposition)",
            "problem": "คำถามซับซ้อน เช่น 'เปรียบเทียบ A กับ B' หรือคำถามที่ต้องใช้ตรรกะหลายชั้น (Multi-hop) มักทำให้การค้นหาทีเดียวล้มเหลว",
            "analogy": "เหมือน Project Manager ที่เจอโปรเจกต์ใหญ่ เขาจะไม่ทำรวดเดียว แต่จะแตกเป็น Task ย่อยๆ: \n1. หาข้อมูล A \n2. หาข้อมูล B \n3. เอามาเทียบกัน \nการทำทีละขั้นทำให้งานสำเร็จได้ง่ายกว่า",
            "technical": "ใช้ LLM วิเคราะห์โครงสร้างคำถาม แล้วแตกเป็น Sequential Steps ระบบจะค้นหาข้อมูลสำหรับ Step 1 ก่อน แล้วค่อยไป Step 2 จนครบ"
        },
        "HyDE": {
            "icon": "👻",
            "concept": "Hypothetical Document Embeddings (มโนก่อนหา)",
            "problem": "บางครั้งคำถาม (Question) กับคำตอบ (Document) ใช้คำศัพท์คนละชุดกันเลย ทำให้ Vector Search หาไม่เจอ (เช่น ถามอาการ แต่เอกสารเขียนชื่อโรค)",
            "analogy": "เหมือนคุณไม่รู้คำตอบ แต่คุณพอนึกภาพออกว่าคำตอบหน้าตาควรเป็นยังไง \nคุณจึงให้ AI **'เขียนคำตอบปลอมๆ'** ขึ้นมาก่อน แล้วเอาคำตอบปลอมนั้นไปเดินหาเอกสารจริงที่หน้าตาคล้ายๆ กัน",
            "technical": "ใช้ LLM สร้าง Fake Answer จาก Query แล้วนำ Vector ของ Fake Answer ไปค้นหาใน Database ซึ่งมักจะเจอเอกสารจริงได้ดีกว่าใช้คำถามดิบๆ"
        },
        "Context Compression": {
            "icon": "✂️",
            "concept": "การย่อความบริบท (Information Extraction)",
            "problem": "เอกสารที่ค้นเจออาจจะยาวมาก และมีน้ำเยอะ ถ้าส่งทั้งหมดไปให้ AI ตอบ จะเปลือง Token และอาจทำให้ AI หลุดประเด็น",
            "analogy": "เหมือนการใช้ **ปากกาไฮไลท์** ขีดเน้นเฉพาะใจความสำคัญในหนังสือเรียน ก่อนจะเข้าห้องสอบ คุณไม่ได้จำทั้งเล่ม แต่จำเฉพาะส่วนที่ขีดเส้นใต้ไว้",
            "technical": "ใช้ LLM อีกตัวหนึ่ง อ่านเอกสารที่ค้นเจอ แล้วสั่งให้ 'คัดลอกเฉพาะประโยคที่เกี่ยวข้องกับคำถาม' ออกมา ส่วนที่ไม่เกี่ยวให้ทิ้งไป"
        },
        "Query Rewriting": {
            "icon": "🔄",
            "concept": "การเรียบเรียงคำถามใหม่ (Query Refinement)",
            "problem": "ภาษาพูดของมนุษย์นั้นยุ่งเหยิง เต็มไปด้วยคำฟุ่มเฟือย หรือคำสรรพนามที่ไม่ชัดเจน",
            "analogy": "เปรียบเสมือน **ล่ามแปลภาษา** ที่คอยฟังคำบ่นของคุณ แล้วแปลเป็นคำสั่งที่กระชับ ชัดเจน และตรงประเด็น เพื่อสั่งงานหุ่นยนต์",
            "technical": "ส่งคำถามเดิมเข้า LLM พร้อมคำสั่ง 'Rewrite this for search engine optimization' เพื่อให้ได้ Keyword ที่คมชัดที่สุดก่อนเริ่มกระบวนการค้นหา"
        }
    }
    
    # Render Lesson Grid
    cols = st.columns(2)
    for i, (key, data) in enumerate(lessons.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="lesson-box">
                <div class="lesson-header">{data['icon']} {key} ({data['concept']})</div>
                <p><b>🚨 ปัญหา:</b> {data['problem']}</p>
                <p><b>💡 เปรียบเทียบ:</b> {data['analogy'].replace(chr(10), '<br>')}</p>
                <hr>
                <p style="font-size:0.9em; color:#4b5563"><b>⚙️ เชิงเทคนิค:</b> {data['technical']}</p>
            </div>
            """, unsafe_allow_html=True)