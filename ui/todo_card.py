"""Todo card widget with priority dot, content, timestamp, and action buttons."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor

from backend.models import TodoItem
from ui.styles import (
    PRIORITY_COLORS, PRIORITY_LABELS,
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY,
    BTN_GREEN, BTN_RED, BTN_GRAY,
    BORDER_CARD, CARD_RADIUS, DOT_SIZE, BTN_SIZE,
)


class IconButton(QPushButton):
    """Circular button with a QPainter-drawn vector icon."""

    def __init__(self, icon_type: str, color: str, parent=None):
        super().__init__(parent)
        self._icon_type = icon_type
        self._color = color
        self._hovered = False
        self.setFixedSize(BTN_SIZE, BTN_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = 1  # margin so the circle doesn't clip
        d = BTN_SIZE - r * 2

        if self._hovered:
            p.setBrush(QColor(self._color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(r, r, d, d)
            icon_color = QColor("white")
        else:
            p.setBrush(QColor(255, 255, 255, 28))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(r, r, d, d)
            icon_color = QColor(255, 255, 255, 210)

        pen = QPen(icon_color, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)

        if self._icon_type in ("check",):
            self._draw_check(p)
        elif self._icon_type in ("cross", "delete"):
            self._draw_cross(p)
        elif self._icon_type == "dots":
            self._draw_dots(p)

        p.end()

    def _draw_check(self, p: QPainter):
        cx, cy = BTN_SIZE / 2, BTN_SIZE / 2
        path = QPainterPath()
        path.moveTo(cx - 5.5, cy + 0.5)
        path.lineTo(cx - 1.5, cy + 5)
        path.lineTo(cx + 6, cy - 4.5)
        p.drawPath(path)

    def _draw_cross(self, p: QPainter):
        pad = 7.5
        p.drawLine(int(pad), int(pad), int(BTN_SIZE - pad), int(BTN_SIZE - pad))
        p.drawLine(int(BTN_SIZE - pad), int(pad), int(pad), int(BTN_SIZE - pad))

    def _draw_dots(self, p: QPainter):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(p.pen().color())  # use icon color for fill
        r = 1.8
        cx = BTN_SIZE / 2
        for offset in (-5, 0, 5):
            p.drawEllipse(int(cx + offset - r), int(BTN_SIZE / 2 - r), int(r * 2), int(r * 2))


class TodoCard(QWidget):
    completed = pyqtSignal(str)
    uncompleted = pyqtSignal(str)
    edit_requested = pyqtSignal(TodoItem)
    delete_requested = pyqtSignal(str)

    def __init__(self, item: TodoItem, card_mode: str = "active", parent=None):
        super().__init__(parent)
        self._item = item
        self._card_mode = card_mode
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

        if self._card_mode == "active":
            self._btn_done = IconButton("check", BTN_GREEN)
            self._btn_done.clicked.connect(self._on_completed)
            self._btn_fail = IconButton("cross", BTN_RED)
            self._btn_fail.clicked.connect(self._on_uncompleted)
            self._btn_edit = IconButton("dots", BTN_GRAY)
            self._btn_edit.clicked.connect(self._on_edit)
            btn_layout.addWidget(self._btn_done)
            btn_layout.addWidget(self._btn_fail)
            btn_layout.addWidget(self._btn_edit)
        else:
            self._btn_delete = IconButton("delete", BTN_RED)
            self._btn_delete.clicked.connect(self._on_delete)
            btn_layout.addWidget(self._btn_delete)

        root.addWidget(dot)
        root.addLayout(text_layout, 1)
        root.addLayout(btn_layout)

    def _on_completed(self):
        self.completed.emit(self._item.id)

    def _on_uncompleted(self):
        self.uncompleted.emit(self._item.id)

    def _on_edit(self):
        self.edit_requested.emit(self._item)

    def _on_delete(self):
        self.delete_requested.emit(self._item.id)

    @property
    def todo_id(self) -> str:
        return self._item.id
