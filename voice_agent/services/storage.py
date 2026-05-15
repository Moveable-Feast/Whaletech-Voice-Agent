import sqlite3
import os
from datetime import datetime

def get_db_path():
    """返回项目根目录下的数据库路径"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_root, "visitors.db")

def init_db():
    """初始化数据库"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            company TEXT NOT NULL,
            phone TEXT,
            purpose TEXT,
            visitor_name TEXT,
            entry_time TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_visitor(record):
    """保存访客记录"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    cursor = conn.execute("PRAGMA table_info(visits)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "visitor_name" in columns:
        conn.execute(
            "INSERT INTO visits (plate_number, company, phone, purpose, visitor_name, entry_time) VALUES (?, ?, ?, ?, ?, ?)",
            (
                record["plate_number"],
                record["company"],
                record.get("phone", "未提供"),
                record.get("purpose", "未说明"),
                record.get("visitor_name", ""),
                datetime.now().isoformat()
            )
        )
    else:
        conn.execute(
            "INSERT INTO visits (plate_number, company, phone, purpose, entry_time) VALUES (?, ?, ?, ?, ?)",
            (
                record["plate_number"],
                record["company"],
                record.get("phone", "未提供"),
                record.get("purpose", "未说明"),
                datetime.now().isoformat()
            )
        )
    
    conn.commit()
    conn.close()

def get_history(plate_number):
    """获取访客历史"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT company, purpose FROM visits WHERE plate_number = ? ORDER BY entry_time DESC LIMIT 1",
        (plate_number,)
    )
    result = cursor.fetchone()
    conn.close()
    return result

def get_visitor_history(plate_number):
    """获取详细访客历史"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT company, purpose, phone, entry_time FROM visits WHERE plate_number = ? ORDER BY entry_time DESC LIMIT 1",
        (plate_number,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    company, purpose, phone, entry_time = result
    last_visit = datetime.fromisoformat(entry_time)
    days_since = (datetime.now() - last_visit).days
    
    return {
        "company": company,
        "purpose": purpose,
        "phone": phone,
        "last_visit": entry_time,
        "days_since": days_since,
        "last_purpose": purpose
    }