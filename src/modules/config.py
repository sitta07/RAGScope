import os

# Paths
DATA_FOLDER = "./data"
DB_PATH = "./processed_data/chroma_db"
COLLECTION_NAME = "harry_potter_lore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Technique Metadata (Clean Text)
TECHNIQUE_INFO = {
    "Hybrid Search": {
        "desc": "Combines Keyword (BM25) and Semantic (Vector) search.",
        "pros": "Balances exact matches with semantic meaning.",
        "cons": "Slightly slower merge process.",
        "pair_with": "Reranking"
    },
    "Reranking": {
        "desc": "Re-scores retrieved documents using an AI model.",
        "pros": "High precision, filters irrelevant chunks.",
        "cons": "Higher latency due to LLM usage.",
        "pair_with": "Hybrid, Multi-Query"
    },
    "Parent-Document": {
        "desc": "Fetches full original document context.",
        "pros": "Zero missing context.",
        "cons": "Higher token usage.",
        "pair_with": "Context Compression"
    },
    "Multi-Query": {
        "desc": "Generates diverse query variations.",
        "pros": "Captures different phrasings.",
        "cons": "Increased database load.",
        "pair_with": "Reranking"
    },
    "Sub-Query": {
        "desc": "Breaks complex problems into steps.",
        "pros": "Solves multi-hop logic problems.",
        "cons": "Slowest technique (Sequential).",
        "pair_with": "Reranking"
    },
    "HyDE": {
        "desc": "Hallucinates an answer to search by meaning.",
        "pros": "Good for zero-shot tasks.",
        "cons": "Risk of misleading hallucinations.",
        "pair_with": "Hybrid"
    },
    "Context Compression": {
        "desc": "Extracts only relevant sentences.",
        "pros": "Reduces noise and tokens.",
        "cons": "Requires extra LLM processing.",
        "pair_with": "Parent-Document"
    },
    "Query Rewriting": {
        "desc": "Optimizes user query for search engine.",
        "pros": "Standard best practice.",
        "cons": "Minor latency overhead.",
        "pair_with": "All"
    }
}

# Pipeline Presets
PIPELINE_PRESETS = {
    "Balanced (GPT-4)": {"techs": ["Hybrid Search", "Query Rewriting"]},
    "Deep Research": {"techs": ["Hybrid Search", "Reranking", "Parent-Document", "Multi-Query"]},
    "Fast Retrieval": {"techs": ["Hybrid Search", "Context Compression"]},
    "Logic/Reasoning": {"techs": ["Sub-Query", "Reranking"]}
}