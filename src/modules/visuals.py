import graphviz
import streamlit as st

def render_tech_flowchart(tech_name):
    """
    Renders a detailed engineering-grade flowchart for RAG techniques using Graphviz.
    """
    
    # Global Graph Settings (Professional Look)
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR', splines='ortho', ranksep='0.8', nodesep='0.6')
    graph.attr('node', fontname='Helvetica', fontsize='12', shape='box', style='rounded,filled', fillcolor='white', color='#64748b')
    graph.attr('edge', color='#94a3b8', arrowsize='0.8')

    # 1. Hybrid Search (Detailed)
    if tech_name == "Hybrid Search":
        # Inputs
        graph.node('Q', 'User Query', shape='oval', fillcolor='#eff6ff', color='#3b82f6')
        
        # Parallel Processes
        with graph.subgraph(name='cluster_sparse') as c:
            c.attr(label='Keyword Path (BM25)', color='#cbd5e1', style='dashed')
            c.node('Tok', 'Tokenizer', shape='component')
            c.node('BM25', 'BM25 Index', shape='cylinder', fillcolor='#f1f5f9')
            c.node('ResK', 'Keyword Results\n(List A)', shape='note')
            c.edge('Tok', 'BM25')
            c.edge('BM25', 'ResK')

        with graph.subgraph(name='cluster_dense') as c:
            c.attr(label='Semantic Path (Vector)', color='#cbd5e1', style='dashed')
            c.node('Emb', 'Embedding Model\n(MiniLM-L6)', shape='component', fillcolor='#e0e7ff')
            c.node('Vec', 'Query Vector\n[0.1, -0.5, ...]', shape='parallelogram')
            c.node('VDB', 'Vector DB\n(Chroma)', shape='cylinder', fillcolor='#f1f5f9')
            c.node('ResV', 'Semantic Results\n(List B)', shape='note')
            c.edge('Emb', 'Vec')
            c.edge('Vec', 'VDB', label=' Cosine Sim')
            c.edge('VDB', 'ResV')

        # Fusion
        graph.node('Fuse', 'Reciprocal Rank\nFusion (RRF)', shape='diamond', fillcolor='#dcfce7', color='#16a34a')
        graph.node('Final', 'Final Ranked List', shape='note', fillcolor='#dcfce7')

        # Edges
        graph.edge('Q', 'Tok')
        graph.edge('Q', 'Emb')
        graph.edge('ResK', 'Fuse')
        graph.edge('ResV', 'Fuse')
        graph.edge('Fuse', 'Final')

    # 2. Reranking (Detailed)
    elif tech_name == "Reranking":
        graph.node('Init', 'Initial Retrieval\n(Top-50 Docs)', shape='folder', fillcolor='#eff6ff')
        graph.node('Q', 'User Query', shape='oval', fillcolor='#eff6ff')
        
        # LLM Process
        with graph.subgraph(name='cluster_scoring') as c:
            c.attr(label='Cross-Encoder / LLM Scoring Loop', color='#9333ea', style='solid')
            c.node('Pair', 'Input Pair\n(Query + Doc[i])')
            c.node('AI', 'AI Model\n(Llama 3)', shape='component', fillcolor='#f3e8ff')
            c.node('Score', 'Relevance Score\n(0.0 - 1.0)', shape='circle')
            c.edge('Pair', 'AI')
            c.edge('AI', 'Score')

        graph.node('Sort', 'Sort Descending', shape='invtrapezium')
        graph.node('Top', 'Top-5 Docs\n(High Precision)', shape='note', fillcolor='#dcfce7')

        graph.edge('Init', 'Pair', label=' Iterate')
        graph.edge('Q', 'Pair')
        graph.edge('Score', 'Sort')
        graph.edge('Sort', 'Top', label=' Filter')

    # 3. Parent-Document (Detailed)
    elif tech_name == "Parent-Document":
        graph.node('Q', 'Query', shape='oval')
        
        with graph.subgraph(name='cluster_search') as c:
            c.attr(label='Step 1: Child Search', color='#cbd5e1')
            c.node('Chunk', 'Small Chunk Found\n(id: 101_child_5)', shape='note', fillcolor='#fff1f2')
            c.node('Meta', 'Metadata Lookup\n(parent_id: 101)', shape='box3d')
            c.edge('Chunk', 'Meta')

        with graph.subgraph(name='cluster_fetch') as c:
            c.attr(label='Step 2: Parent Retrieval', color='#cbd5e1')
            c.node('Store', 'Doc Store / S3\n(Full Files)', shape='cylinder')
            c.node('Full', 'Full Document\n(Content of ID 101)', shape='note', fillcolor='#dcfce7')
            c.edge('Store', 'Full')

        graph.edge('Q', 'Chunk', label=' Vector Search')
        graph.edge('Meta', 'Store', label=' Fetch ID')

    # 4. Multi-Query (Detailed)
    elif tech_name == "Multi-Query":
        graph.node('Q', 'Ambiguous Query', shape='oval', fillcolor='#fff7ed')
        graph.node('LLM', 'LLM Generator', shape='component', fillcolor='#ffedd5')
        
        # Variations
        with graph.subgraph(name='cluster_vars') as c:
            c.attr(label='Query Variations', style='dashed')
            c.node('Q1', 'Var 1: Specific')
            c.node('Q2', 'Var 2: Broad')
            c.node('Q3', 'Var 3: Related')
        
        graph.node('DB', 'Vector DB', shape='cylinder')
        graph.node('Union', 'Set Union\n(Deduplication)', shape='diamond')
        graph.node('Final', 'Comprehensive Context', shape='note', fillcolor='#dcfce7')

        graph.edge('Q', 'LLM')
        graph.edge('LLM', 'Q1')
        graph.edge('LLM', 'Q2')
        graph.edge('LLM', 'Q3')
        graph.edge('Q1', 'DB')
        graph.edge('Q2', 'DB')
        graph.edge('Q3', 'DB')
        graph.edge('DB', 'Union', label=' Results')
        graph.edge('Union', 'Final')

    # 5. HyDE (Detailed)
    elif tech_name == "HyDE":
        graph.node('Q', 'User Query', shape='oval')
        graph.node('LLM', 'LLM Hallucinator', shape='component', fillcolor='#f3e8ff')
        
        graph.node('Fake', 'Hypothetical Answer\n(Fake Document)', shape='note', style='dashed', fillcolor='#fdf4ff')
        
        graph.node('Emb', 'Embedding Model', shape='component')
        graph.node('Vec', 'Hypo-Vector', shape='parallelogram')
        graph.node('DB', 'Vector DB', shape='cylinder')
        graph.node('Real', 'Real Document\n(Semantic Match)', shape='note', fillcolor='#dcfce7')

        graph.edge('Q', 'LLM')
        graph.edge('LLM', 'Fake', label=' Generate')
        graph.edge('Fake', 'Emb')
        graph.edge('Emb', 'Vec')
        graph.edge('Vec', 'DB', label=' Search')
        graph.edge('DB', 'Real')

    # 6. Context Compression (Detailed)
    elif tech_name == "Context Compression":
        graph.node('Raw', 'Retrieved Docs\n(10 pages)', shape='folder')
        
        with graph.subgraph(name='cluster_compress') as c:
            c.attr(label='Compression Pipeline', color='#cbd5e1')
            c.node('LLM', 'LLM Extractor', shape='component', fillcolor='#dbeafe')
            c.node('Prompt', 'Prompt:\n"Extract only key facts"', shape='note', style='dotted')
            c.edge('Prompt', 'LLM')
        
        graph.node('Out', 'Compressed Context\n(1 page)', shape='note', fillcolor='#dcfce7')
        
        graph.edge('Raw', 'LLM', label=' Feed')
        graph.edge('LLM', 'Out', label=' Output')

    # 7. Query Rewriting (Detailed)
    elif tech_name == "Query Rewriting":
        graph.node('Raw', 'Raw Input\n"umm.. wand stuff"', shape='oval', fillcolor='#fecaca')
        graph.node('LLM', 'LLM Rewriter', shape='component', fillcolor='#fee2e2')
        graph.node('Prompt', 'System Prompt:\n"Optimize for Search"', shape='note', style='dotted')
        
        graph.node('Clean', 'Optimized Query\n"Harry Potter wand core"', shape='oval', fillcolor='#dcfce7')
        graph.node('Search', 'Search Engine', shape='cylinder')

        graph.edge('Raw', 'LLM')
        graph.edge('Prompt', 'LLM')
        graph.edge('LLM', 'Clean', label=' Refine')
        graph.edge('Clean', 'Search')

    # 8. Sub-Query (Detailed)
    elif tech_name == "Sub-Query":
        graph.node('Q', 'Complex Query\n"Compare A vs B"', shape='oval')
        graph.node('Plan', 'Decomposition Planner', shape='component')
        
        with graph.subgraph(name='cluster_steps') as c:
            c.attr(label='Sequential Execution')
            c.node('S1', 'Step 1:\nFind info on A')
            c.node('Ctx1', 'Context A', shape='note')
            c.node('S2', 'Step 2:\nFind info on B')
            c.node('Ctx2', 'Context B', shape='note')
            
            c.edge('S1', 'Ctx1', label=' Search')
            c.edge('Ctx1', 'S2', label=' Augment')
            c.edge('S2', 'Ctx2', label=' Search')
        
        graph.node('Ans', 'Final Synthesis', shape='diamond', fillcolor='#dcfce7')

        graph.edge('Q', 'Plan')
        graph.edge('Plan', 'S1')
        graph.edge('Ctx2', 'Ans')

    # Render
    st.graphviz_chart(graph, use_container_width=True)