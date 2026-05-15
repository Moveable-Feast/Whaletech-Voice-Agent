import sqlite3
import os

print("检查数据库...")
print()

# 检查两个可能的数据库文件
paths = [
    'visitors.db',
    'voice_agent/visitors.db'
]

for db_path in paths:
    print(f"检查: {db_path}")
    exists = os.path.exists(db_path)
    print(f"  存在: {exists}")

    if exists:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"  表: {tables}")

            if tables:
                for table in tables:
                    table_name = table[0]
                    cursor = conn.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    print(f"  {table_name} 表数据: {rows}")

            conn.close()
        except Exception as e:
            print(f"  错误: {e}")
    print()