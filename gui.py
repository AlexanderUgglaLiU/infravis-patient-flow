import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QScrollArea,
)
from PySide6.QtCore import Qt

from data import create_aggregate

from gui.icicle_plot import IciclePlot
from gui.filter_menu import FilterMenu
from gui.data_display_menu import DataDisplayMenu
from gui.collapsable_widget import HideBox

class Main(QGroupBox):

    def __init__(self):
        super().__init__()
        self.window_layout = QHBoxLayout()
        self.window_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.window_layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        left_panel_layout = QVBoxLayout()
        left_panel_widget = QWidget()
        left_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_panel_widget.setLayout(left_panel_layout)

        self.filter_menu = FilterMenu()
        hb_filter_manu = HideBox("Generating", self.filter_menu)
        left_panel_layout.addWidget(hb_filter_manu)
        self.data_display_menu = DataDisplayMenu()
        left_panel_layout.addWidget(self.data_display_menu)

        scroll_area = QScrollArea(self)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(475)
        scroll_area.setWidget(left_panel_widget)

        self.window_layout.addWidget(scroll_area)

        self.icicle_plot = QWidget()  # dummy
        self.window_layout.addWidget(self.icicle_plot)

        self.filter_menu.generate_plot_signal.connect(lambda d: self.create_icicle(d))

    def create_icicle(self, data: dict):
        agg = create_aggregate(
            data["data_paths"],
            data["pick_from"],
            data["patient_attributes"],
            data["num_patients"],
        )
        self.window_layout.removeWidget(self.icicle_plot)
        self.icicle_plot = IciclePlot(
            agg.event_aggregate_root, data["row_height"], data["group_similar"]
        )
        self.window_layout.addWidget(self.icicle_plot)
        self.icicle_plot.icicle_selection_signal.connect(self.data_display_menu.display)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.resize(1500, 1000)
    main.setWindowTitle("ER Patient Flow Visualizer")
    main.show()
    sys.exit(app.exec())
