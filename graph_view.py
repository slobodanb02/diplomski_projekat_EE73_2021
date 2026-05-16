import matplotlib
# Use the generic QtAgg backend which automatically binds to PySide6
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton

class ErrorGraphDialog(QDialog):
    def __init__(self, graph_data, error_col_name, uncert_col_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historical Error & Uncertainty Analysis")
        self.resize(800, 500)
        
        self.graph_data = graph_data 
        
        self.error_col_name = error_col_name
        self.uncert_col_name = uncert_col_name
        
        self.layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.btn_close = QPushButton("Close Graph")
        self.btn_close.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_close)
        
        self.plot_error_data()

    def plot_error_data(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        years = sorted(self.graph_data.keys())
        
        errors = [self.graph_data[year].get(self.error_col_name, 0.0) for year in years]
        uncertainties = [self.graph_data[year].get(self.uncert_col_name, 0.0) for year in years]

        ax.errorbar(years, errors, yerr=uncertainties, fmt='o', 
                    color='#d62728',
                    ecolor='#1f77b4',
                    elinewidth=3,
                    capsize=6,
                    markersize=8,
                    linestyle='dashed',
                    linewidth=1)

        ax.set_title("Measurement Error & Uncertainty Over Time", fontsize=14, fontweight='bold')
        ax.set_xlabel("Calibration Year", fontsize=12)
        ax.set_ylabel(f"{self.error_col_name} ± {self.uncert_col_name}", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.figure.tight_layout()
        self.canvas.draw()