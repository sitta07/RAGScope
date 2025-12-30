from langchain_groq import ChatGroq

def get_llm(api_key):
    """Connect to Groq Llama 3."""
    if not api_key: return None
    # Temperature 0.0 for consistent logic/reasoning
    return ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0.0)