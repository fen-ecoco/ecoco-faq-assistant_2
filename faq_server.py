import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── 資料庫連線 ──
# 優先使用環境變數 DATABASE_URL（Render 雲端）
# 若不存在則使用本機 SQLite 模式（local fallback）
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_conn()
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
            images TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Database initialized successfully")

init_db()

app = FastAPI(title="ECOCO FAQ Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecoco_persistent_faq.html")

@app.get("/", include_in_schema=False)
async def read_index():
    if os.path.exists(HTML_PATH):
        return FileResponse(HTML_PATH)
    return HTMLResponse("<h2>找不到前端檔案</h2>", status_code=404)

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
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faqs ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/faqs", response_model=FAQ)
async def create_faq(faq: FAQ):
    conn = get_conn()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y/%m/%d")
    cursor.execute("""
        INSERT INTO faqs (theme, main_item, sub_item, detail, content_v1, content_v2, created_date, modified_date, images)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (faq.theme, faq.main_item, faq.sub_item, faq.detail, faq.content_v1, faq.content_v2, now, now, faq.images))
    new_id = cursor.fetchone()["id"]
    conn.commit()
    cursor.close()
    conn.close()
    return {**faq.dict(), "id": new_id, "created_date": now, "modified_date": now}

@app.put("/faqs/{faq_id}", response_model=FAQ)
async def update_faq(faq_id: int, faq: FAQ):
    conn = get_conn()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y/%m/%d")
    cursor.execute("""
        UPDATE faqs SET
            theme=%s, main_item=%s, sub_item=%s, detail=%s,
            content_v1=%s, content_v2=%s, modified_date=%s, images=%s
        WHERE id=%s
    """, (faq.theme, faq.main_item, faq.sub_item, faq.detail,
          faq.content_v1, faq.content_v2, now, faq.images, faq_id))
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="FAQ not found")
    conn.commit()
    cursor.close()
    conn.close()
    return {**faq.dict(), "id": faq_id, "modified_date": now}

@app.delete("/faqs/{faq_id}")
async def delete_faq(faq_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faqs WHERE id=%s", (faq_id,))
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="FAQ not found")
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "FAQ deleted successfully"}
