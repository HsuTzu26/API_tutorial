# Imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import logging
import sqlite3
import os

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite 資料庫名稱
DB_FILE = 'todos.db'

# 創建資料庫連接
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 初始化資料庫
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL
            )
        ''')
        conn.commit()

# 初始化資料庫
init_db()

logger.info(f"資料庫 {DB_FILE} 已初始化。")

# 創建 FastAPI 應用
app = FastAPI()

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['*'],
)

# 自定義靜態檔案服務，設置快取頭
class CacheControlStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        return response

# 掛載靜態檔案
app.mount('/static', CacheControlStaticFiles(directory='static'), name='static')

# 資料模型
class Todo(BaseModel):
    task: str

class BulkDelete(BaseModel):
    ids: List[int]

@app.get('/', response_class=HTMLResponse)
async def read_root():
    try:
        with open('static/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse('<div class="text-red-600">無法找到 index.html，請確認檔案存在於 static 資料夾下。</div>')

@app.post('/todos', response_class=HTMLResponse)
async def create_todo(todo: Todo):
    if not todo.task.strip():
        return HTMLResponse('<div class="text-red-600">任務不能為空！</div>')
    
    with get_db_connection() as conn:
        conn.execute('INSERT INTO todos (task) VALUES (?)', (todo.task,))
        conn.commit()
    
    return HTMLResponse('<div class="text-green-600">待辦事項已新增！</div>')

@app.get('/todos', response_class=HTMLResponse)
async def get_todos():
    with get_db_connection() as conn:
        todos = conn.execute('SELECT id, task FROM todos').fetchall()
    
    if not todos:
        return HTMLResponse('<li class="p-2 text-gray-500">暫無待辦事項</li>')

    todo_items = ''.join(
        f'<li class="p-2 border-b flex justify-between items-center">'
        f'<div><input type="checkbox" name="ids" value="{row["id"]}" class="mr-2">{row["task"]}</div>'
        f'<div>'
        f'<button onclick="editTodo({row["id"]})" class="text-blue-500 hover:text-blue-700 mr-2">編輯</button>'
        f'<button onclick="deleteTodo({row["id"]})" class="text-red-500 hover:text-red-700">刪除</button>'
        f'</div>'
        f'</li>'
        for row in todos
    )
    return HTMLResponse(todo_items)


@app.put("/todos/{todo_id}", response_class=HTMLResponse)
async def update_todo(todo_id: int, todo: Todo):
    with get_db_connection() as conn:
        conn.execute('UPDATE todos SET task = ? WHERE id = ?', (todo.task, todo_id))
        conn.commit()

    return HTMLResponse('<div class="text-green-600">待辦事項已更新！</div>')

@app.post('/todos/bulk-delete', response_class=HTMLResponse)
async def bulk_delete_todos(bulk: BulkDelete):
    with get_db_connection() as conn:
        conn.executemany('DELETE FROM todos WHERE id = ?', [(i,) for i in bulk.ids])
        conn.commit()
    return HTMLResponse(f'<div class="text-green-600">已刪除 {len(bulk.ids)} 個待辦事項！</div>')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
