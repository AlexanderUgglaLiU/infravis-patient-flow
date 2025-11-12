from PySide6 import QtCore
from PySide6.QtWidgets import QToolButton, QWidget, QVBoxLayout, QGroupBox, QSizePolicy
from PySide6.QtCore import Qt


class HideBox(QWidget):
    def __init__(self, title: str, content: QWidget):
        super().__init__()
        self.content = content

        self.toggleButton = QToolButton()
        toggleButton = self.toggleButton
        toggleButton.setStyleSheet("QToolButton { border: none; }")
        toggleButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toggleButton.setArrowType(Qt.ArrowType.RightArrow)
        toggleButton.setText(title)
        toggleButton.setCheckable(True)
        toggleButton.setChecked(True)
        toggleButton.toggled.connect(self._on_toggle)

        self.content_box = QGroupBox()
        self.content_box_layout = QVBoxLayout()
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.content_box.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.content_box.setLayout(self.content_box_layout)
        self._on_toggle(True)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.toggleButton)
        main_layout.addWidget(self.content_box)

    def _on_toggle(self, checked) -> None:
        self.toggleButton.setArrowType(
            Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
        )
        if checked:
            self.content_box_layout.addWidget(self.content)
        else:
            self.content_box_layout.removeWidget(self.content)
            self.content.setParent(None)

