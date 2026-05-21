import json
from pathlib import Path
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent  # exe 所在目录
else:
    BASE_DIR = Path(__file__).resolve().parent.parent  # 项目根目录（保持不变）

DATA_DIR = BASE_DIR / "data"


DATA_FILE = DATA_DIR / "todos.json"


def _ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_todos() -> list[dict]:
    _ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos: list[dict]):
    _ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)
