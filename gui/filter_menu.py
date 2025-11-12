from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGroupBox,
    QVBoxLayout,
    QSizePolicy,
    QPushButton,
    QFormLayout,
    QCheckBox,
    QLineEdit,
    QSpinBox,
    QComboBox,
)
from PySide6.QtCore import Qt, QSettings, Signal

import os


class FilterMenu(QWidget):

    generate_plot_signal = Signal(dict)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("InfraVis", "PatientFlow")
        # Header
        header_group_box = QGroupBox("Data source")
        self.header_layout = QFormLayout()
        header_group_box.setLayout(self.header_layout)
        self.data_source = QLineEdit()

        self.data_source.setText(str(self.settings.value("data_source_dir", "")))
        self.data_source.textChanged.connect(
            lambda: self.settings.setValue("data_source_dir", self.data_source.text())
        )

        self.header_layout.addRow(QLabel("Source dir"), self.data_source)
        self.load_button = QPushButton("Refresh")
        self.load_button.clicked.connect(self.refresh)

        self.header_layout.addRow(self.load_button)

        # Rows
        rows_group_box = QGroupBox("Files")
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        rows_group_box.setLayout(self.rows_layout)
        self.rows: list[QCheckBox] = []

        # Which patients
        self.num_patients_spin_box = QSpinBox()

        self.num_patients_spin_box.setMaximum(1000000)
        num_p = self.settings.value("num_patients", 400, int)
        if type(num_p) is int:  # Cast to int
            self.num_patients_spin_box.setValue(num_p)
        self.num_patients_spin_box.valueChanged.connect(
            lambda x: self.settings.setValue("num_patients", x)
        )

        self.pick_from_cb = QComboBox()
        self.patient_attributes_cb = QComboBox()

        num_patients_layout = QFormLayout()
        num_patients_layout.addRow(QLabel("Num patients"), self.num_patients_spin_box)
        num_patients_layout.addRow(QLabel("Pick from"), self.pick_from_cb)
        num_patients_layout.addRow(
            QLabel("Patient attributes"), self.patient_attributes_cb
        )

        num_patients_widget = QGroupBox("Which patients")
        num_patients_widget.setLayout(num_patients_layout)

        # Display
        display_group_box = QGroupBox("Display")
        display_layout = QFormLayout()
        display_group_box.setLayout(display_layout)

        self.row_height_spin_box = QSpinBox()
        self.row_height_spin_box.setMaximum(1000000)
        row_height = self.settings.value("row_height", 40, int)
        if type(row_height) is int:
            self.row_height_spin_box.setValue(row_height)
        self.row_height_spin_box.valueChanged.connect(
            lambda x: self.settings.setValue("row_height", x)
        )

        display_layout.addRow(QLabel("Row height (px)"), self.row_height_spin_box)

        self.group_similar_cb = QCheckBox()

        group_similar = self.settings.value("group_similar", True, bool)
        if type(group_similar) is bool:
            self.group_similar_cb.setChecked(group_similar)
        self.group_similar_cb.checkStateChanged.connect(
            lambda x: self.settings.setValue("group_similar", x)
        )

        display_layout.addRow(QLabel("Group similar events"), self.group_similar_cb)
        # Generate
        self.generate_plot_button = QPushButton("Generate plot")
        self.generate_plot_button.clicked.connect(self.generate)

        # Main
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setFixedWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setLayout(self.main_layout)
        filter_label = QLabel("Data sources")

        self.main_layout.addWidget(filter_label)
        self.main_layout.addWidget(header_group_box)
        self.main_layout.addWidget(rows_group_box)
        self.main_layout.addWidget(num_patients_widget)
        self.main_layout.addWidget(display_group_box)
        self.main_layout.addWidget(self.generate_plot_button)
        self.refresh()

    def refresh(self):
        for c in self.rows:
            self.rows_layout.removeWidget(c)
            c.deleteLater()
        self.rows.clear()

        pf = self.settings.value("pick_from", "", str)
        pa = self.settings.value("patient_attributes", "", str)
        self.pick_from_cb.clear()

        self.patient_attributes_cb.clear()

        if not os.path.exists(self.data_source.text()):
            return

        files = os.listdir(self.data_source.text())
        files.sort()

        for p in files:
            cb = FilterCheck(p)
            self.rows_layout.addWidget(cb)
            self.rows.append(cb)
            self.pick_from_cb.addItem(p)
            self.patient_attributes_cb.addItem(p)

        if type(pf) is str:  # cast to str
            try:
                idx = files.index(pf)
                self.pick_from_cb.setCurrentIndex(idx)
            except:
                pass

        self.pick_from_cb.currentIndexChanged.connect(
            lambda x: self.settings.setValue("pick_from", files[x])
        )

        if type(pa) is str:  # cast to str
            try:
                idx = files.index(pa)
                self.patient_attributes_cb.setCurrentIndex(idx)
            except:
                pass

        self.patient_attributes_cb.currentIndexChanged.connect(
            lambda x: self.settings.setValue("patient_attributes", files[x])
        )

    def generate(self):
        data_paths: list[str] = []

        for fc in self.rows:
            if fc.isChecked():
                data_paths.append(self.data_source.text() + "/" + fc.text())

        out: dict = {
            "data_paths": data_paths,
            "num_patients": self.num_patients_spin_box.value(),
            "pick_from": self.data_source.text()
            + "/"
            + self.pick_from_cb.currentText(),
            "patient_attributes": self.data_source.text()
            + "/"
            + self.patient_attributes_cb.currentText(),
            "group_similar": self.group_similar_cb.checkState().value,
            "row_height": self.row_height_spin_box.value(),
        }
        self.generate_plot_signal.emit(out)


class FilterCheck(QCheckBox):
    path: str

    def __init__(self, path: str):
        super().__init__(path)
        self.path = path
        self.settings = QSettings("InfraVis", "PatientFlow")
        self.setChecked(bool(self.settings.value(path, True, bool)))
        self.checkStateChanged.connect(
            lambda x: self.settings.setValue(path, self.isChecked())
        )
