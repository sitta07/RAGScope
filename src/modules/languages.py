# Dictionary เก็บข้อความ 2 ภาษา
TEXTS = {
    "en": {
        "title": "RAGScope Pro",
        "subheader_config": "Pipeline Configuration",
        "subheader_chat": "RAGScope Chat",
        "subheader_ab": "A/B Strategy Comparison",
        "subheader_learn": "RAG Academy: Interactive Flows",
        "active_strategy": "Active Strategy",
        "presets": "Quick Presets",
        "manual": "Manual Customization",
        "placeholder": "Ask a question about Harry Potter...",
        "running": "Running RAG Pipeline...",
        "no_api": "Please enter your Groq API Key.",
        "analysis": "Analysis",
        "logs": "Execution Logs",
        "context": "Retrieved Context",
        "btn_read": "Read Content",
        "btn_compare": "Run Comparison",
        "learn_intro": "Explore the logic behind each technique using the flowcharts below.",
        "tech_desc": {
             "Hybrid Search": "Combines Keyword (BM25) and Semantic (Vector) search.",
             "Reranking": "Re-scores retrieved documents using an AI model.",
             "Parent-Document": "Fetches full original document context.",
             "Multi-Query": "Generates diverse query variations.",
             "Sub-Query": "Breaks complex problems into steps.",
             "HyDE": "Hallucinates an answer to search by meaning.",
             "Context Compression": "Extracts only relevant sentences.",
             "Query Rewriting": "Optimizes user query for search engine."
        }
    },
    "th": {
        "title": "RAGScope Pro",
        "subheader_config": "ตั้งค่ากระบวนการ (Pipeline)",
        "subheader_chat": "ห้องแชท RAGScope",
        "subheader_ab": "เปรียบเทียบกลยุทธ์ A/B",
        "subheader_learn": "RAG Academy: แผนภาพการทำงาน",
        "active_strategy": "กลยุทธ์ที่ใช้",
        "presets": "ชุดคำสั่งด่วน",
        "manual": "ปรับแต่งเอง",
        "placeholder": "ถามคำถามเกี่ยวกับ Harry Potter...",
        "running": "กำลังประมวลผล...",
        "no_api": "กรุณากรอก Groq API Key",
        "analysis": "วิเคราะห์ผล",
        "logs": "บันทึกการทำงาน",
        "context": "เอกสารที่ค้นเจอ",
        "btn_read": "อ่านเนื้อหา",
        "btn_compare": "เริ่มเปรียบเทียบ",
        "learn_intro": "เรียนรู้หลักการทำงานของแต่ละเทคนิคผ่านแผนภาพ Flowchart ด้านล่าง",
        "tech_desc": {
             "Hybrid Search": "ผสมผสานการค้นหาด้วยคำ (Keyword) และความหมาย (Vector)",
             "Reranking": "ให้คะแนนเอกสารใหม่ด้วย AI เพื่อความแม่นยำสูงสุด",
             "Parent-Document": "ดึงบริบทเอกสารฉบับเต็มเมื่อเจอท่อนที่เกี่ยว",
             "Multi-Query": "สร้างคำถามหลากหลายรูปแบบเพื่อค้นหาให้ครอบคลุม",
             "Sub-Query": "แตกปัญหาซับซ้อนเป็นข้อย่อยๆ แล้วทำทีละขั้น",
             "HyDE": "มโนคำตอบขึ้นมาก่อน แล้วเอาไปหาเอกสารที่คล้ายกัน",
             "Context Compression": "คัดลอกเฉพาะประโยคสำคัญเพื่อประหยัด Token",
             "Query Rewriting": "เรียบเรียงคำถามใหม่ให้ Search Engine เข้าใจง่าย"
        }
    }
}

def get_text(lang, key):
    """Helper to retrieve text based on language."""
    return TEXTS.get(lang, TEXTS["en"]).get(key, key)