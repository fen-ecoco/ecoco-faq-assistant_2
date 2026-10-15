"""
ECOCO FAQ 本機 → 雲端 完整同步腳本
步驟：
  1. 讀取本機 SQLite 所有資料
  2. 清空雲端所有資料（逐筆刪除）
  3. 將本機資料全部推送至雲端

使用方式：
  python push_local_to_render.py
"""

import requests
import sqlite3
import os

LOCAL_DB  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecoco_faq.db")
RENDER_URL = "https://ecoco-faq-assistant-2.onrender.com"

def get_local_faqs():
    print("📂 讀取本機資料庫...")
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faqs ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    print(f"✅ 本機共 {len(rows)} 筆資料")
    return rows

def get_cloud_faqs():
    print("\n🌐 連線至雲端（首次可能需等待 30～60 秒喚醒）...")
    r = requests.get(f"{RENDER_URL}/faqs", timeout=90)
    r.raise_for_status()
    faqs = r.json()
    print(f"✅ 雲端目前共 {len(faqs)} 筆資料")
    return faqs

def clear_cloud(faqs):
    if not faqs:
        print("\n☁️  雲端已無資料，跳過清除步驟")
        return
    print(f"\n🗑️  開始清除雲端 {len(faqs)} 筆資料...")
    failed = 0
    for i, faq in enumerate(faqs):
        try:
            r = requests.delete(f"{RENDER_URL}/faqs/{faq['id']}", timeout=30)
            if r.status_code == 200:
                print(f"  刪除 [{i+1}/{len(faqs)}] ID:{faq['id']} ✓")
            else:
                print(f"  刪除 [{i+1}/{len(faqs)}] ID:{faq['id']} 失敗（{r.status_code}）")
                failed += 1
        except Exception as e:
            print(f"  刪除 [{i+1}/{len(faqs)}] 錯誤：{e}")
            failed += 1
    print(f"✅ 清除完成，失敗 {failed} 筆")

def push_to_cloud(local_faqs):
    print(f"\n📤 開始推送 {len(local_faqs)} 筆資料至雲端...")
    success = 0
    failed  = 0
    for i, faq in enumerate(local_faqs):
        payload = {
            "theme":       faq.get("theme") or "",
            "main_item":   faq.get("main_item") or "",
            "sub_item":    faq.get("sub_item") or "",
            "detail":      faq.get("detail") or "",
            "content_v1":  faq.get("content_v1") or "",
            "content_v2":  faq.get("content_v2") or "",
            "images":      faq.get("images") or "",
            "is_archived": faq.get("is_archived") or 0,
        }
        try:
            r = requests.post(
                f"{RENDER_URL}/faqs",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            if r.status_code == 200:
                success += 1
                print(f"  上傳 [{i+1}/{len(local_faqs)}] {faq.get('theme','')} / {str(faq.get('detail',''))[:30]} ✓")
            else:
                failed += 1
                print(f"  上傳 [{i+1}/{len(local_faqs)}] 失敗（{r.status_code}）")
        except Exception as e:
            failed += 1
            print(f"  上傳 [{i+1}/{len(local_faqs)}] 錯誤：{e}")

    print(f"\n{'='*50}")
    print(f"  同步完成！成功：{success} 筆　失敗：{failed} 筆")
    print(f"  請前往 {RENDER_URL} 確認資料")
    print(f"{'='*50}")

if __name__ == "__main__":
    print("="*50)
    print("  ECOCO FAQ 本機 → 雲端 完整同步")
    print("="*50)

    # 確認
    ans = input("\n⚠️  此操作將清空雲端所有資料並以本機取代，確定繼續？(輸入 y 確認)：")
    if ans.strip().lower() != "y":
        print("已取消。")
        exit()

    try:
        local_faqs  = get_local_faqs()
        if not local_faqs:
            print("❌ 本機無資料，中止操作")
            exit()

        cloud_faqs  = get_cloud_faqs()
        clear_cloud(cloud_faqs)
        push_to_cloud(local_faqs)

    except Exception as e:
        print(f"\n❌ 發生錯誤：{e}")
        print("請確認本機伺服器已啟動，且雲端網址可以連線。")
