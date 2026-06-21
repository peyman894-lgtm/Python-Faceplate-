from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys


class AnalogFaceplate(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LIRA-0900")

        self.setFixedSize(171, 701)

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )

        self.build_ui()

    def build_ui(self):

        main = QVBoxLayout(self)

        # ==================================
        # Header
        # ==================================

        header = QFrame()
        header.setFrameShape(QFrame.Box)

        header_layout = QVBoxLayout(header)

        tag = QLabel("LIRA-0900")
        tag.setAlignment(Qt.AlignCenter)

        tag.setFont(
            QFont("Arial", 10, QFont.Bold)
        )

        desc = QLabel(
            "Sammelbeh. B0900"
        )

        desc.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(tag)
        header_layout.addWidget(desc)

        main.addWidget(header)

        # ==================================
        # Gauge
        # ==================================

        gauge_frame = QFrame()
        gauge_frame.setStyleSheet(
            "background:black;"
        )

        gauge_layout = QHBoxLayout(
            gauge_frame
        )

        self.gauge = QProgressBar()

        self.gauge.setOrientation(
            Qt.Vertical
        )

        self.gauge.setRange(0, 100)

        self.gauge.setValue(65)

        self.gauge.setTextVisible(False)

        self.gauge.setStyleSheet("""
            QProgressBar {
                background:black;
                border:1px solid gray;
            }

            QProgressBar::chunk {
                background:red;
            }
        """)

        gauge_layout.addStretch()
        gauge_layout.addWidget(self.gauge)
        gauge_layout.addStretch()

        main.addWidget(gauge_frame)

        # ==================================
        # Engineering Units
        # ==================================

        self.unit_label = QLabel(
            "0 - 100 %"
        )

        self.unit_label.setAlignment(
            Qt.AlignCenter
        )

        self.unit_label.setStyleSheet("""
            background:lightgray;
            font-weight:bold;
        """)

        main.addWidget(
            self.unit_label
        )

        # ==================================
        # Current Value
        # ==================================

        value_frame = QGroupBox(
            "Value"
        )

        value_layout = QVBoxLayout()

        self.value_label = QLabel(
            "75.3"
        )

        self.value_label.setAlignment(
            Qt.AlignCenter
        )

        self.value_label.setFont(
            QFont(
                "Consolas",
                18,
                QFont.Bold
            )
        )

        value_layout.addWidget(
            self.value_label
        )

        value_frame.setLayout(
            value_layout
        )

        main.addWidget(value_frame)

        # ==================================
        # Alarm Limits
        # ==================================

        limits = QGroupBox(
            "Alarm Limits"
        )

        grid = QGridLayout()

        grid.addWidget(
            QLabel("H2"),
            0, 0
        )

        self.h2 = QLabel("95")
        grid.addWidget(
            self.h2,
            0, 1
        )

        grid.addWidget(
            QLabel("H1"),
            1, 0
        )

        self.h1 = QLabel("85")
        grid.addWidget(
            self.h1,
            1, 1
        )

        grid.addWidget(
            QLabel("L1"),
            2, 0
        )

        self.l1 = QLabel("15")
        grid.addWidget(
            self.l1,
            2, 1
        )

        grid.addWidget(
            QLabel("L2"),
            3, 0
        )

        self.l2 = QLabel("5")
        grid.addWidget(
            self.l2,
            3, 1
        )

        limits.setLayout(grid)

        main.addWidget(limits)

        # ==================================
        # Buttons
        # ==================================

        chart_btn = QPushButton(
            "Chart"
        )

        limits_btn = QPushButton(
            "Grenzwerte"
        )

        mos_btn = QPushButton(
            "MOS"
        )

        close_btn = QPushButton(
            "Close View"
        )

        close_btn.clicked.connect(
            self.close
        )

        main.addWidget(chart_btn)
        main.addWidget(limits_btn)
        main.addWidget(mos_btn)

        main.addStretch()

        main.addWidget(close_btn)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = AnalogFaceplate()

    w.show()

    sys.exit(app.exec_())