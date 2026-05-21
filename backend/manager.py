from backend.models import TodoItem
from backend.storage import load_todos, save_todos


class TodoManager:
    def __init__(self):
        self._todos: list[dict] = load_todos()

    def _persist(self):
        save_todos(self._todos)

    def _find_index(self, todo_id: str) -> int:
        for i, d in enumerate(self._todos):
            if d["id"] == todo_id:
                return i
        raise ValueError(f"Todo with id {todo_id} not found")

    def add_todo(self, content: str, priority: str, period: str) -> TodoItem:
        item = TodoItem(content=content, priority=priority, period=period)
        self._todos.append(item.to_dict())
        self._persist()
        return item

    def get_todos(self, period: str = None, status: str = "active") -> list[TodoItem]:
        result = []
        for d in self._todos:
            if d["status"] != status:
                continue
            if period is not None and d["period"] != period:
                continue
            result.append(TodoItem.from_dict(d))
        return result

    def get_all_todos(self) -> list[TodoItem]:
        return [TodoItem.from_dict(d) for d in self._todos]

    def mark_completed(self, todo_id: str):
        idx = self._find_index(todo_id)
        self._todos[idx]["status"] = "completed"
        self._persist()

    def mark_uncompleted(self, todo_id: str):
        idx = self._find_index(todo_id)
        self._todos[idx]["status"] = "uncompleted"
        self._persist()

    def restore_to_active(self, todo_id: str):
        idx = self._find_index(todo_id)
        self._todos[idx]["status"] = "active"
        self._persist()

    def delete_todo(self, todo_id: str):
        idx = self._find_index(todo_id)
        del self._todos[idx]
        self._persist()

    def update_todo(self, todo_id: str, content: str, priority: str, period: str):
        idx = self._find_index(todo_id)
        self._todos[idx]["content"] = content
        self._todos[idx]["priority"] = priority
        self._todos[idx]["period"] = period
        self._persist()
