from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QSizePolicy,
    QPushButton,
    QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor, QMouseEvent, QWheelEvent


class ColorBox(QPushButton):

    clicked_signal = Signal(QMouseEvent)

    def __init__(
        self,
        text: str,
        color: str,
        width=100,
        height=-1,
        tooltip: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.color = color
        self.selected_counter = 0
        if height < 0:
            self.setFixedWidth(width)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        else:
            self.setFixedSize(width, height)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.setAutoFillBackground(True)

        self.set_selected(False)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setCheckable(True)

        self.setToolTip(tooltip)

        # Create layout and label
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Optional: no padding
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        label = QLabel(text)
        label.setStyleSheet(
            """
                border: 0px solid black;
                background-color: rgba(0,0,0,0);
                margin: 2px;
            """
        )
        label.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(label)
        self.setLayout(layout)

    def set_selected(self, selected: bool) -> None:
        if selected:
            self.selected_counter += 1
        else:
            self.selected_counter = max(self.selected_counter - 1, 0)

        border_color: str
        if self.selected_counter > 0:
            border_color = "black"
        else:
            border_color = "rgba(0,0,0,30%)"

        self.setStyleSheet(
            f"""
            border: 2px solid {border_color};
            background-color: {self.color};
            padding: 0px;
            margin: 0px;
        """
        )

    def mousePressEvent(self, mouse_event: QMouseEvent):
        self.clicked_signal.emit(mouse_event)


class Selected:
    def __init__(self, obj) -> None:
        self.obj = obj
        self.obj.left_box.set_selected(True)

    def __del__(self) -> None:
        self.obj.left_box.set_selected(False)


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event: QWheelEvent):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
