import sys
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy


class DataPoint:
    def __init__(self, title: str, count: int, color: str = "#466681") -> None:
        self.title = title
        self.count = count
        self.color = color


class SingleBarWidget(QWidget):
    def __init__(self, title: str, data_points: list[DataPoint]):
        super().__init__()

        self.title = title
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # self.setFixedHeight(175)
        # Layout
        layout = QVBoxLayout(self)

        # Matplotlib Figure + Canvas
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        
        layout.addWidget(self.canvas)

        # Draw the plot
        self.draw_chart(data_points)

    def draw_chart(self, data_points: list[DataPoint]):
        ax = self.figure.add_subplot(111)
        text_color = "white"
        acc = 0
        for dp in data_points:
            rect = ax.barh([dp.title], [dp.count], left=0, color=dp.color, label=dp.title, height=0.8)
            ax.bar_label(rect, label_type="center", color=text_color, labels=[f"{dp.count} {dp.title}"]) #
            # ax.annotate("hello", (0., 0.))
            acc += dp.count
        ax.set_yticks([0])
        # ax.set_yticklabels(["Gender"])
        # ax.set_title(self.title)
        ax.legend(
            bbox_to_anchor=(0, 1),
            ncol=len(data_points),
            loc='lower left', fontsize='small'
        )

        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SingleBarWidget(
        "Gender whow",
        [DataPoint("Man", 10, "#555599"), DataPoint("Woman", 50, "#995571"), DataPoint("Man", 10, "#555599"), DataPoint("Woman", 50, "#995571")],
    )
    window.setWindowTitle("Gender Chart Example (PySide6)")
    window.resize(600, 400)
    window.show()

    sys.exit(app.exec())
