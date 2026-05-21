"""Main window with period tabs, scrollable card list, and FAB add button."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QPushButton, QLabel, QButtonGroup,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from backend.manager import TodoManager
from backend.models import TodoItem
from ui.styles import (
    BG_DARK, BG_TAB_BAR, ACCENT_BLUE, TEXT_PRIMARY, TEXT_SECONDARY,
    PERIOD_LABELS, GLOBAL_STYLE, WIN_WIDTH, WIN_HEIGHT, WIN_MIN_W, WIN_MIN_H,
)
from ui.todo_card import TodoCard
from ui.add_todo_dialog import AddTodoDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._manager = TodoManager()
        self._current_period = "daily"

        self.setWindowTitle("待办事项管理")
        self.resize(WIN_WIDTH, WIN_HEIGHT)
        self.setMinimumSize(WIN_MIN_W, WIN_MIN_H)

        # App icon
        from pathlib import Path
        icon_path = Path(__file__).resolve().parent.parent / "icon" / "app_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Global style
        self.setStyleSheet(GLOBAL_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Period tabs ──────────────────────────────────
        root.addLayout(self._build_tab_bar())

        # ── Progress bar ─────────────────────────────────
        self._progress_container = self._build_progress_bar()
        root.addWidget(self._progress_container)

        # ── Card list ─────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)

        self._card_container = QWidget()
        self._card_container.setStyleSheet(f"background: {BG_DARK};")
        self._card_layout = QVBoxLayout(self._card_container)
        self._card_layout.setContentsMargins(20, 16, 20, 16)
        self._card_layout.setSpacing(10)
        self._card_layout.addStretch()

        self._scroll.setWidget(self._card_container)
        root.addWidget(self._scroll, 1)

        # ── FAB button ────────────────────────────────────
        fab_container = QHBoxLayout()
        fab_container.setContentsMargins(0, 0, 24, 20)

        self._fab = QPushButton("+")
        self._fab.setFixedSize(56, 56)
        self._fab.setFont(QFont("Segoe UI", 24))
        self._fab.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 28px;
            }}
            QPushButton:hover {{
                background: #1084E0;
            }}
        """)
        self._fab.clicked.connect(self._on_add)
        self._fab.setToolTip("新建待办事项")

        fab_container.addStretch()
        fab_container.addWidget(self._fab)
        root.addLayout(fab_container)

        # ── Status bar ────────────────────────────────────
        self._status_label = QLabel()
        self._status_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            padding: 8px 20px;
            background: transparent;
        """)
        root.addWidget(self._status_label)

        # Load initial data
        self._refresh_list()

    def _build_tab_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setContentsMargins(0, 0, 0, 0)
        bar.setSpacing(0)

        tab_widget = QWidget()
        tab_widget.setStyleSheet(f"background: {BG_TAB_BAR};")
        tab_widget.setFixedHeight(48)

        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(16, 0, 16, 0)
        tab_layout.setSpacing(4)

        self._tab_group = QButtonGroup(self)
        self._tab_buttons = {}

        for i, (key, label) in enumerate(PERIOD_LABELS.items()):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(36)
            btn.setMinimumWidth(90)
            btn.setFont(QFont("Microsoft YaHei UI", 13))

            is_active = key == self._current_period
            btn.setChecked(is_active)
            self._apply_tab_style(btn, is_active)

            btn.clicked.connect(lambda checked, k=key: self._on_period_change(k))
            self._tab_group.addButton(btn, i)
            self._tab_buttons[key] = btn
            tab_layout.addWidget(btn)

        tab_layout.addStretch()
        bar.addWidget(tab_widget)
        return bar

    def _apply_tab_style(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {ACCENT_BLUE};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_SECONDARY};
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    color: {TEXT_PRIMARY};
                    background: #333;
                }}
            """)

    def _build_progress_bar(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {BG_DARK};")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(12)

        self._progress_label = QLabel()
        self._progress_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; background: transparent;")

        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: #333;
                border: none;
                border-radius: 4px;
            }}
        """)

        layout.addWidget(self._progress_label)
        layout.addWidget(self._progress_bar, 1)
        return container

    def _refresh_progress(self):
        period_completed = self._manager.get_todos(period=self._current_period, status="completed")
        period_active = self._manager.get_todos(period=self._current_period, status="active")
        period_uncompleted = self._manager.get_todos(period=self._current_period, status="uncompleted")

        total = len(period_active) + len(period_completed) + len(period_uncompleted)
        done = len(period_completed)

        if total == 0:
            pct = 0
            self._progress_bar.setValue(0)
            self._progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background: #333;
                    border: none;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background: #444;
                    border-radius: 4px;
                }}
            """)
        else:
            pct = int(done / total * 100)
            self._progress_bar.setValue(pct)
            self._update_progress_color(pct)

        period_names = {"daily": "今日", "weekly": "本周", "monthly": "本月"}
        name = period_names.get(self._current_period, "")
        self._progress_label.setText(f"{name}完成度: {done}/{total}")

    def _update_progress_color(self, pct: int):
        if pct < 25:
            color = "#E74C3C"
        elif pct < 50:
            color = "#F39C12"
        elif pct < 100:
            color = "#3498DB"
        else:
            color = "#27AE60"

        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: #333;
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 4px;
            }}
        """)

    def _on_period_change(self, period: str):
        self._current_period = period
        for key, btn in self._tab_buttons.items():
            self._apply_tab_style(btn, key == period)
        self._refresh_progress()
        self._refresh_list()

    def _on_add(self):
        dlg = AddTodoDialog(self, default_period=self._current_period)
        if dlg.exec() == AddTodoDialog.DialogCode.Accepted:
            data = dlg.get_data()
            self._manager.add_todo(data["content"], data["priority"], data["period"])
            self._refresh_list()

    def _on_edit(self, item: TodoItem):
        dlg = AddTodoDialog(self, edit_item=item, default_period=self._current_period)
        if dlg.exec() == AddTodoDialog.DialogCode.Accepted:
            data = dlg.get_data()
            self._manager.update_todo(
                data["edit_id"], data["content"], data["priority"], data["period"]
            )
            self._refresh_list()

    def _on_completed(self, todo_id: str):
        self._manager.mark_completed(todo_id)
        self._refresh_list()

    def _on_uncompleted(self, todo_id: str):
        self._manager.mark_uncompleted(todo_id)
        self._refresh_list()

    def _on_delete(self, todo_id: str):
        self._manager.delete_todo(todo_id)
        self._refresh_list()

    def _build_section_header(self, title: str, count: int) -> QPushButton:
        btn = QPushButton(f"▼ {title} ({count})")
        btn.setFlat(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {TEXT_SECONDARY};
                font-size: 12px;
                font-weight: bold;
                text-align: left;
                padding: 6px 0;
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                color: {TEXT_PRIMARY};
            }}
        """)
        return btn

    def _toggle_section(self, header: QPushButton, container: QWidget):
        visible = container.isVisible()
        container.setVisible(not visible)
        title = header.text()
        if visible:
            header.setText(title.replace("▼", "▶"))
        else:
            header.setText(title.replace("▶", "▼"))

    def _refresh_list(self):
        # Remove existing widgets (keep stretch)
        while self._card_layout.count() > 1:
            item = self._card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # ── Active cards ──────────────────────────────────
        active = self._manager.get_todos(period=self._current_period, status="active")
        for todo in active:
            card = TodoCard(todo, card_mode="active")
            card.completed.connect(self._on_completed)
            card.uncompleted.connect(self._on_uncompleted)
            card.edit_requested.connect(self._on_edit)
            self._card_layout.insertWidget(self._card_layout.count() - 1, card)

        # ── Completed section ─────────────────────────────
        completed = self._manager.get_todos(period=self._current_period, status="completed")
        if completed:
            header = self._build_section_header("已完成", len(completed))
            self._card_layout.insertWidget(self._card_layout.count() - 1, header)

            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(10)

            for todo in completed:
                card = TodoCard(todo, card_mode="completed")
                card.delete_requested.connect(self._on_delete)
                container_layout.addWidget(card)

            self._card_layout.insertWidget(self._card_layout.count() - 1, container)
            header.clicked.connect(lambda checked, h=header, c=container: self._toggle_section(h, c))

        # ── Uncompleted section ───────────────────────────
        uncompleted = self._manager.get_todos(period=self._current_period, status="uncompleted")
        if uncompleted:
            header = self._build_section_header("未完成", len(uncompleted))
            self._card_layout.insertWidget(self._card_layout.count() - 1, header)

            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(10)

            for todo in uncompleted:
                card = TodoCard(todo, card_mode="uncompleted")
                card.delete_requested.connect(self._on_delete)
                container_layout.addWidget(card)

            self._card_layout.insertWidget(self._card_layout.count() - 1, container)
            header.clicked.connect(lambda checked, h=header, c=container: self._toggle_section(h, c))

        # Update status bar
        all_active = self._manager.get_todos(status="active")
        all_completed = self._manager.get_todos(status="completed")
        all_uncompleted = self._manager.get_todos(status="uncompleted")
        self._status_label.setText(
            f"活跃: {len(all_active)}  |  已完成: {len(all_completed)}  |  未完成: {len(all_uncompleted)}"
        )

        # Update progress bar
        self._refresh_progress()
