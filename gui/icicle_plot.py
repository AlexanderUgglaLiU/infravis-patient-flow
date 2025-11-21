from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent

import timeline
from gui.gui_components import Selected, ColorBox
from gui.histogram import HistogramWidget
from icd import ICD_SE

class Icicle(QWidget):
    data: timeline.EventAggregate
    parent_icicle: "Icicle|None"
    selected_signal = Signal(Selected, bool)  # bool = is_shift

    def __init__(self, data: timeline.EventAggregate, height_mult: int):
        super().__init__()
        self.data = data

        stop_here_count = data.stop_here
        total_count = data.size
        color = data.color
        label = data.key

        self.icicle_height = height_mult * total_count

        self.count = stop_here_count
        self.parent_icicle = None

        # Main horizontal layout
        self.h_layout = QHBoxLayout()
        palette = self.palette()
        self.setPalette(palette)

        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(10)
        self.h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Dummy histogram
        self.histogram = QWidget()

        tooltip: str = (
            f"{label}\n\nnum sequences: {total_count}\nend here: {stop_here_count}\n{data.info}"
        )

        # Left colored box
        self.left_box = ColorBox(
            label, color, width=50, height=self.icicle_height, tooltip=tooltip
        )
        self.left_box.clicked.connect(self.clicked)
        self.left_box.clicked_signal.connect(self._on_clicked)
        self.h_layout.addWidget(self.left_box)

        # Right vertical layout container
        right_container = QWidget()
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)
        v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_container.setLayout(v_layout)

        # Container for children
        self.child_v_container = QWidget()
        self.child_v_container_layout = QVBoxLayout()
        self.child_v_container_layout.setContentsMargins(0, 0, 0, 0)
        self.child_v_container_layout.setSpacing(0)
        self.child_v_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.child_v_container.setLayout(self.child_v_container_layout)

        v_layout.addWidget(self.child_v_container)

        # Bottom colored box in the VBox
        self.bottom_box = ColorBox(
            label, "#000000", width=5, height=stop_here_count * height_mult
        )
        self.bottom_box.set_selected(True)
        v_layout.addWidget(self.bottom_box)

        # Add right container to HBox
        self.h_layout.addWidget(right_container)

        self.setLayout(self.h_layout)

    def add_sub_icicle(self, sub_icicle) -> None:
        sub_icicle.parent_icicle = self
        self.child_v_container_layout.addWidget(sub_icicle)

    def _on_clicked(self, mouse_event: QMouseEvent):
        if mouse_event.button() == Qt.MouseButton.LeftButton:
            self.selected_signal.emit(
                Selected(self), mouse_event.modifiers().value == Qt.Modifier.SHIFT.value
            )
        else:
            self.toggle_local_histogram()

    def toggle_local_histogram(self):
        if type(self.histogram) != HistogramWidget:
            data: list[float] = []
            if not self.parent_icicle is None:  # cast to icicle
                data = self.data.get_time_diffs(self.parent_icicle.data)

            self.histogram = HistogramWidget(data, self.icicle_height, 300, 4)
            self.h_layout.insertWidget(0, self.histogram)
        else:
            self.h_layout.removeWidget(self.histogram)
            self.histogram.deleteLater()
            self.histogram = QWidget()

    def clicked(self):
        if self.left_box.isChecked():
            data: list[float] = []
            if not self.parent_icicle is None:  # cast to icicle
                data = self.data.get_time_diffs(self.parent_icicle.data)

            self.histogram = HistogramWidget(data, self.icicle_height, 300, 3)
            self.h_layout.insertWidget(0, self.histogram)
        else:
            self.h_layout.removeWidget(self.histogram)
            self.histogram.deleteLater()
            self.histogram = QWidget()


class IciclePlot(QWidget):
    icicle_selection_signal = Signal(Icicle, Icicle)
    data: timeline.EventAggregate

    # left click
    selected_icicle_1: Selected | None
    # shift left click
    selected_icicle_2: Selected | None

    def __init__(
        self,
        data: timeline.EventAggregate,
        row_height: int,
        group_similar: bool,
        label: str = "",
    ):
        print("Creating IciclePlot")
        super().__init__()


        self.data = data
        self.row_height = row_height
        self.group_similar = group_similar
        self.selected_icicle_1 = None
        self.selected_icicle_2 = None

        scroll_area = QScrollArea(self)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        qlabel = QLabel(label)
        main_layout.addWidget(qlabel)
        self.main_icicle = self.to_icicle_recursive(data)
        main_layout.addWidget(scroll_area)
        scroll_area.setWidget(self.main_icicle)

    def _on_icicle_clicked(self, icicle_selected: Selected, shift: bool) -> None:
        if shift:
            if (
                not self.selected_icicle_2 is None
            ) and self.selected_icicle_2.obj == icicle_selected.obj:
                self.selected_icicle_2 = None
            else:
                self.selected_icicle_2 = icicle_selected
        else:
            if (
                not self.selected_icicle_1 is None
            ) and self.selected_icicle_1.obj == icicle_selected.obj:
                self.selected_icicle_1 = None
            else:
                self.selected_icicle_1 = icicle_selected
            self.selected_icicle_2 = None
        i1: Icicle | None = None
        i2: Icicle | None = None
        if not self.selected_icicle_1 is None:
            i1 = self.selected_icicle_1.obj
        if not self.selected_icicle_2 is None:
            i2 = self.selected_icicle_2.obj

        self.icicle_selection_signal.emit(i1, i2)

    def to_icicle_recursive(self, data: timeline.EventAggregate) -> Icicle:
        icicle = Icicle(data, self.row_height)
        icicle.selected_signal.connect(self._on_icicle_clicked)
        keys: list[str]

        if self.group_similar:
            keys = sorted(
                data.children.keys(),
                key=lambda k: data.children[k].color
                + str(f"{data.children[k].size:0>10}"),
                reverse=True,
            )
        else:
            keys = sorted(
                data.children.keys(),
                key=lambda k: data.children[k].size,
                reverse=True,
            )

        for key in keys:
            icicle.add_sub_icicle(self.to_icicle_recursive(data.children[key]))
        return icicle
