"""Dialog for creating and editing a todo item."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QComboBox, QPushButton,
)
from PyQt6.QtCore import Qt

from ui.styles import (
    PRIORITY_LABELS, PERIOD_LABELS,
    BG_DARK, BG_CARD, ACCENT_BLUE, TEXT_PRIMARY,
)


class AddTodoDialog(QDialog):
    def __init__(self, parent=None, edit_item=None, default_period="daily"):
        super().__init__(parent)
        self._edit_id = edit_item.id if edit_item else None
        self.setWindowTitle("编辑待办事项" if edit_item else "新建待办事项")
        self.setFixedSize(420, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_CARD};
                border: 1px solid #333;
                border-radius: 10px;
            }}
            QLabel {{
                background: transparent;
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(24, 20, 24, 20)

        # Content
        layout.addWidget(QLabel("待办内容："))
        self._content_edit = QTextEdit()
        self._content_edit.setPlaceholderText("输入待办事项的内容…")
        self._content_edit.setMaximumHeight(100)
        if edit_item:
            self._content_edit.setText(edit_item.content)

        layout.addWidget(self._content_edit)

        # Priority
        layout.addWidget(QLabel("优先级："))
        self._priority_combo = QComboBox()
        for key, label in PRIORITY_LABELS.items():
            self._priority_combo.addItem(label, key)
        if edit_item:
            idx = self._priority_combo.findData(edit_item.priority)
            if idx >= 0:
                self._priority_combo.setCurrentIndex(idx)

        layout.addWidget(self._priority_combo)

        # Period
        layout.addWidget(QLabel("周期："))
        self._period_combo = QComboBox()
        for key, label in PERIOD_LABELS.items():
            self._period_combo.addItem(label, key)
        if edit_item:
            idx = self._period_combo.findData(edit_item.period)
            if idx >= 0:
                self._period_combo.setCurrentIndex(idx)
        else:
            idx = self._period_combo.findData(default_period)
            if idx >= 0:
                self._period_combo.setCurrentIndex(idx)

        layout.addWidget(self._period_combo)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: #3A3A3A; color: {TEXT_PRIMARY};
                border: none; border-radius: 6px;
                padding: 8px 22px;
            }}
            QPushButton:hover {{ background: #4A4A4A; }}
        """)
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton("保存" if edit_item else "确定")
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_BLUE}; color: white;
                border: none; border-radius: 6px;
                padding: 8px 22px;
            }}
            QPushButton:hover {{ background: #1084E0; }}
        """)
        confirm_btn.clicked.connect(self._on_confirm)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(confirm_btn)
        layout.addLayout(btn_layout)

    def _on_confirm(self):
        content = self._content_edit.toPlainText().strip()
        if not content:
            return  # silently ignore empty content
        self.accept()

    def get_data(self) -> dict:
        return {
            "edit_id": self._edit_id,
            "content": self._content_edit.toPlainText().strip(),
            "priority": self._priority_combo.currentData(),
            "period": self._period_combo.currentData(),
        }
