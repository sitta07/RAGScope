import os

# Paths
DATA_FOLDER = "./data"
DB_PATH = "./processed_data/chroma_db"
COLLECTION_NAME = "harry_potter_lore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Technique Metadata (For internal logic mapping)
TECHNIQUE_INFO = {
    "Hybrid Search": {"pair_with": "Reranking"},
    "Reranking": {"pair_with": "Hybrid, Multi-Query"},
    "Parent-Document": {"pair_with": "Context Compression"},
    "Multi-Query": {"pair_with": "Reranking"},
    "Sub-Query": {"pair_with": "Reranking"},
    "HyDE": {"pair_with": "Hybrid"},
    "Context Compression": {"pair_with": "Parent-Document"},
    "Query Rewriting": {"pair_with": "All"}
}

# Pipeline Presets
PIPELINE_PRESETS = {
    "Balanced (GPT-4)": {"techs": ["Hybrid Search", "Query Rewriting"]},
    "Deep Research": {"techs": ["Hybrid Search", "Reranking", "Parent-Document", "Multi-Query"]},
    "Fast Retrieval": {"techs": ["Hybrid Search", "Context Compression"]},
    "Logic/Reasoning": {"techs": ["Sub-Query", "Reranking"]}
}