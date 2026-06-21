from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys


class TasterForm(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Einblendregler")

        self.setFixedSize(171, 678)

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )

        main = QVBoxLayout(self)
        main.setContentsMargins(4,4,4,4)

        # =====================================
        # Header
        # =====================================

        header = QFrame()
        header.setFrameShape(QFrame.Box)

        header_layout = QVBoxLayout(header)

        tag1 = QLabel("LIRA-0900")
        tag1.setAlignment(Qt.AlignCenter)
        tag1.setFont(QFont("Arial", 10, QFont.Bold))

        tag2 = QLabel("Sammelbeh. B090")
        tag2.setAlignment(Qt.AlignCenter)
        tag2.setFont(QFont("Arial", 8))

        header_layout.addWidget(tag1)
        header_layout.addWidget(tag2)

        main.addWidget(header)

        # =====================================
        # MOS Button
        # =====================================

        self.mos_btn = QPushButton("MOS")
        self.mos_btn.setMinimumHeight(50)

        main.addWidget(self.mos_btn)

        # =====================================
        # Password Panel
        # =====================================

        self.pw_panel = QGroupBox("Password")
        pw_layout = QVBoxLayout()

        pw_layout.addWidget(
            QLabel("Enter Password")
        )

        self.password = QLineEdit()
        self.password.setEchoMode(
            QLineEdit.Password
        )

        pw_layout.addWidget(self.password)

        self.pw_panel.setLayout(pw_layout)

        self.pw_panel.hide()

        main.addWidget(self.pw_panel)

        # =====================================
        # MOS Startup
        # =====================================

        self.mos_startup = QGroupBox(
            "MOS Startup"
        )

        startup_layout = QVBoxLayout()

        startup_layout.addWidget(
            QPushButton("Activate")
        )

        startup_layout.addWidget(
            QPushButton("Remove")
        )

        startup_layout.addWidget(
            QPushButton("Confirm")
        )

        self.mos_startup.setLayout(
            startup_layout
        )

        main.addWidget(self.mos_startup)

        # =====================================
        # MOS Maintenance
        # =====================================

        self.mos_maint = QGroupBox(
            "MOS Maintenance"
        )

        maint_layout = QVBoxLayout()

        maint_layout.addWidget(
            QPushButton("Activate")
        )

        maint_layout.addWidget(
            QPushButton("Remove")
        )

        maint_layout.addWidget(
            QPushButton("Confirm")
        )

        self.mos_maint.setLayout(
            maint_layout
        )

        main.addWidget(self.mos_maint)

        # =====================================
        # ON OFF
        # =====================================

        self.onoff = QGroupBox(
            "ON / OFF"
        )

        onoff_layout = QVBoxLayout()

        onoff_layout.addWidget(
            QLabel("T_EIN")
        )

        onoff_layout.addWidget(
            QPushButton("ON")
        )

        onoff_layout.addWidget(
            QLabel("T_AUS")
        )

        onoff_layout.addWidget(
            QPushButton("OFF")
        )

        onoff_layout.addWidget(
            QPushButton("Confirm")
        )

        self.onoff.setLayout(
            onoff_layout
        )

        main.addWidget(self.onoff)

        main.addStretch()

        # =====================================
        # Close Button
        # =====================================

        close_btn = QPushButton(
            "Close View"
        )

        close_btn.clicked.connect(
            self.close
        )

        main.addWidget(close_btn)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = TasterForm()

    w.show()

    sys.exit(app.exec_())