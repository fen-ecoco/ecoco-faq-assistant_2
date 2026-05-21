import os
import sqlite3
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server_debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = bool(DATABASE_URL)
DB_PATH = "ecoco_faq.db"

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    logger.info("Using PostgreSQL (Supabase) Database.")
else:
    logger.info("Using SQLite Local Database.")

def get_sqlite_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_pg_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    if USE_POSTGRES:
        conn = get_pg_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faqs (
                id SERIAL PRIMARY KEY,
                theme TEXT NOT NULL,
                main_item TEXT,
                sub_item TEXT,
                detail TEXT,
                content_v1 TEXT,
                content_v2 TEXT,
                created_date TEXT,
                modified_date TEXT,
                images TEXT,
                is_archived INTEGER DEFAULT 0,
                note TEXT
            )
        """)
        # Try to add columns if missing
        try:
            cursor.execute("ALTER TABLE faqs ADD COLUMN is_archived INTEGER DEFAULT 0")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE faqs ADD COLUMN note TEXT")
        except Exception:
            pass
        conn.commit()
        cursor.close()
        conn.close()
    else:
        conn = get_sqlite_conn()
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
                images TEXT,
                note TEXT
            )
        """)
        try:
            cursor.execute("ALTER TABLE faqs ADD COLUMN is_archived INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE faqs ADD COLUMN note TEXT")
        except sqlite3.OperationalError:
            pass
        conn.commit()
        conn.close()

init_db()

app = FastAPI(title="ECOCO FAQ Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ★ 修正：使用相對路徑，本機和 Render 都能正確讀取
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecoco_persistent_faq.html")

@app.get("/", include_in_schema=False)
async def read_index():
    if os.path.exists(HTML_PATH):
        return FileResponse(HTML_PATH)
    return HTMLResponse("<h2>找不到前端檔案，請確認 ecoco_persistent_faq.html 在同一個資料夾內</h2>", status_code=404)

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
    is_archived: Optional[int] = 0
    note: Optional[str] = None

@app.get("/faqs", response_model=List[FAQ])
async def get_faqs():
    if USE_POSTGRES:
        conn = get_pg_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM faqs ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(row) for row in rows]
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM faqs ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

@app.post("/faqs", response_model=FAQ)
async def create_faq(faq: FAQ):
    now = datetime.now().strftime("%Y/%m/%d")
    is_archived = faq.is_archived if faq.is_archived is not None else 0
    if USE_POSTGRES:
        conn = get_pg_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO faqs (theme, main_item, sub_item, detail, content_v1, content_v2, created_date, modified_date, images, is_archived, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (faq.theme, faq.main_item, faq.sub_item, faq.detail, faq.content_v1, faq.content_v2, now, now, faq.images, is_archived, faq.note))
        new_id = cursor.fetchone()["id"]
        conn.commit()
        cursor.close()
        conn.close()
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO faqs (theme, main_item, sub_item, detail, content_v1, content_v2, created_date, modified_date, images, is_archived, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (faq.theme, faq.main_item, faq.sub_item, faq.detail, faq.content_v1, faq.content_v2, now, now, faq.images, is_archived, faq.note))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
    return {**faq.dict(), "id": new_id, "created_date": now, "modified_date": now}

@app.put("/faqs/{faq_id}", response_model=FAQ)
async def update_faq(faq_id: int, faq: FAQ):
    now = datetime.now().strftime("%Y/%m/%d")
    is_archived = faq.is_archived if faq.is_archived is not None else 0
    if USE_POSTGRES:
        conn = get_pg_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE faqs SET
                theme=%s, main_item=%s, sub_item=%s, detail=%s,
                content_v1=%s, content_v2=%s, modified_date=%s, images=%s, is_archived=%s, note=%s
            WHERE id=%s
        """, (faq.theme, faq.main_item, faq.sub_item, faq.detail, faq.content_v1, faq.content_v2, now, faq.images, is_archived, faq.note, faq_id))
        rowcount = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE faqs SET
                theme=?, main_item=?, sub_item=?, detail=?,
                content_v1=?, content_v2=?, modified_date=?, images=?, is_archived=?, note=?
            WHERE id=?
        """, (faq.theme, faq.main_item, faq.sub_item, faq.detail, faq.content_v1, faq.content_v2, now, faq.images, is_archived, faq.note, faq_id))
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="FAQ not found")
        
    return {**faq.dict(), "id": faq_id, "modified_date": now}

@app.delete("/faqs/{faq_id}")
async def delete_faq(faq_id: int):
    if USE_POSTGRES:
        conn = get_pg_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faqs WHERE id=%s", (faq_id,))
        rowcount = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faqs WHERE id=?", (faq_id,))
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"message": "FAQ deleted successfully"}

class AIChatRequest(BaseModel):
    query: str

@app.post("/api/ai_chat")
async def ai_chat(req: AIChatRequest):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="未設定 GEMINI_API_KEY。請在環境變數中加入您的 Gemini API 密鑰。")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        prompt = f"""
你是一位專業的 ECOCO (點數回饋平台) 客服助手。
你的職責是基於 ECOCO 的官方網站(https://www.ecoco.network/)、官方粉絲團以及公開資訊，提供準確且有禮貌的客服回覆。
請直接以客服的口吻回覆，內容應該幫助解決用戶的問題，並避免給出未經證實的承諾。
如果問題超出 ECOCO 的範圍，請委婉告知。

用戶的問題是：「{req.query}」
"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        logger.error(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 生成失敗: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7777)
    args = parser.parse_args()

    print(f"==========================================")
    print(f" ECOCO FAQ Server Starting...")
    print(f" Target: http://{args.host}:{args.port}")
    print(f" DB Mode: {'PostgreSQL (Cloud)' if USE_POSTGRES else 'SQLite (Local)'}")
    print(f"==========================================")
    uvicorn.run(app, host=args.host, port=args.port)
