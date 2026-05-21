"""Todo card widget with priority dot, content, timestamp, and action buttons."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

from backend.models import TodoItem
from ui.styles import (
    PRIORITY_COLORS, PRIORITY_LABELS,
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY,
    BTN_GREEN, BTN_RED, BTN_GRAY,
    BORDER_CARD, CARD_RADIUS, DOT_SIZE, BTN_SIZE,
)


class TodoCard(QWidget):
    completed = pyqtSignal(str)    # emits todo_id
    uncompleted = pyqtSignal(str)  # emits todo_id
    edit_requested = pyqtSignal(TodoItem)  # emits the item to edit

    def __init__(self, item: TodoItem, parent=None):
        super().__init__(parent)
        self._item = item
        self._build_ui()

    def _build_ui(self):
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            TodoCard {{
                background: {BG_CARD};
                border: 1px solid {BORDER_CARD};
                border-radius: {CARD_RADIUS}px;
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(12)

        # ── Left: priority dot ───────────────────────────
        dot = QLabel()
        dot.setFixedSize(DOT_SIZE, DOT_SIZE)
        color = PRIORITY_COLORS.get(self._item.priority, "#888")
        dot.setStyleSheet(f"""
            background: {color};
            border-radius: {DOT_SIZE // 2}px;
            min-width: {DOT_SIZE}px;
            min-height: {DOT_SIZE}px;
        """)
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Center: content + time ───────────────────────
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        content = QLabel(self._item.content)
        content.setStyleSheet("background: transparent; font-size: 14px;")
        content.setWordWrap(True)

        # Format timestamp for display
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(self._item.created_at)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            time_str = self._item.created_at[:16]

        meta = QLabel(f"{time_str}  ·  {PRIORITY_LABELS.get(self._item.priority, '')}")
        meta.setStyleSheet(f"background: transparent; color: {TEXT_SECONDARY}; font-size: 11px;")

        text_layout.addWidget(content)
        text_layout.addWidget(meta)

        # ── Right: action buttons ────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self._btn_done = self._make_circle_btn("✓", BTN_GREEN, self._on_completed)
        self._btn_fail = self._make_circle_btn("✗", BTN_RED, self._on_uncompleted)
        self._btn_edit = self._make_circle_btn("⋯", BTN_GRAY, self._on_edit)

        btn_layout.addWidget(self._btn_done)
        btn_layout.addWidget(self._btn_fail)
        btn_layout.addWidget(self._btn_edit)

        root.addWidget(dot)
        root.addLayout(text_layout, 1)
        root.addLayout(btn_layout)

    def _make_circle_btn(self, text: str, color: str, slot) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(BTN_SIZE, BTN_SIZE)
        btn.setFont(QFont("Segoe UI", 11))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: {BTN_SIZE // 2}px;
                font-weight: bold;
                padding: 0;
            }}
            QPushButton:hover {{
                opacity: 0.8;
                background: {color};
            }}
        """)
        btn.clicked.connect(slot)
        return btn

    def _on_completed(self):
        self.completed.emit(self._item.id)

    def _on_uncompleted(self):
        self.uncompleted.emit(self._item.id)

    def _on_edit(self):
        self.edit_requested.emit(self._item)

    @property
    def todo_id(self) -> str:
        return self._item.id
