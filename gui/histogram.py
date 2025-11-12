import sys
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSizePolicy,
)
import matplotlib.ticker as ticker
from PySide6.QtCore import Qt
import math

class HistogramWidget(QWidget):
    def __init__(self, data, height: int = -1, width:int = 300, bins=10, parent=None):
        super().__init__(parent)

        # Create a Matplotlib figure and canvas
        self.figure = Figure(figsize=(4, 3), constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.setFixedWidth(width)
        if height > 0:
            self.setFixedHeight(height)
        else:
            self.setMaximumHeight(500)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Create a vertical layout and add the canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)
    
        # Plot the histogram
        self.plot_histogram(data, bins)

    def plot_histogram(self, data, num_bins):
        ax = self.figure.add_subplot(111)
        ax.clear()
        counts, bins, patches = ax.hist(data, bins=num_bins, color="skyblue", edgecolor="black")
        ax.set_xticks(bins)
        ax.set_ylabel("Frequency")
        
        max_count = max(counts)

        if max_count <= 20:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        elif max_count <= 200:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        elif max_count <= 2000:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(100))
        else:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(1000))

        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: str(int(x))))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{math.floor(int(x)/60)}:{(int(x)%60):0>2}" ))
        ax.set_xlabel("Time (HH:MM)")

        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt + Matplotlib Histogram")

        # Sample data
        data = np.random.normal(loc=0, scale=1, size=5)

        # Create and set the central widget
        hist_widget = HistogramWidget(data, 50, bins=3)
        self.setCentralWidget(hist_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
