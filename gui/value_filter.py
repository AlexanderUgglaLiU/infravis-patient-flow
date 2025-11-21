import sys, os

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QScrollArea,
    QLabel,
    QFormLayout,
    QSpinBox,
    QCheckBox,
    QLineEdit
)
from PySide6.QtCore import Qt

from gui.gui_components import NoScrollComboBox
import pandas as pd


class ValueFilter(QWidget):

    def __init__(self):
        super().__init__()
        self.dir_path = ""

        layout = QFormLayout()
        self.setLayout(layout)
        self.filter_enabled_check_box = QCheckBox()

        self.file_combo_box = NoScrollComboBox()
        self.file_combo_box.currentIndexChanged.connect(self.update_columns)

        self.column_name_combo_box = NoScrollComboBox()

        self.min_value_spin_box = QSpinBox()
        self.min_value_spin_box.setMinimum(-1000000)
        self.min_value_spin_box.setMaximum(1000000)

        self.max_value_spin_box = QSpinBox()
        self.max_value_spin_box.setMinimum(-1000000)
        self.max_value_spin_box.setMaximum(1000000)

        layout.addRow(QLabel("Enabled"), self.filter_enabled_check_box)
        layout.addRow(QLabel("File"), self.file_combo_box)
        layout.addRow(QLabel("Value"), self.column_name_combo_box)
        layout.addRow(QLabel("Min"), self.min_value_spin_box)
        layout.addRow(QLabel("Max"), self.max_value_spin_box)

    def apply_filter(self, seq_ids: list[int]) -> list[int]:
        if not self.filter_enabled_check_box.isChecked():
            return seq_ids

        data = pd.read_csv(f"{self.dir_path}/{self.file_combo_box.currentText()}")
        data = data.loc[data["seqID"].isin(seq_ids)]
        data = data[
            data[self.column_name_combo_box.currentText()].between(
                self.min_value_spin_box.value(), self.max_value_spin_box.value()
            )
        ]

        return data["seqID"].to_list()

    def update_files(self, dir_path:str):
        self.dir_path = dir_path
        files = os.listdir(self.dir_path)
        
        self.file_combo_box.clear()
        self.file_combo_box.addItems(files)

    def update_columns(self):
        cols = pd.read_csv(f"{self.dir_path}/{self.file_combo_box.currentText()}").columns
        
        self.column_name_combo_box.clear()
        self.column_name_combo_box.addItems(cols.to_list())
