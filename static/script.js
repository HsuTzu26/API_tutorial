document.addEventListener('DOMContentLoaded', function () {
    console.log("🔄 頁面加載完成，等待畫面渲染...");
    requestAnimationFrame(() => {
        getTodos().then(() => {
            console.log("✅ getTodos 完成");
        });
    });
});


async function getTodos() {
    try {
        console.log("🔄 嘗試連接 /todos API...");
        const response = await fetch('/todos', {
            headers: {
                'Accept': 'text/html'
            }
        });

        console.log("📌 Response Status:", response.status);
        console.log("📌 Response Headers:", response.headers);

        if (response.ok) {
            const list = await response.text();
            console.log("📌 成功取得資料：", list);

            // 嘗試解析並插入到畫面中
            document.getElementById('todo-list').innerHTML = list;
        } else {
            const errorMessage = await response.text();
            document.getElementById('message').innerHTML = `<div class="text-red-600">無法載入清單：${errorMessage}</div>`;
            console.error("❌ 載入待辦事項失敗:", response.statusText);
        }
    } catch (error) {
        document.getElementById('message').innerHTML = `<div class="text-red-600">無法載入清單：${error.message}</div>`;
        console.error("❌ 載入發生錯誤:", error);
    }
}


async function addTodo() {
    const taskInput = document.getElementById('task-input');
    const task = taskInput.value.trim();
    if (!task) {
        alert('待辦事項不能為空！');
        return;
    }

    const response = await fetch('/todos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task }),
    });

    if (response.ok) {
        alert('待辦事項已新增！');
        taskInput.value = '';
        getTodos();
    }
}

async function editTodo(id) {
    const newTask = prompt('請輸入新的待辦事項：');
    if (newTask !== null) {
        await fetch(`/todos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ task: newTask.trim() }),
        });
        getTodos();
    }
}

async function deleteTodo(id) {
    if (confirm('確認刪除此項目嗎？')) {
        await fetch('/todos/bulk-delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: [id] }),
        });
        getTodos();
    }
}

async function bulkDeleteTodos() {
    const checkboxes = document.querySelectorAll('input[name="ids"]:checked');
    const ids = Array.from(checkboxes).map(cb => parseInt(cb.value));

    if (ids.length > 0 && confirm(`確認刪除 ${ids.length} 個項目嗎？`)) {
        await fetch('/todos/bulk-delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids }),
        });
        getTodos();
    }
}
