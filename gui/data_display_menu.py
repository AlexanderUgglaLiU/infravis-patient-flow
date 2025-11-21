from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSettings

from gui.histogram import HistogramWidget
from gui.icicle_plot import Icicle
from data import get_patient_attribute_aggregate, AggregateDict
from gui.gui_components import ColorBox

import gui.stacked_bar as sb


class DataDisplayMenu(QGroupBox):

    def __init__(self):
        super().__init__("Data display")
        self.settings = QSettings("InfraVis", "PatientFlow")
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
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
        self.patient_data_vis = QWidget()  # dummy
        self.patient_data = QLabel()
        self.patient_data.setWordWrap(True)

        self.main_layout.addWidget(title_label_widget)
        self.main_layout.addWidget(self.histogram)
        # self.main_layout.addWidget(self.patient_data_vis)
        self.main_layout.addWidget(self.patient_data)

    def display(self, i1: Icicle | None, i2: Icicle | None) -> None:
        self.main_layout.removeWidget(self.histogram)
        self.histogram.deleteLater()

        # self.main_layout.removeWidget(self.patient_data_vis)
        # self.patient_data_vis.deleteLater()

        self.from_event_label.setText("<from>" if i1 is None else i1.data.key)
        self.to_event_label.setText("<to>" if i2 is None else i2.data.key)

        # Histogram
        if (i1 is None) or (i2 is None):
            self.histogram = QWidget()
            # self.patient_data_vis = QWidget()
        else:
            data = i1.data.get_time_diffs(i2.data)
            self.histogram = HistogramWidget(data, 500, 350, 5)
            self.main_layout.addWidget(self.histogram)

        # Data
        seq_ids:list[int] = []
        if (i1 is None) and (i2 is None):
            self.patient_data.setText("")
            return
        elif not((i1 is None) or (i2 is None)):
            seq_ids = i1.data.get_common_seqids(i2.data)
        elif not(i1 is None):
            seq_ids = list(i1.data.events.keys())
        elif not(i2 is None):
            seq_ids = list(i2.data.events.keys())

        if len(seq_ids) == 0:
            self.patient_data.setText("No common sequences")
            return

        pa = (
            str(self.settings.value("data_source_dir", ""))
            + "/"
            + str(self.settings.value("patient_attributes", "", str))
        )
        agg_dict = get_patient_attribute_aggregate(pa, seq_ids)
        self.patient_data.setText(str(agg_dict))

        # self.patient_data_vis = PatientDataVis(agg_dict)
        # self.main_layout.addWidget(self.patient_data_vis)

class ColorLabel(QLabel):
    def __init__(self,text:str, color:str, width: int, height: int, tooltip:str):
        super().__init__(text)
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # label = QLabel(text)
        self.setStyleSheet(
            f"""
                border: 0px solid black;
                background-color: {color};
                margin: 2px;
            """
        )
        self.setToolTip(tooltip)

class StackedBar(QWidget):
    def __init__(self, data: list[sb.DataPoint], width: int, height: int = 40):
        super().__init__()
        # self.setFixedWidth(width)
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        total_count = 0.0
        for d in data:
            total_count += d.count

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

        acc_width = 0
        for d in data:
            print(">>", (d.count / total_count) * width, round((d.count / total_count) * width))
            cell_width = round((d.count / total_count) * width)
            acc_width += cell_width
            bar = ColorLabel(
                f"{d.title}: {d.count}",
                d.color,
                cell_width,
                height,
                f"{d.title}: {d.count}",
            )
            layout.addWidget(bar)
        print(width, acc_width)
        self.setFixedWidth(acc_width)


class PatientDataVis(QWidget):

    def __init__(self, agg_dict: AggregateDict):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # gender
        main_layout.addWidget(QLabel("Gender"))

        for d_keys in agg_dict.data_discrete.keys():
            data_gender = []
            agg_gender = agg_dict.data_discrete[d_keys]
            for key in sorted(agg_gender.keys()):
                color: str
                match key.lower():
                    case "kvinna":
                        color = "#af3f3f"

                    case "man":
                        color = "#5C5CCC"

                    case _:
                        color = "#727777"

                data_gender.append(sb.DataPoint(key, agg_gender[key], color))

            main_layout.addWidget(StackedBar(data_gender, 300, 40))
            main_layout.addWidget(sb.SingleBarWidget(d_keys, data_gender))
