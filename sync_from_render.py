"""
ECOCO FAQ 雲端同步到本機腳本
從 Render 雲端下載最新資料，同步到本機 SQLite 資料庫

使用方式：
  python sync_from_render.py          → 同步（保留本機資料，雲端優先）
  python sync_from_render.py --reset  → 清空本機，完全用雲端資料取代
"""

import requests
import sqlite3
import os
import sys
import argparse
from datetime import datetime

RENDER_URL = "https://ecoco-faq-assistant-2.onrender.com"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecoco_faq.db")

def get_local_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theme TEXT NOT NULL,
            main_item TEXT, sub_item TEXT, detail TEXT,
            content_v1 TEXT, content_v2 TEXT,
            created_date TEXT, modified_date TEXT, images TEXT
        )
    """)
    conn.commit()
    return conn

def fetch_render_faqs():
    print(f"🌐 正在連線到 Render（首次可能需要 30 秒喚醒）...")
    try:
        res = requests.get(f"{RENDER_URL}/faqs", timeout=60)
        res.raise_for_status()
        faqs = res.json()
        print(f"✅ 雲端取得 {len(faqs)} 筆資料")
        return faqs
    except Exception as e:
        print(f"❌ 無法連線到 Render：{e}")
        return None

def sync(reset=False):
    print("=" * 55)
    print("  ECOCO FAQ 雲端 → 本機 同步工具")
    print("=" * 55)

    faqs = fetch_render_faqs()
    if faqs is None:
        return

    conn = get_local_db()
    cursor = conn.cursor()

    if reset:
        print("\n⚠️  清空本機資料庫，完全以雲端資料取代...")
        cursor.execute("DELETE FROM faqs")
        conn.commit()
        print("✅ 本機資料已清空")
    else:
        cursor.execute("SELECT COUNT(*) FROM faqs")
        local_count = cursor.fetchone()[0]
        print(f"\n📂 本機目前有 {local_count} 筆資料")

    # 取得本機現有的 detail+theme 組合，避免重複
    cursor.execute("SELECT theme, detail FROM faqs")
    existing = set((r[0], r[1]) for r in cursor.fetchall())

    added = 0
    skipped = 0

    for faq in reversed(faqs):
        key = (faq.get('theme',''), faq.get('detail',''))
        if not reset and key in existing:
            skipped += 1
            continue
        cursor.execute("""
            INSERT INTO faqs (theme, main_item, sub_item, detail, content_v1, content_v2, created_date, modified_date, images)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            faq.get('theme',''), faq.get('main_item',''), faq.get('sub_item',''),
            faq.get('detail',''), faq.get('content_v1',''), faq.get('content_v2',''),
            faq.get('created_date',''), faq.get('modified_date',''), faq.get('images','')
        ))
        added += 1

    conn.commit()
    conn.close()

    print(f"\n{'=' * 55}")
    print(f"  同步完成！新增：{added} 筆　略過重複：{skipped} 筆")
    print(f"  資料庫位置：{DB_PATH}")
    print(f"{'=' * 55}")
    print(f"\n現在可以啟動 啟動ECOCO知識庫.bat 查看本機資料")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true', help='清空本機資料，完全用雲端取代')
    args = parser.parse_args()
    sync(reset=args.reset)
