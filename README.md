Markdown

# RAG Insight & Observability Platform

A Professional RAG (Retrieval-Augmented Generation) visualization tool built with Streamlit. This project demonstrates how different retrieval strategies perform side-by-side using real-time visualization.

## Key Features
- **Split-Screen Comparison:** Compare Basic Vector Search vs. MMR (Maximal Marginal Relevance).
- **Search Radar:** Interactive 2D scatter plot (UMAP) to visualize query semantics vs. document knowledge base.
- **100% Free Stack:** Powered by Streamlit, ChromaDB, and Groq API (Llama3-70b).

## Tech Stack
- **Frontend:** Streamlit, Plotly
- **LLM:** Groq API (Llama3-70b)
- **Vector DB:** ChromaDB (Persistent)
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **Orchestration:** LangChain

## Installation

1. **Clone the repository**
```bash
git clone ..
cd rag-observability-platform
```

2. **Create Virtual Environment**
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Prepare Data (Ingestion)**
```bash
python src/ingest.py
```
5. **Run the App**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m streamlit run src/app.py
```
