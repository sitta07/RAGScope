import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        /* Hidden Header */
        header {visibility: hidden;}
        [data-testid="stHeader"] {display: none;}
        .block-container { padding-top: 1rem !important; }
        
        /* Buttons */
        div.stButton > button { 
            width: 100%; border-radius: 6px; font-weight: 600; height: 3.2em; 
            background-color: #f8fafc; border: 1px solid #cbd5e1; color: #334155;
            transition: all 0.2s;
        }
        div.stButton > button:hover { background-color: #e2e8f0; transform: translateY(-1px); }
        
        /* Typography */
        .custom-title { font-size: 2.5rem; font-weight: 800; color: #1e293b; margin: 0; padding: 0; line-height: 1.2; }
        .custom-welcome-title { font-size: 3.5rem; font-weight: 800; color: #1e293b; text-align: center; margin-top: 20px; }
        .welcome-subtitle { font-size: 1.3rem; color: #64748b; text-align: center; margin-bottom: 3rem;}
        
        /* Cards */
        .feature-card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; height: 100%; }
        .feature-title { font-weight: bold; color: #0f172a; font-size: 1.1rem; margin-bottom: 8px; margin-top: 10px; }
        .feature-desc { font-size: 0.95rem; color: #475569; line-height: 1.6; }
        
        /* Status & Logs */
        .active-status { background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 12px; border-radius: 6px; text-align: center; font-weight: 600; margin-bottom: 20px; }
        .source-ref { font-size: 0.85em; background: #fff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #10b981; }
        .log-entry { font-family: 'Courier New', monospace; font-size: 0.8em; background: #f1f5f9; padding: 8px; margin-bottom: 4px; border-radius: 4px; }
        
        /* Lessons */
        .lesson-container { border: 1px solid #e2e8f0; border-radius: 8px; padding: 25px; background-color: #ffffff; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .process-box { background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 0 4px 4px 0; white-space: pre-line; color: #334155; line-height: 1.6; }

        /* Pro Credit */
        .pro-credit {
            font-family: 'Helvetica Neue', sans-serif;
            font-size: 0.75rem;
            color: #94a3b8;
            text-align: center;
            margin-top: 25px;
            opacity: 0.8;
            transition: opacity 0.3s;
        }
        .pro-credit:hover { opacity: 1; }
        .pro-credit a { color: #64748b; text-decoration: none; font-weight: 600; }
        .pro-credit a:hover { color: #3b82f6; text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

def render_pro_credit(in_sidebar=False):
    style = "style='margin-top: 10px;'" if in_sidebar else ""
    st.markdown(f"""
    <div class='pro-credit' {style}>
        Created by <b>Sitta Boonkaew</b><br>
        <a href='https://github.com/sitta07' target='_blank'>github.com/sitta07</a>
    </div>
    """, unsafe_allow_html=True)