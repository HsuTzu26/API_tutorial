import sqlite3

# 資料庫檔案名稱
DB_FILE = 'todos.db'

def get_db_connection():
    """建立資料庫連線"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        print("✅ 成功連接資料庫！")
        return conn
    except sqlite3.Error as e:
        print(f"❌ 資料庫連接失敗: {e}")
        return None

def check_table_exists(conn):
    """檢查資料表是否存在"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos';")
        table = cursor.fetchone()
        if table:
            print("✅ 資料表 'todos' 存在。")
            return True
        else:
            print("❌ 資料表 'todos' 不存在。")
            return False
    except sqlite3.Error as e:
        print(f"❌ 查詢資料表失敗: {e}")
        return False

def fetch_todos(conn):
    """查詢所有待辦事項"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task FROM todos;")
        todos = cursor.fetchall()
        if todos:
            print("📌 目前的待辦事項：")
            for todo in todos:
                print(f"- [{todo['id']}] {todo['task']}")
        else:
            print("📌 沒有待辦事項。")
    except sqlite3.Error as e:
        print(f"❌ 查詢資料失敗: {e}")

def add_todo(conn, task):
    """新增一個待辦事項"""
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (task) VALUES (?)", (task,))
        conn.commit()
        print(f"✅ 已新增待辦事項：{task}")
    except sqlite3.Error as e:
        print(f"❌ 新增資料失敗: {e}")

def delete_todo(conn, task):
    """刪除一個待辦事項"""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE task = ?", (task,))
        conn.commit()
        print(f"✅ 已刪除待辦事項：{task}")
    except sqlite3.Error as e:
        print(f"❌ 刪除資料失敗: {e}")

if __name__ == "__main__":
    # 1️⃣ 連接資料庫
    conn = get_db_connection()

    print("====================")
    if conn:
        # 2️⃣ 檢查資料表
        if check_table_exists(conn):
            # 3️⃣ 查詢待辦事項
            fetch_todos(conn)

            # 4️⃣ 新增測試資料
            add_todo(conn, "測試項目")
            fetch_todos(conn)

            # 5️⃣ 刪除測試資料
            delete_todo(conn, "測試項目")
            fetch_todos(conn)

        # 關閉資料庫連線
        conn.close()
        print("✅ 資料庫連線已關閉。")

    else:
        print("❌ 無法連接資料庫，請檢查資料庫檔案是否存在。")
