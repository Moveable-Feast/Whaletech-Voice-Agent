import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'visitors.db')

print("=" * 80)
print("访客记录查询")
print("=" * 80)
print()
print(f"数据库路径: {db_path}")
print()

if not os.path.exists(db_path):
    print("[ERROR] 数据库文件不存在，请先启动 app.py 初始化数据库")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM visits")
count = cursor.fetchone()[0]

print(f"共 {count} 条记录")
print()

if count > 0:
    print("-" * 80)
    cursor.execute("SELECT id, plate_number, company, phone, purpose, entry_time FROM visits ORDER BY entry_time DESC")
    rows = cursor.fetchall()

    print(f"{'ID':<3} {'车牌':<12} {'公司':<15} {'手机号':<12} {'事由':<10} {'时间'}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:<3} {row[1]:<12} {row[2]:<15} {row[3]:<12} {row[4]:<10} {row[5][:16]}")
else:
    print("[INFO] 数据库为空，请先调用 API 添加访客记录")

conn.close()
print()
print("=" * 80)