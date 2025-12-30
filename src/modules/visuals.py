import graphviz
import streamlit as st

def render_tech_flowchart(tech_name):
    """Renders a Graphviz flowchart for a specific RAG technique."""
    
    # Create graph object
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR', size='8,3')
    # Default node style
    graph.attr('node', shape='box', style='rounded,filled', fillcolor='#f0f9ff', color='#0284c7', fontname='Arial')
    
    if tech_name == "Hybrid Search":
        graph.node('U', 'User Query', shape='oval', fillcolor='#fff7ed', color='#ea580c')
        graph.node('K', 'Keyword Search\n(BM25)')
        graph.node('V', 'Vector Search\n(Embeddings)')
        graph.node('M', 'Merge Results', fillcolor='#dcfce7', color='#16a34a')
        graph.edge('U', 'K')
        graph.edge('U', 'V')
        graph.edge('K', 'M')
        graph.edge('V', 'M')

    elif tech_name == "Reranking":
        graph.node('Docs', 'Retrieved Docs\n(Example: 50 items)', shape='stack')
        graph.node('LLM', 'AI Judge\n(Scoring 0-10)', fillcolor='#f3e8ff', color='#9333ea')
        graph.node('Top', 'Top-5 Docs', shape='note', fillcolor='#dcfce7', color='#16a34a')
        graph.edge('Docs', 'LLM')
        graph.edge('LLM', 'Top', label=' Filter Best')

    elif tech_name == "Parent-Document":
        graph.node('C', 'Small Chunk\n(Found)', style='dashed')
        graph.node('Meta', 'Check Metadata\n(Source ID)')
        graph.node('Disk', 'Disk Storage', shape='cylinder', fillcolor='#e5e7eb')
        graph.node('Full', 'Full Document', shape='note', fillcolor='#dcfce7')
        graph.edge('C', 'Meta')
        graph.edge('Meta', 'Disk', label=' Fetch')
        graph.edge('Disk', 'Full')

    elif tech_name == "Multi-Query":
        graph.node('Q', 'Original Query', shape='oval', fillcolor='#fff7ed')
        graph.node('AI', 'AI Generator')
        graph.node('Q1', 'Variation 1')
        graph.node('Q2', 'Variation 2')
        graph.node('Q3', 'Variation 3')
        graph.node('DB', 'Search DB')
        graph.edge('Q', 'AI')
        graph.edge('AI', 'Q1')
        graph.edge('AI', 'Q2')
        graph.edge('AI', 'Q3')
        graph.edge('Q1', 'DB')
        graph.edge('Q2', 'DB')
        graph.edge('Q3', 'DB')

    elif tech_name == "Sub-Query":
        graph.node('Q', 'Complex Query', shape='oval', fillcolor='#fff7ed')
        graph.node('Plan', 'AI Planner', fillcolor='#f3e8ff')
        graph.node('S1', 'Step 1: Search')
        graph.node('S2', 'Step 2: Search')
        graph.node('Ans', 'Final Answer', shape='note', fillcolor='#dcfce7')
        graph.edge('Q', 'Plan')
        graph.edge('Plan', 'S1')
        graph.edge('S1', 'S2', label=' Next Step')
        graph.edge('S2', 'Ans', label=' Synthesize')

    # Default fallback for others (Simple)
    else:
        graph.node('In', 'Input', shape='oval')
        graph.node('Proc', f'{tech_name}\nProcess', fillcolor='#f3e8ff')
        graph.node('Out', 'Output', shape='note', fillcolor='#dcfce7')
        graph.edge('In', 'Proc')
        graph.edge('Proc', 'Out')
    
    st.graphviz_chart(graph, use_container_width=True)