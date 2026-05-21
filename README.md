# 待办事项管理 (TODO List)

基于艾森豪威尔矩阵（紧急/重要四象限）的桌面待办事项管理软件，支持日/周/月视图，数据本地 JSON 存储。

## 功能特性

- **艾森豪威尔四象限分类**：紧急且重要（红）、紧急但不重要（蓝）、不紧急但重要（橙）、不紧急且不重要（绿）
- **日/周/月视图**：按周期管理和筛选待办事项
- **完成度进度条**：实时显示当前周期完成率，颜色随百分比动态变化
- **已完成/未完成管理**：折叠式区域，支持彻底删除
- **深色主题 UI**：自定义 QPainter 矢量图标按钮，圆角卡片设计

## 项目结构

```
TODO_List/
├── README.md
├── requirements.txt
├── devlog.md
├── main.py                     # 程序入口
├── 图标文件/
│   └── app_icon.png            # 应用图标
├── backend/
│   ├── __init__.py
│   ├── models.py               # TodoItem 数据模型
│   ├── storage.py              # JSON 文件读写
│   └── manager.py              # 业务逻辑（增删改查）
├── ui/
│   ├── __init__.py
│   ├── styles.py               # 颜色常量 + 全局样式表
│   ├── add_todo_dialog.py      # 新建/编辑待办对话框
│   ├── todo_card.py            # 待办卡片 + IconButton 图标按钮
│   └── main_window.py          # 主窗口（周期切换 + 进度条 + 卡片列表）
└── data/
    └── todos.json              # 运行时自动生成
```

---

## 文件与函数说明

### 入口

| 文件 | 说明 |
|---|---|
| `main.py` | 创建 QApplication，启动 MainWindow |

### backend/ — 后端逻辑层

#### `models.py` — 数据模型

| 类/函数 | 说明 |
|---|---|
| `TodoItem` | dataclass，字段：`id`(UUID)、`content`、`priority`、`period`、`created_at`(ISO 8601)、`status` |
| `TodoItem.to_dict()` | 序列化为 dict |
| `TodoItem.from_dict(data)` | 从 dict 反序列化 |

**字段枚举值**：
- `priority`: `urgent_important` / `urgent_not_important` / `not_urgent_important` / `not_urgent_not_important`
- `period`: `daily` / `weekly` / `monthly`
- `status`: `active` / `completed` / `uncompleted`

#### `storage.py` — 持久化层

| 函数 | 说明 |
|---|---|
| `load_todos()` | 从 `data/todos.json` 读取，返回 `list[dict]` |
| `save_todos(todos)` | 写入 `data/todos.json`，自动创建目录和文件 |

#### `manager.py` — 业务逻辑层

| 类/方法 | 说明 |
|---|---|
| `TodoManager` | 核心业务类，操作内存中的 todo 列表并自动持久化 |
| `add_todo(content, priority, period)` | 创建待办，返回 `TodoItem` |
| `get_todos(period, status)` | 按周期和状态筛选，返回 `list[TodoItem]` |
| `get_all_todos()` | 获取全部待办 |
| `mark_completed(todo_id)` | 标记为已完成 |
| `mark_uncompleted(todo_id)` | 标记为未完成 |
| `restore_to_active(todo_id)` | 恢复为活跃状态 |
| `delete_todo(todo_id)` | 永久删除 |
| `update_todo(todo_id, content, priority, period)` | 编辑待办内容 |

### ui/ — 前端 UI 层

#### `styles.py` — 主题常量

| 常量 | 说明 |
|---|---|
| `PRIORITY_COLORS` | 四种优先级 → 色值映射（红/蓝/橙/绿） |
| `PRIORITY_LABELS` | 优先级 → 中文标签映射 |
| `PERIOD_LABELS` | 周期 → 中文标签映射（每日/每周/每月） |
| `BG_DARK`, `BG_CARD`, `BG_TAB_BAR` | 背景色常量 |
| `TEXT_PRIMARY`, `TEXT_SECONDARY` | 文字颜色常量 |
| `ACCENT_BLUE`, `BTN_GREEN`, `BTN_RED`, `BTN_GRAY` | 按钮/强调色常量 |
| `CARD_RADIUS`, `DOT_SIZE`, `BTN_SIZE` | 尺寸常量 |
| `GLOBAL_STYLE` | 全局 QSS 样式表 |

#### `add_todo_dialog.py` — 新建/编辑对话框

| 类/方法 | 说明 |
|---|---|
| `AddTodoDialog(parent, edit_item, default_period)` | 对话框，`edit_item` 为 None 时新建，否则编辑模式预填数据 |
| `get_data()` | 返回 `{"edit_id", "content", "priority", "period"}` |

#### `todo_card.py` — 待办卡片组件

| 类/信号/方法 | 说明 |
|---|---|
| `IconButton(icon_type, color)` | QPushButton 子类，QPainter 手绘矢量图标 |
| `IconButton` — `"check"` | 勾号（完成按钮） |
| `IconButton` — `"cross"` | 叉号（未完成按钮） |
| `IconButton` — `"dots"` | 三点（编辑按钮） |
| `IconButton` — `"delete"` | 删除叉号 |
| `TodoCard(item, card_mode)` | 卡片组件，`card_mode`: `"active"` / `"completed"` / `"uncompleted"` |
| `TodoCard.completed` | `pyqtSignal(str)` — 触发完成 |
| `TodoCard.uncompleted` | `pyqtSignal(str)` — 触发未完成 |
| `TodoCard.edit_requested` | `pyqtSignal(TodoItem)` — 触发编辑 |
| `TodoCard.delete_requested` | `pyqtSignal(str)` — 触发删除 |

#### `main_window.py` — 主窗口

| 类/方法 | 说明 |
|---|---|
| `MainWindow` | QMainWindow，包含标签栏、进度条、卡片列表、FAB 按钮、状态栏 |
| `_build_tab_bar()` | 构建 每日/每周/每月 切换标签栏 |
| `_build_progress_bar()` | 构建完成度进度条组件 |
| `_build_section_header(title, count)` | 构建已完成/未完成折叠标题 |
| `_refresh_list()` | 刷新全部卡片列表 |
| `_refresh_progress()` | 刷新进度条（计算完成率 + 更新颜色） |
| `_toggle_section(header, container)` | 折叠/展开已完成或未完成区域 |

---

## 安装与运行

### 环境要求

- Python 3.10+
- Windows / macOS / Linux

### 克隆仓库

```bash
git clone https://github.com/dh31223/TODO_List.git
```


### 创建虚拟环境

```bash
python -m venv .venv
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 打包命令

```bash
pyinstaller --onefile --windowed --name "TODO_List" --add-data "icon/app_icon.png;icon" main.py
```
---

## 打包为 .exe

使用 PyInstaller 将程序打包为单个可执行文件：


| 参数 | 说明 |
|---|---|
| `--onefile` | 打包为单个 .exe 文件 |
| `--windowed` | 不显示命令行窗口（GUI 程序） |
| `--name` | 输出文件名 |
| `--add-data` | 附带资源文件（Windows 用 `;` 分隔，macOS/Linux 用 `:`） |

### 3. 输出位置

生成的 .exe 位于 `dist/TODO_List.exe`，可直接双击运行。

> **注意**：首次运行时 `data/todos.json` 会在 .exe 同级目录自动创建。
