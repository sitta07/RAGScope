import streamlit as st
import plotly.express as px
from utils import (
    load_vector_db, 
    get_all_documents_metadata, 
    get_llm, 
    perform_rag, 
    TECHNIQUE_DESCRIPTIONS 
)

st.set_page_config(page_title="RAGScope Pro", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
    .stCheckbox { margin-top: 5px; } 
    .tech-card { 
        background-color: #f8f9fa; 
        padding: 10px; 
        border-radius: 8px; 
        margin-bottom: 10px; 
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Groq API Key", type="password")
    vector_db = load_vector_db()
    df_meta = get_all_documents_metadata(vector_db)

# --- Header ---
st.title("🧠 RAGScope: Modular Pipeline")

# --- 🎛️ Mode Selection (Switch 2 โหมดตรงนี้) ---
mode = st.radio(
    "Select Mode:", 
    ["1. Normal Chat (Single Pipeline)", "2. Compare Strategies (A/B Testing)"],
    horizontal=True
)
st.divider()

# Input Query (ใช้ร่วมกัน)
query = st.text_input("💬 Enter your question:", value="What is the remote work policy?")

# --- 🛠️ Helper Function: สร้าง Checkbox สวยๆ ---
def render_technique_selector(key_prefix):
    """สร้างรายการ Checkbox พร้อมคำอธิบาย"""
    selected_techniques = []
    
    st.markdown("### 🛠️ Configure Pipeline")
    st.caption("Select techniques to enable in this pipeline:")
    
    # วนลูปสร้าง Checkbox ทีละอัน
    for tech_name, description in TECHNIQUE_DESCRIPTIONS.items():
        # ใช้ container เพื่อจัดกลุ่มให้ดูเป็นก้อนเดียวกัน (Card)
        with st.container():
            # แบ่งคอลัมน์: ซ้าย(Checkbox) ขวา(Text)
            c1, c2 = st.columns([0.05, 0.95]) 
            with c1:
                # Checkbox
                is_checked = st.checkbox("", key=f"{key_prefix}_{tech_name}")
            with c2:
                # Title & Description
                st.markdown(f"**{tech_name}**")
                st.caption(description)
                
            if is_checked:
                selected_techniques.append(tech_name)
        
        # เส้นคั่นบางๆ ระหว่างตัวเลือก
        st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
            
    return selected_techniques

# --- 🚀 Logic การแสดงผลตามโหมด ---

if "Normal Chat" in mode:
    # === MODE 1: SINGLE PIPELINE ===
    col_input, col_result = st.columns([0.4, 0.6])
    
    with col_input:
        # เรียกใช้ฟังก์ชันสร้าง Checkbox
        selected_techs = render_technique_selector(key_prefix="single")
        
        if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
            if not api_key:
                st.error("Please enter Groq API Key first!")
            else:
                with st.spinner("Processing..."):
                    llm = get_llm(api_key)
                    ans, docs, lat = perform_rag(query, vector_db, llm, selected_techs)
                    
                    # Store Result in Session State (Optional, for simplicity just show here)
                    st.session_state['result_single'] = (ans, docs, lat, selected_techs)

    with col_result:
        st.subheader("📝 Result")
        if 'result_single' in st.session_state:
            ans, docs, lat, used_techs = st.session_state['result_single']
            
            # Show Active Tags
            st.markdown("Active Techniques:")
            st.write(" ".join([f"`{t}`" for t in used_techs]))
            
            st.success(ans)
            st.metric("Latency", f"{lat:.4f}s")
            
            with st.expander("📄 Source Documents"):
                for d in docs:
                    st.markdown(f"**Source:** {d.metadata.get('source_doc', 'Unknown')}")
                    st.caption(d.page_content)
                    st.divider()

else:
    # === MODE 2: COMPARE STRATEGIES ===
    c1, c2 = st.columns(2)
    
    # --- Pipeline A ---
    with c1:
        st.header("🟢 Pipeline A")
        techs_a = render_technique_selector(key_prefix="pipeline_a")
        run_a = st.button("Run Pipeline A", use_container_width=True)
    
    # --- Pipeline B ---
    with c2:
        st.header("🔵 Pipeline B")
        techs_b = render_technique_selector(key_prefix="pipeline_b")
        run_b = st.button("Run Pipeline B", use_container_width=True)
    
    # --- Display Results Side-by-Side ---
    st.divider()
    res_c1, res_c2 = st.columns(2)
    
    if run_a or run_b:
        llm = get_llm(api_key)
        
        # Run A
        if run_a:
            with res_c1:
                with st.spinner("Running A..."):
                    ans_a, docs_a, lat_a = perform_rag(query, vector_db, llm, techs_a)
                    st.success(f"**Answer A:**\n\n{ans_a}")
                    st.metric("Latency A", f"{lat_a:.4f}s")
                    
        # Run B
        if run_b:
            with res_c2:
                with st.spinner("Running B..."):
                    ans_b, docs_b, lat_b = perform_rag(query, vector_db, llm, techs_b)
                    st.info(f"**Answer B:**\n\n{ans_b}")
                    st.metric("Latency B", f"{lat_b:.4f}s")

# --- Visualization (Global) ---
with st.expander("📡 Knowledge Base Radar", expanded=False):
    fig = px.scatter(df_meta, x='umap_x', y='umap_y', hover_data=['source_doc'], title="Embedding Space")
    st.plotly_chart(fig, use_container_width=True)