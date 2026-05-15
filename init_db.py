import sqlite3
import os
import sys

db_path = os.path.join(os.path.dirname(__file__), 'visitors.db')

print("=" * 70)
print("数据库初始化")
print("=" * 70)
print()
print(f"数据库路径: {db_path}")
print()

if not os.path.exists(db_path):
    print("[INFO] 数据库不存在，正在创建...")
    conn = sqlite3.connect(db_path)
    conn.execute("""
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
    print("[OK] 数据库创建成功")
else:
    print("[INFO] 数据库已存在")

    # 检查记录数
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT COUNT(*) FROM visits")
    count = cursor.fetchone()[0]
    print(f"[INFO] 当前有 {count} 条记录")
    conn.close()
    print()

    # 检查是否指定了 --force 参数
    force_mode = '--force' in sys.argv or '-f' in sys.argv

    if force_mode:
        print("[INFO] 强制清空模式...")
    else:
        confirm = input("确定要清空所有访客记录吗？(y/n): ")

    if force_mode or confirm.lower() == 'y':
        conn = sqlite3.connect(db_path)
        print()
        print(f"正在删除 {count} 条记录...")

        conn.execute("DELETE FROM visits")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='visits'")
        conn.commit()
        conn.close()
        print("[OK] 数据库已清空")
    else:
        print("[INFO] 操作已取消")

print()
print("=" * 70)