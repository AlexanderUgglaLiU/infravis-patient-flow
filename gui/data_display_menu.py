from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
)
from PySide6.QtCore import Qt

from gui.histogram import HistogramWidget
from gui.icicle_plot import Icicle


class DataDisplayMenu(QGroupBox):

    def __init__(self):
        super().__init__("Data display")
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.main_layout)

        self.setFixedWidth(400)

        title_label_layout = QHBoxLayout()
        self.from_event_label = QLabel("<from>")
        arrow_event_label = QLabel("->")
        self.to_event_label = QLabel("<to>")

        title_label_layout.addWidget(self.from_event_label)
        title_label_layout.addWidget(arrow_event_label)
        title_label_layout.addWidget(self.to_event_label)
        title_label_widget = QWidget()

        title_label_widget.setLayout(title_label_layout)

        self.histogram = QWidget()  # dummy

        self.main_layout.addWidget(title_label_widget)
        self.main_layout.addWidget(self.histogram)

    def display(self, i1: Icicle | None, i2: Icicle | None) -> None:
        self.main_layout.removeWidget(self.histogram)
        self.histogram.deleteLater()
        self.from_event_label.setText("<from>" if i1 is None else i1.data.key)
        self.to_event_label.setText("<to>" if i2 is None else i2.data.key)

        if (i1 is None) or (i2 is None):
            self.histogram = QWidget()
        else:
            data = i1.data.get_time_diffs(i2.data)
            self.histogram = HistogramWidget(data, 500, 350, 5)

        self.main_layout.addWidget(self.histogram)
