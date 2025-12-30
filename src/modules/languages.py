# src/modules/languages.py

TEXTS = {
    "en": {
        "title": "RAGScope Pro",
        "subheader_config": "Pipeline Configuration",
        "subheader_chat": "Chat Interface",
        "subheader_ab": "A/B Strategy Comparison",
        "subheader_learn": "RAG Academy: CS101 Deep Dive",
        "active_strategy": "Active Strategy",
        "presets": "Quick Presets",
        "manual": "Manual Customization",
        "placeholder": "Enter your query here...",
        "running": "Processing...",
        "no_api": "Groq API Key is required.",
        "analysis": "Analysis",
        "logs": "System Logs",
        "context": "Context",
        "btn_read": "Read File",
        "btn_compare": "Compare Strategies",
        "learn_intro": "Learn RAG concepts from scratch, just like a Computer Science 101 class.",
        # REWRITTEN (EN): CS101 Education Style
        "lessons": {
            "Hybrid Search": {
                "concept": "Keyword Match (Ctrl+F) + Semantic Match (Meaning)",
                "problem": "Basics: A 'Keyword' is an exact string of characters.\n\nScenario: You search for 'PC'.\n- Keyword Search: Finds text containing 'PC'.\n- Problem: It misses text containing 'Computer' or 'Laptop' because the strings don't match.\n- Vector Search: Finds 'Laptop' because it knows it means the same as 'PC', but might miss specific part numbers like 'PC-98'.",
                "process": "1. Run 'Keyword Search' (BM25) to catch exact terms.\n2. Run 'Vector Search' (Embeddings) to catch related meanings.\n3. Merge the two lists (Weighted Sum) to get the best of both worlds.",
                "technical": "Tech Stack: BM25 (Sparse Vector) + ChromaDB (Dense Vector) + Reciprocal Rank Fusion (RRF)."
            },
            "Reranking": {
                "concept": "Quality Check / Re-sorting results",
                "problem": "Basics: Database retrieval aims for speed, not perfection.\n\nScenario: You ask for 'Harry's enemy'.\n- The DB quickly grabs 50 docs mentioning 'Harry' or 'Enemy'.\n- The top result might be just a casual mention: 'Harry ate with his enemy'.\n- This is irrelevant trash data, but the DB thinks it matches.",
                "process": "1. Retrieve a large pool of candidates (e.g., 50 docs).\n2. Use a 'Teacher AI' (Reranker) to read each doc carefully.\n3. The AI gives a score (0-10): 'Is this actually relevant?'\n4. Sort by score and keep only the Top 5.",
                "technical": "Tech Stack: Cross-Encoder Model or LLM-based Scoring Prompt."
            },
            "Parent-Document": {
                "concept": "Find the Needle, Return the Haystack",
                "problem": "Basics: 'Chunking' is splitting text into small pieces (e.g., 5 lines) for the DB.\n\nScenario: A chunk says: 'He killed him.'\n- Problem: Who is 'He'? Who is 'him'?\n- Without the previous paragraphs (Context), this information is useless to the AI.",
                "process": "1. Search using small chunks (precise matching).\n2. When a chunk is found, look at its ID tag (e.g., 'Chapter 1').\n3. Go to the Hard Drive and load the *entire* Chapter 1.\n4. Send the full chapter to the AI so it knows who 'He' is.",
                "technical": "Tech Stack: Metadata Mapping (Child Chunk ID -> Parent Doc ID) + Disk I/O."
            },
            "Multi-Query": {
                "concept": "Asking the same question in different ways",
                "problem": "Basics: Users are bad at prompting.\n\nScenario: User types 'snake man'.\n- The DB looks for 'snake' and 'man'.\n- It might miss 'Voldemort' or 'Basilisk' because the user didn't use those specific words.",
                "process": "1. AI looks at 'snake man' and brainstorms synonyms.\n2. Generates: 'Who is Voldemort?', 'List of serpents', 'Slytherin monster'.\n3. Runs 3 separate searches.\n4. Combines results to cover all possibilities.",
                "technical": "Tech Stack: LLM Query Generation -> Parallel Thread Execution -> Set Deduplication."
            },
            "Sub-Query": {
                "concept": "Divide and Conquer (Step-by-Step)",
                "problem": "Basics: Search Engines are bad at logic.\n\nScenario: 'Who is older, Harry or Ron?'\n- If you search this directly, you might find nothing comparing their ages.\n- You need two separate facts: Harry's birthday AND Ron's birthday.",
                "process": "1. Break it down: 'Find Harry's birthday' (Step 1).\n2. Search and get answer (e.g., 1980).\n3. Break it down: 'Find Ron's birthday' (Step 2).\n4. Search and get answer (e.g., 1980).\n5. AI compares the two facts.",
                "technical": "Tech Stack: Chain-of-Thought Decomposition -> Sequential Retrieval Loops."
            },
            "HyDE": {
                "concept": "Fake it 'til you make it",
                "problem": "Basics: 'Semantic Gap'. Questions look different from Answers.\n\nScenario: Question: 'Symptoms of flu'. Answer Doc: 'High fever, chills, fatigue'.\n- The words don't match well in vector space.",
                "process": "1. AI hallucinates a fake answer: 'Flu symptoms usually include fever and body ache...'\n2. Convert this *Fake Answer* into numbers (Vector).\n3. Search the DB using the *Fake Answer's* vector.\n4. You will find real medical docs that look like the fake answer.",
                "technical": "Tech Stack: Zero-shot Generation -> Embedding -> Similarity Search."
            },
            "Context Compression": {
                "concept": "Summarizing / Removing Noise",
                "problem": "Basics: LLM Context Window is expensive ($).\n\nScenario: You found a 10-page document about Potions.\n- User only asked: 'What color is Polyjuice Potion?'\n- Sending all 10 pages is a waste of money and might confuse the AI.",
                "process": "1. Load the full 10 pages.\n2. Use a cheaper/faster AI to scan it.\n3. Extract ONLY sentences mentioning 'Polyjuice' and 'Color'.\n4. Send only those 2 sentences to the main Chatbot.",
                "technical": "Tech Stack: LLM Extraction Chain / Map-Reduce Summarization."
            },
            "Query Rewriting": {
                "concept": "Pre-processing / Cleaning Input",
                "problem": "Basics: Garbage In, Garbage Out.\n\nScenario: User asks: 'umm.. tell me about that stick thingy he uses'.\n- Search Engine result: 0 found (because of 'umm', 'thingy').",
                "process": "1. Intercept the user's messy text.\n2. Tell AI: 'Translate this into a formal search query'.\n3. Output: 'Harry Potter magic wand description'.\n4. Search with the clean version.",
                "technical": "Tech Stack: Few-shot Prompting for Text Normalization."
            }
        }
    },
    "th": {
        "title": "RAGScope Pro",
        "subheader_config": "ตั้งค่ากระบวนการ (Pipeline)",
        "subheader_chat": "ระบบสนทนา",
        "subheader_ab": "เปรียบเทียบผลลัพธ์ (A/B Test)",
        "subheader_learn": "RAG Academy: ปูพื้นฐานละเอียด (CS101)",
        "active_strategy": "กลยุทธ์ปัจจุบัน",
        "presets": "ชุดคำสั่งด่วน",
        "manual": "กำหนดค่าเอง",
        "placeholder": "พิมพ์คำถามของคุณที่นี่...",
        "running": "กำลังประมวลผล...",
        "no_api": "กรุณาระบุ Groq API Key",
        "analysis": "วิเคราะห์ระบบ",
        "logs": "บันทึกการทำงาน",
        "context": "ข้อมูลอ้างอิง",
        "btn_read": "อ่านไฟล์",
        "btn_compare": "เริ่มเปรียบเทียบ",
        "learn_intro": "เรียนรู้หลักการทำงานของ RAG เหมือนนั่งเรียนวิชาเขียนโปรแกรมเบื้องต้น",
        # REWRITTEN (TH): CS101 Education Style
        "lessons": {
            "Hybrid Search": {
                "concept": "การค้นหาแบบผสม (Keyword Match + Semantic Match)",
                "problem": "พื้นฐาน: 'Keyword' คือข้อความที่ต้องตรงกันเป๊ะๆ (เหมือนกด Ctrl+F)\n\nสถานการณ์: คุณค้นหาคำว่า 'ยารักษาหวัด'\n- Keyword Search: จะหาเฉพาะเอกสารที่มีคำว่า 'ยารักษาหวัด' เป๊ะๆ\n- ปัญหา: มันจะไม่เจอเอกสารที่เขียนว่า 'สมุนไพรแก้คัดจมูก' (เพราะตัวอักษรไม่เหมือนกัน)\n- Vector Search: จะหาเจอ เพราะมันรู้ว่า 'หวัด' กับ 'คัดจมูก' คือเรื่องเดียวกัน",
                "process": "1. รันระบบหาคำตรงตัว (BM25) เพื่อเก็บตกคำเฉพาะ (เช่น ชื่อยา)\n2. รันระบบหาความหมาย (Vector) เพื่อเก็บตกคำที่เขียนไม่เหมือนกัน\n3. เอาผลลัพธ์มารวมกัน เพื่อปิดจุดอ่อนของทั้งคู่",
                "technical": "เชิงเทคนิค: ผสาน Sparse Vector (คำ) และ Dense Vector (ความหมาย) เข้าด้วยกัน"
            },
            "Reranking": {
                "concept": "การตรวจคุณภาพซ้ำ (Re-sorting)",
                "problem": "พื้นฐาน: Database ปกติเน้น 'ความเร็ว' ไม่เน้น 'ความฉลาด'\n\nสถานการณ์: ค้นหา 'ศัตรูของแฮร์รี่'\n- Database รีบกวาดมา 50 ใบ อาจเจอประโยคไร้สาระเช่น 'แฮร์รี่กินข้าวกับศัตรู' มาเป็นอันดับ 1\n- ถ้าเราเอาอันดับ 1 ไปตอบเลย AI ก็จะตอบผิด",
                "process": "1. ให้ Database กวาดมาก่อนเยอะๆ (50 ใบ)\n2. ส่งให้ 'AI ครูผู้ช่วย' (Reranker) นั่งอ่านละเอียดทีละใบ\n3. ให้คะแนนความตรงคำถาม (0-10)\n4. เรียงลำดับใหม่ แล้วคัดเฉพาะ 5 อันดับแรกที่คะแนนดีที่สุด",
                "technical": "เชิงเทคนิค: ใช้ Cross-Encoder Model ในการให้คะแนนความเกี่ยวข้อง (Relevance Score)"
            },
            "Parent-Document": {
                "concept": "หาจากชิ้นเล็ก แต่ส่งข้อมูลชิ้นใหญ่",
                "problem": "พื้นฐาน: การทำ 'Chunking' คือการหั่นหนังสือเป็นย่อหน้าเล็กๆ\n\nสถานการณ์: เจอ Chunk ที่เขียนว่า 'เขาฆ่ามันตาย'\n- ปัญหา: AI ไม่รู้ว่า 'เขา' คือใคร และ 'มัน' คือตัวอะไร เพราะบริบทอยู่ในย่อหน้าก่อนหน้า\n- ถ้าส่งไปแค่นี้ AI จะตอบว่า 'ไม่ทราบชื่อตัวละคร'",
                "process": "1. ค้นหาด้วย Chunk เล็กๆ (เพื่อให้เจอง่าย)\n2. เมื่อเจอแล้ว ให้ดู 'รหัสอ้างอิง' (Source ID)\n3. วิ่งไปเปิดไฟล์ต้นฉบับ แล้วก๊อปปี้ 'ทั้งบท' มาแทน\n4. ส่งบทเต็มให้ AI อ่าน มันจะรู้ทันทีว่า 'เขา' คือโวลเดอมอร์",
                "technical": "เชิงเทคนิค: การทำ Metadata Mapping ระหว่าง Child Chunk กับ Parent Document"
            },
            "Multi-Query": {
                "concept": "การถามเผื่อ (Query Expansion)",
                "problem": "พื้นฐาน: ผู้ใช้งานมักใช้คำค้นหาที่ไม่ดี\n\nสถานการณ์: ผู้ใช้พิมพ์ว่า 'งู'\n- ปัญหา: ใน Database อาจจะไม่มีคำว่า 'งู' เลย มีแต่คำว่า 'บาซิลิสก์' หรือ 'นากินี'\n- ผลลัพธ์: หาไม่เจอ (Search Miss)",
                "process": "1. AI เห็นคำว่า 'งู' แล้วคิดคำแทนให้: 'สัตว์เลื้อยคลานในฮอกวอตส์', 'บาซิลิสก์', 'สัญลักษณ์บ้านสลิธีริน'\n2. สั่งค้นหาทั้ง 3 คำค้นใหม่พร้อมกัน\n3. เอาผลลัพธ์มารวมกัน รับรองว่าเจอแน่นอน",
                "technical": "เชิงเทคนิค: ใช้ LLM Gen คำถาม -> Parallel Search -> Deduplication (ตัดตัวซ้ำ)"
            },
            "Sub-Query": {
                "concept": "การแตกปัญหาใหญ่ (Divide and Conquer)",
                "problem": "พื้นฐาน: การเปรียบเทียบต้องใช้ข้อมูล 2 ชุด\n\nสถานการณ์: 'แฮร์รี่กับรอน ใครแก่กว่า?'\n- ปัญหา: ไม่มีเอกสารใบไหนเขียนเทียบวันเกิดคู่นี้ไว้ตรงๆ\n- การค้นหาทีเดียวจึงล้มเหลว",
                "process": "1. แตกงานเป็นข้อย่อย: 'หาวันเกิดแฮร์รี่' (ข้อ 1)\n2. ค้นหาและจำไว้ (1980)\n3. แตกงานต่อ: 'หาวันเกิดรอน' (ข้อ 2)\n4. ค้นหาและจำไว้ (1980)\n5. เอาข้อมูล 2 ชุดมาเทียบกัน",
                "technical": "เชิงเทคนิค: การทำ Chain-of-Thought เพื่อค้นหาแบบเป็นลำดับขั้น (Step-by-Step)"
            },
            "HyDE": {
                "concept": "การมโนคำตอบล่วงหน้า",
                "problem": "พื้นฐาน: คำถาม กับ คำตอบ มักใช้ภาษาคนละแบบ\n\nสถานการณ์: ถามว่า 'อาการโดนคำสาป'\n- เอกสารตอบ: 'ผิวหนังเปลี่ยนสี ตัวเย็นเฉียบ'\n- ปัญหา: คำว่า 'อาการ' กับ 'ผิวหนัง' ในทางคอมพิวเตอร์มันมองว่าเป็นคนละเรื่องกัน (Vector ไม่ตรงกัน)",
                "process": "1. ให้ AI มโนคำตอบขึ้นมาก่อน: 'อาการโดนคำสาปน่าจะมี ผิวหนังเปื่อย ตัวเย็น...'\n2. เอา 'คำตอบมโน' นี้ไปค้นหา\n3. จะเจอเอกสารจริงง่ายกว่า เพราะภาษามันคล้ายกันแล้ว",
                "technical": "เชิงเทคนิค: Generate Hypothetical Answer -> Embedding -> Similarity Search"
            },
            "Context Compression": {
                "concept": "การย่อความ (Summarization)",
                "problem": "พื้นฐาน: พื้นที่สมอง AI (Context Window) มีจำกัดและแพง\n\nสถานการณ์: ค้นเจอหนังสือ 10 หน้าที่เกี่ยวกับยาปรุง\n- ผู้ใช้ถามแค่: 'สีของน้ำยาคืออะไร?'\n- การส่ง 10 หน้าไปให้ AI อ่าน เป็นการสิ้นเปลือง",
                "process": "1. โหลด 10 หน้ามาไว้ที่ระบบ\n2. ใช้ AI ตัวเล็กอ่านกวาดสายตา\n3. คัดลอกเฉพาะประโยคที่มีคำว่า 'สี' หรือ 'ลักษณะ' ออกมา\n4. ส่งเฉพาะ 2-3 ประโยคนั้นไปตอบคำถาม",
                "technical": "เชิงเทคนิค: ใช้ LLM ทำหน้าที่เป็น Extractor เพื่อลดจำนวน Token"
            },
            "Query Rewriting": {
                "concept": "การล้างข้อมูลขยะ (Input Cleaning)",
                "problem": "พื้นฐาน: Garbage In, Garbage Out (ขยะเข้า ขยะออก)\n\nสถานการณ์: ผู้ใช้พิมพ์: 'เอ่อ... ไอ้ไม้ที่มันใช้เสกอะ อันนั้นแหละ'\n- Search Engine งง: หาคำว่า 'เอ่อ', 'ไอ้ไม้' ไม่เจออะไรที่มีสาระ",
                "process": "1. ดักจับข้อความขยะของผู้ใช้\n2. สั่ง AI ให้แปลเป็นภาษาทางการ: 'ข้อมูลเกี่ยวกับไม้กายสิทธิ์'\n3. เอาคำที่แปลแล้วไปค้นหา",
                "technical": "เชิงเทคนิค: ใช้ Few-shot Prompting เพื่อแปลงภาษาพูดเป็นภาษา Search Engine"
            }
        }
    }
}

def get_text(lang, key):
    return TEXTS.get(lang, TEXTS["en"]).get(key, key)

def get_lesson(lang, tech_name):
    return TEXTS.get(lang, TEXTS["en"]).get("lessons", {}).get(tech_name, {})