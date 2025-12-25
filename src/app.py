import streamlit as st
import plotly.express as px
import pandas as pd
from utils import load_vector_db, get_all_documents_metadata, get_llm, perform_rag

# --- Page Config ---
st.set_page_config(
    page_title="RAG Insight Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Look ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.markdown("[Get Free Key Here](https://console.groq.com/keys)")
    
    st.divider()
    
    st.subheader("📁 Dataset Info")
    # Load DB & Data
    try:
        vector_db = load_vector_db()
        df_meta = get_all_documents_metadata(vector_db)
        
        unique_files = df_meta['source_doc'].unique() if not df_meta.empty else []
        selected_file = st.selectbox("Filter Visualization by Source", ["All"] + list(unique_files))
        
        st.info(f"Loaded {len(df_meta)} chunks from {len(unique_files)} documents.")
    except Exception as e:
        st.error(f"Error loading DB. Did you run ingest.py?\n{e}")
        st.stop()

# --- Main Area ---
st.title("RAG Insight & Observability Platform")
st.markdown("Compare Retrieval Strategies side-by-side with real-time visualization.")

# 1. Search Input
query = st.text_input("Enter your query:", placeholder="e.g., What is the refund policy?", value="What is the policy on remote work?")

# 2. Search Radar (The "Wow" Factor)
st.subheader("📡 Semantic Search Radar")
with st.expander("Show Visualization Details", expanded=True):
    # Filter Data for Plotting
    plot_df = df_meta.copy()
    if selected_file != "All":
        plot_df = plot_df[plot_df['source_doc'] == selected_file]

    # Create Base Plot (Gray dots)
    fig = px.scatter(
        plot_df, 
        x='umap_x', 
        y='umap_y', 
        hover_data=['source_doc'],
        color_discrete_sequence=['#e0e0e0'], # Gray for background
        opacity=0.5,
        title="Knowledge Base Universe (UMAP Projection)"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=400)

# 3. Execution & Comparison
if st.button("Run Analysis", type="primary") and query:
    llm = get_llm(groq_api_key)
    if not llm:
        st.warning("⚠️ Please provide a Groq API Key in the sidebar to generate answers. Running in Retrieval-Only mode.")

    col1, col2 = st.columns(2)

    # --- Left Panel: Basic Strategy ---
    with col1:
        st.markdown("### 🟢 Strategy A: Basic Similarity")
        answer_a, docs_a, latency_a = perform_rag(query, vector_db, llm, strategy="basic")
        
        st.success(f"Answer: {answer_a}")
        st.metric("Latency", f"{latency_a:.4f}s")
        
        with st.expander("📄 Retrieved Context (Top 4)"):
            for i, doc in enumerate(docs_a):
                st.markdown(f"**{i+1}. {doc.metadata['source_doc']}**")
                st.caption(doc.page_content[:200] + "...")

    # --- Right Panel: Advanced Strategy ---
    with col2:
        st.markdown("### 🔵 Strategy B: MMR (Maximal Marginal Relevance)")
        answer_b, docs_b, latency_b = perform_rag(query, vector_db, llm, strategy="advanced")
        
        st.success(f"Answer: {answer_b}")
        st.metric("Latency", f"{latency_b:.4f}s")
        
        with st.expander("Retrieved Context (Top 4)"):
            for i, doc in enumerate(docs_b):
                st.markdown(f"**{i+1}. {doc.metadata['source_doc']}**")
                st.caption(doc.page_content[:200] + "...")

    # --- Update Radar with Search Results ---
    # Highlight Retrieved Docs (Basic = Green, Advanced = Blue)
    
    # Prepare Data for highlighting
    retrieved_a_df = pd.DataFrame([d.metadata for d in docs_a])
    retrieved_b_df = pd.DataFrame([d.metadata for d in docs_b])
    
    if not retrieved_a_df.empty:
        fig.add_trace(px.scatter(retrieved_a_df, x='umap_x', y='umap_y', hover_data=['source_doc']).data[0])
        fig.data[-1].marker.color = '#2ecc71' # Green
        fig.data[-1].marker.size = 12
        fig.data[-1].name = 'Basic Retrieval'

    if not retrieved_b_df.empty:
        fig.add_trace(px.scatter(retrieved_b_df, x='umap_x', y='umap_y', hover_data=['source_doc']).data[0])
        fig.data[-1].marker.color = '#3498db' # Blue
        fig.data[-1].marker.symbol = 'diamond'
        fig.data[-1].marker.size = 12
        fig.data[-1].name = 'MMR Retrieval'

    st.plotly_chart(fig, use_container_width=True)

else:
    # Show default plot if not searched yet
    st.plotly_chart(fig, use_container_width=True)