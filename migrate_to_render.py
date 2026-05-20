"""
ECOCO FAQ 資料搬移腳本
從本機 http://127.0.0.1:7777 搬移所有資料到 Render 雲端

使用方式：
1. 先啟動本機伺服器（執行 啟動ECOCO知識庫.bat）
2. 開啟終端機，執行：python migrate_to_render.py
"""

import requests
import json

LOCAL_URL = "http://127.0.0.1:7777"
RENDER_URL = "https://ecoco-faq-assistant-2.onrender.com"

def migrate():
    print("=" * 50)
    print("ECOCO FAQ 資料搬移工具")
    print("=" * 50)

    # 步驟1：從本機讀取所有資料
    print("\n📥 正在從本機讀取資料...")
    try:
        res = requests.get(f"{LOCAL_URL}/faqs", timeout=5)
        faqs = res.json()
        print(f"✅ 成功讀取 {len(faqs)} 筆資料")
    except Exception as e:
        print(f"❌ 無法連線到本機伺服器：{e}")
        print("請確認已啟動 啟動ECOCO知識庫.bat")
        return

    if not faqs:
        print("⚠️  本機沒有資料，結束。")
        return

    # 步驟2：確認 Render 可以連線
    print(f"\n🌐 正在連線到 Render（可能需要 30 秒喚醒）...")
    try:
        res = requests.get(f"{RENDER_URL}/faqs", timeout=60)
        existing = res.json()
        print(f"✅ Render 連線成功，目前有 {len(existing)} 筆資料")
    except Exception as e:
        print(f"❌ 無法連線到 Render：{e}")
        return

    # 步驟3：逐筆推送資料
    print(f"\n📤 開始搬移 {len(faqs)} 筆資料到 Render...")
    success = 0
    failed = 0

    for i, faq in enumerate(reversed(faqs)):  # reversed 保持原本順序
        payload = {
            "theme": faq.get("theme", ""),
            "main_item": faq.get("main_item", ""),
            "sub_item": faq.get("sub_item", ""),
            "detail": faq.get("detail", ""),
            "content_v1": faq.get("content_v1", ""),
            "content_v2": faq.get("content_v2", ""),
        }
        try:
            res = requests.post(f"{RENDER_URL}/faqs",
                                json=payload,
                                headers={"Content-Type": "application/json"},
                                timeout=30)
            if res.status_code == 200:
                success += 1
                print(f"  ✅ [{i+1}/{len(faqs)}] {faq.get('theme','')} / {faq.get('detail','')[:30]}")
            else:
                failed += 1
                print(f"  ❌ [{i+1}/{len(faqs)}] 失敗：{res.status_code}")
        except Exception as e:
            failed += 1
            print(f"  ❌ [{i+1}/{len(faqs)}] 錯誤：{e}")

    print("\n" + "=" * 50)
    print(f"搬移完成！成功：{success} 筆　失敗：{failed} 筆")
    print(f"請前往 {RENDER_URL} 確認資料")
    print("=" * 50)

if __name__ == "__main__":
    migrate()
