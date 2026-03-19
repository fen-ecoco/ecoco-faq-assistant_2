import sqlite3
import re
from datetime import datetime

DB_PATH = "ecoco_faq.db"
TXT_PATH = r"c:\Users\fen\Desktop\TXT筆記本\【常用回覆】.txt"

def parse_and_insert():
    if not os.path.exists(TXT_PATH):
        print("Note file not found.")
        return

    with open(TXT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Simple parsing logic for the first part of the file
    # Format appears to be: Title [Optional Number]
    # Then some explanation
    
    current_theme = "常用回覆"
    now = datetime.now().strftime("%Y/%m/%d")
    
    for i in range(2, 100): # Just taking the first 100 lines for now
        line = lines[i].strip()
        if not line or line.startswith("---"):
            continue
            
        # Try to find common patterns
        # Example: "找機台說明 10841 / Z10902 + 13808 /13572"
        match = re.match(r"^([^\d]+)(\d.*)?$", line)
        if match:
            main_item = match.group(1).strip()
            detail = match.group(2).strip() if match.group(2) else ""
            
            # Simple check to avoid duplicates or junk
            if len(main_item) > 2:
                cursor.execute("""
                    INSERT INTO faqs (theme, main_item, detail, created_date, modified_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (current_theme, main_item, detail, now, now))
    
    conn.commit()
    conn.close()
    print("Initial data inserted.")

import os
parse_and_insert()
