import streamlit as st


def inject_custom_css(theme="dark"):
    """Inject custom CSS with support for light/dark theme"""
    
    # Theme colors
    if theme == "light":
        bg_primary = "#ffffff"
        text_primary = "#000000"
        text_secondary = "#475569"
        card_bg = "rgba(255,255,255,0.95)"
        lesson_bg = "#ffffff"
    else:  # dark
        bg_primary = "#0f172a"
        text_primary = "#6f4571"
        text_secondary = "#94a3b8"
        card_bg = "rgba(15,23,42,0.85)"
        lesson_bg = "#1e293b"
    
    st.markdown(f"""
    <style>

    /* Hide Streamlit header */
    header {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }}

    /* GLOBAL FONT */
    html, body, [class*="css"]  {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: {bg_primary};
        color: {text_primary};
    }}

    /* TITLES */

    .custom-title {{
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #6f4571;
        margin-bottom: 0.5rem;
    }}

    .custom-welcome-title {{
        font-size: 3.2rem;
        font-weight: 800;
        text-align: center;
        letter-spacing: -1px;
        margin-top: 10px;
        margin-bottom: 10px;
        color: ##6f4571;
    }}

    .welcome-subtitle {{
        font-size: 1.2rem;
        color: {text_secondary};
        text-align: center;
        margin-bottom: 3rem;
    }}


    /* BUTTONS */

    div.stButton > button {{

        width: 100%;
        height: 3em;

        border-radius: 10px;

        font-weight: 600;

        border: none;

        background: linear-gradient(
            135deg,
            #6366f1,
            #4f46e5
        );

        color: white;

        transition: all 0.25s ease;

        box-shadow: 0 4px 14px rgba(79,70,229,0.25);
    }}

    div.stButton > button:hover {{

        transform: translateY(-2px) scale(1.02);

        box-shadow: 0 8px 24px rgba(79,70,229,0.35);

        background: linear-gradient(
            135deg,
            #7c3aed,
            #4f46e5
        );
    }}


    /* CARDS */

    .feature-card {{

        background: {card_bg};

        backdrop-filter: blur(12px);

        padding: 30px;

        border-radius: 16px;

        border: 1px solid rgba(0,0,0,0.06);

        box-shadow:
        0 10px 30px rgba(0,0,0,0.06);

        transition: all 0.25s ease;

        height: 100%;
    }}

    .feature-card:hover {{

        transform: translateY(-4px);

        box-shadow:
        0 18px 40px rgba(0,0,0,0.12);
    }}


    .feature-title {{

        font-weight: 700;

        font-size: 1.15rem;

        margin-bottom: 10px;

        color: {text_primary};
    }}

    .feature-desc {{

        font-size: 0.95rem;

        line-height: 1.6;

        color: {text_secondary};
    }}



    /* STATUS BOX */

    .active-status {{

        background: linear-gradient(
            135deg,
            #ecfdf5,
            #d1fae5
        );

        border: 1px solid #6ee7b7;

        color: #065f46;

        padding: 14px;

        border-radius: 10px;

        text-align: center;

        font-weight: 600;

        margin-bottom: 25px;

        box-shadow: 0 4px 12px rgba(16,185,129,0.15);
    }}



    /* SOURCE REFERENCE */

    .source-ref {{

        font-size: 0.85em;

        background: #ffffff;

        border-radius: 8px;

        border: 1px solid #e2e8f0;

        padding: 12px;

        margin-bottom: 8px;

        border-left: 4px solid #10b981;

        transition: all 0.15s ease;
    }}

    .source-ref:hover {{

        background: #f8fafc;

        transform: translateX(3px);
    }}



    /* LOG ENTRY */

    .log-entry {{

        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas;

        font-size: 0.8rem;

        background: #0f172a;

        color: #e2e8f0;

        padding: 8px 10px;

        margin-bottom: 4px;

        border-radius: 6px;
    }}



    /* LESSON BOX */

    .lesson-container {{

        border-radius: 16px;

        padding: 30px;

        background: white;

        margin-bottom: 30px;

        border: 1px solid #e2e8f0;

        box-shadow:
        0 12px 30px rgba(0,0,0,0.05);
    }}

    .lesson-header {{
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }}

    .lesson-number {{
        font-size: 2rem;
        font-weight: 800;
        color: #6366f1;
        margin-right: 15px;
        min-width: 50px;
    }}

    .lesson-title {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {text_primary};
    }}

    .process-box {{

        background: {card_bg};

        border-left: 4px solid #6366f1;

        padding: 16px;

        margin: 18px 0;

        border-radius: 6px;

        white-space: pre-line;

        color: {text_primary};

        line-height: 1.7;
    }}

    .lesson-container {{

        border-radius: 16px;

        padding: 30px;

        background: {lesson_bg};

        margin-bottom: 30px;

        border: 1px solid #e2e8f0;

        box-shadow:
        0 12px 30px rgba(0,0,0,0.05);
    }}



    /* CREDIT */

    .pro-credit {{

        font-size: 0.75rem;

        color: #94a3b8;

        text-align: center;

        margin-top: 30px;

        opacity: 0.8;

        transition: opacity 0.25s ease;
    }}

    .pro-credit:hover {{
        opacity: 1;
    }}

    .pro-credit a {{

        color: #6366f1;

        text-decoration: none;

        font-weight: 600;
    }}

    .pro-credit a:hover {{

        text-decoration: underline;
    }}



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