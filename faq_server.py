import sqlite3
import os
import sys
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server_debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database Configuration
DB_PATH = "ecoco_faq.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theme TEXT NOT NULL,
            main_item TEXT,
            sub_item TEXT,
            detail TEXT,
            content_v1 TEXT,
            content_v2 TEXT,
            created_date TEXT,
            modified_date TEXT,
            images TEXT
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB on start
init_db()

app = FastAPI(title="ECOCO FAQ Assistant API")

# Enable CORS for local artifacts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the interface artifact
HTML_PATH = os.path.join(os.path.dirname(__file__), "ecoco_persistent_faq.html")

@app.get("/", include_in_schema=False)
async def read_index():
    if os.path.exists(HTML_PATH):
        return FileResponse(HTML_PATH)
    return {"error": "Management interface file not found. Please check paths."}

class FAQ(BaseModel):
    id: Optional[int] = None
    theme: str
    main_item: Optional[str] = None
    sub_item: Optional[str] = None
    detail: Optional[str] = None
    content_v1: Optional[str] = None
    content_v2: Optional[str] = None
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    images: Optional[str] = None

@app.get("/faqs", response_model=List[FAQ])
async def get_faqs():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faqs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/faqs", response_model=FAQ)
async def create_faq(faq: FAQ):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y/%m/%d")
    cursor.execute("""
        INSERT INTO faqs (theme, main_item, sub_item, detail, content_v1, content_v2, created_date, modified_date, images)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (faq.theme, faq.main_item, faq.sub_item, faq.detail, faq.content_v1, faq.content_v2, now, now, faq.images))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {**faq.dict(), "id": new_id, "created_date": now, "modified_date": now}

@app.put("/faqs/{faq_id}", response_model=FAQ)
async def update_faq(faq_id: int, faq: FAQ):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y/%m/%d")
    cursor.execute("""
        UPDATE faqs SET 
            theme = ?, main_item = ?, sub_item = ?, detail = ?, 
            content_v1 = ?, content_v2 = ?, modified_date = ?, images = ?
        WHERE id = ?
    """, (faq.theme, faq.main_item, faq.sub_item, faq.detail, faq.content_v1, faq.content_v2, now, faq.images, faq_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="FAQ not found")
    conn.commit()
    conn.close()
    return {**faq.dict(), "id": faq_id, "modified_date": now}

@app.delete("/faqs/{faq_id}")
async def delete_faq(faq_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="FAQ not found")
    conn.commit()
    conn.close()
    return {"message": "FAQ deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7777)
    args = parser.parse_args()

    # Check if we should initialize with some data if empty
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM faqs")
        count = cursor.fetchone()[0]
        if count == 0:
            # Dummy data for first run
            data = [
                ("APP2.0", "登入與帳號", "繁體版", "無法收到簡訊驗證碼", 
                 "親愛的會員您好，\n\n若您未收到簡訊驗證碼，請先確認您的手機是否開啟了「阻擋行銷簡訊」功能。您也可以嘗試重新開機後，再次點擊發送確認。若仍有問題，歡迎隨時與我們聯繫！", 
                 "Dear member,\n\nIf you haven't received the SMS verification code, please ensure your phone doesn't block marketing messages. You may also try restarting your device before requesting another code.", 
                 "2026/03/10", "2026/03/10"),
                ("硬體設備", "回收機台", "故障報修", "投入瓶子機器無反應", 
                 "您好，很抱歉讓您在使用上遇到困擾！\n\n若是機器面板或投入口未亮燈，可能是機台暫時連線異常或滿桶中。麻煩您協助提供【站點位置】與【機台編號】，我們將立即派員前往檢修。感謝您的回報！", 
                 "", 
                 "2026/03/10", "2026/03/10")
            ]
            cursor.executemany("""
                INSERT INTO faqs (theme, main_item, sub_item, detail, content_v1, content_v2, created_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
    
    print(f"==========================================")
    print(f" ECOCO FAQ Server Starting...")
    print(f" Target: http://{args.host}:{args.port}")
    print(f" Database: {os.path.abspath(DB_PATH)}")
    print(f"==========================================")
    
    uvicorn.run(app, host=args.host, port=args.port)
