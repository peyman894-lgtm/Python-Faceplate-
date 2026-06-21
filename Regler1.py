"""
form3.py — PyQt5 port of the original Delphi Form3 (analog faceplate)
(STR_Indication.exe Regler.DAT panel — vertical bar gauge with H2/H1/L1/L2 limits)

Original: 171x701px, bsNone border, stays-on-top, vertical TGauge bar (0-1000 internal
scale representing 0-100%), with limit-marker panels (G_0_O2/O1/U1/U2) positioned
along the bar, plus a live value readout, Chart/Limits/MOS buttons.

This is a layout/structure port. Event handlers and live gauge updates are stubs —
wire them to CMGetGateVal (polling) and CMPutGateVal/CMRunMacroByName (writes)
using the existing working CM API code.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor


class VerticalGauge(QProgressBar):
    """
    Equivalent of the original TGauge (gkVerticalBar, 0-1000 scale).
    Displays current process value as a vertical red bar, black background.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOrientation(Qt.Vertical)
        self.setRange(0, 1000)
        self.setValue(0)
        self.setTextVisible(False)
        self.setFixedSize(16, 246)
        self.setStyleSheet("""
            QProgressBar { background-color: black; border: none; }
            QProgressBar::chunk { background-color: red; }
        """)

    def set_percent(self, percent: float):
        """percent: 0-100 -> internal 0-1000 scale, matching original Gauge0_X.Progress."""
        self.setValue(int(max(0, min(100, percent)) * 10))


class LimitMarkersPanel(QWidget):
    """
    Scale tick marks (P_5...P_100) + colored limit indicator lines
    (G_0_O2/O1 yellow/red high, G_0_U1/U2 yellow/red low) next to the gauge.
    Positions are percentage-based along the 246px gauge height, matching DFM offsets.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 246)
        self.high2 = None   # H2 percent (red high limit)
        self.high1 = None   # H1 percent (yellow high limit)
        self.low1 = None    # L1 percent (yellow low limit)
        self.low2 = None    # L2 percent (red low limit)

    def set_limits(self, high2=None, high1=None, low1=None, low2=None):
        self.high2, self.high1, self.low1, self.low2 = high2, high1, low1, low2
        self.update()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QPen
        painter = QPainter(self)
        h = self.height()

        # Tick marks every 10%, matching P_10...P_100 panels
        painter.setPen(QPen(QColor("white"), 1))
        for pct in range(0, 101, 10):
            y = int(h - (pct / 100.0) * h)
            painter.drawLine(0, y, 6, y)

        # Limit lines
        def draw_limit(pct, color):
            if pct is not None:
                y = int(h - (pct / 100.0) * h)
                painter.setPen(QPen(QColor(color), 2))
                painter.drawLine(0, y, 14, y)

        draw_limit(self.high2, "red")
        draw_limit(self.high1, "yellow")
        draw_limit(self.low1, "yellow")
        draw_limit(self.low2, "red")


class LimitsPanel(QFrame):
    """Grenzwerte (Limits) panel: H2/H1/L1/L2 readouts."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: gray;")

        layout = QVBoxLayout(self)
        self.fields = {}
        for label_text, key in [("H2", "high2"), ("H1", "high1"), ("L1", "low1"), ("L2", "low2")]:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Arial", 11))
            val = QLabel("---")
            val.setStyleSheet("background-color: white; color: black;")
            val.setFixedWidth(85)
            val.setAlignment(Qt.AlignCenter)
            row.addWidget(lbl)
            row.addWidget(val)
            layout.addLayout(row)
            self.fields[key] = val

    def set_values(self, high2=None, high1=None, low1=None, low2=None):
        if high2 is not None: self.fields["high2"].setText(f"{high2:.1f}")
        if high1 is not None: self.fields["high1"].setText(f"{high1:.1f}")
        if low1 is not None:  self.fields["low1"].setText(f"{low1:.1f}")
        if low2 is not None:  self.fields["low2"].setText(f"{low2:.1f}")


class PasswordPanel(QFrame):
    """Edit1 — password entry for MOS button (hidden by default)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.edit = QLineEdit()
        self.edit.setEchoMode(QLineEdit.Password)
        self.edit.returnPressed.connect(self.on_enter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.edit)
        self.hide()

    def on_enter(self):
        print(f"Edit1KeyPress — password entered: {'*' * len(self.edit.text())}")


class Form3(QWidget):
    """
    Main analog faceplate window — port of Form3.
    Original: 171x701px, no border, stays on top.
    """
    def __init__(self, tag_name="LIRA-0900", description="Sammelbeh. B0900"):
        super().__init__()
        self.tag_name = tag_name
        self.setWindowTitle("Einblendregler")
        self.setFixedSize(171, 701)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(7, 13, 7, 13)
        main_layout.setSpacing(4)

        # ── Header (Z1_0 / Z2_0 — tag name / description) ──────────────
        header = QFrame()
        header.setFrameShape(QFrame.Panel)
        header.setFrameShadow(QFrame.Raised)
        header_layout = QVBoxLayout(header)

        self.lbl_tag = QLabel(tag_name)
        self.lbl_tag.setAlignment(Qt.AlignCenter)
        self.lbl_tag.setFont(QFont("Arial Narrow", 12, QFont.Bold))

        self.lbl_desc = QLabel(description)
        self.lbl_desc.setAlignment(Qt.AlignCenter)
        self.lbl_desc.setFont(QFont("Small Fonts", 8, QFont.Bold))

        header_layout.addWidget(self.lbl_tag)
        header_layout.addWidget(self.lbl_desc)
        main_layout.addWidget(header)

        # ── Gauge area (Panel4: gauge + limit markers) ──────────────────
        gauge_row = QHBoxLayout()
        gauge_row.addStretch()
        self.gauge = VerticalGauge()
        self.markers = LimitMarkersPanel()
        gauge_row.addWidget(self.gauge)
        gauge_row.addWidget(self.markers)
        gauge_row.addStretch()
        main_layout.addLayout(gauge_row)

        # ── Limits display (Grenz_0: H2/H1/L1/L2 readouts) ──────────────
        self.limits_panel = LimitsPanel()
        main_layout.addWidget(self.limits_panel)

        # ── Live value readout (Anz_0_X) ────────────────────────────────
        self.lbl_value = QLabel("---")
        self.lbl_value.setAlignment(Qt.AlignCenter)
        self.lbl_value.setStyleSheet("background-color: white; color: black;")
        self.lbl_value.setFont(QFont("Arial", 13, QFont.Bold))
        main_layout.addWidget(self.lbl_value)

        # ── Units label (EINH_0) ────────────────────────────────────────
        self.lbl_units = QLabel("0 - 100 %")
        self.lbl_units.setAlignment(Qt.AlignCenter)
        self.lbl_units.setStyleSheet("background-color: gray; color: yellow;")
        self.lbl_units.setFont(QFont("Arial Narrow", 10, QFont.Bold))
        main_layout.addWidget(self.lbl_units)

        # ── Buttons: Grenzwerte / Chart / MOS / close VIEW ──────────────
        self.btn_limits = QPushButton("Grenzwerte")
        self.btn_limits.setCursor(Qt.PointingHandCursor)
        self.btn_limits.clicked.connect(self.on_limits_click)
        main_layout.addWidget(self.btn_limits)

        self.btn_chart = QPushButton("Chart")
        self.btn_chart.setCursor(Qt.PointingHandCursor)
        self.btn_chart.clicked.connect(self.on_chart_click)
        main_layout.addWidget(self.btn_chart)

        self.btn_mos = QPushButton("MOS")
        self.btn_mos.setCursor(Qt.PointingHandCursor)
        self.btn_mos.clicked.connect(self.on_mos_click)
        main_layout.addWidget(self.btn_mos)

        self.pw_panel = PasswordPanel()
        main_layout.addWidget(self.pw_panel)

        self.btn_close = QPushButton("close VIEW")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.on_close_view)
        main_layout.addWidget(self.btn_close)

        # ── Bottom navigation (LO/RO: '<' / '>') ────────────────────────
        nav_row = QHBoxLayout()
        self.btn_lo = QPushButton("<")
        self.btn_ro = QPushButton(">")
        self.btn_lo.setFixedSize(27, 14)
        self.btn_ro.setFixedSize(27, 14)
        self.btn_lo.clicked.connect(self.on_lo_click)
        self.btn_ro.clicked.connect(self.on_ro_click)
        nav_row.addWidget(self.btn_lo)
        nav_row.addStretch()
        nav_row.addWidget(self.btn_ro)
        main_layout.addLayout(nav_row)

        # ── Live update timer — wire this to CMGetGateVal polling ───────
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.poll_tag_value)
        self.poll_timer.start(2000)  # 2s, matches our earlier Python polling tests

    # ── Live data hook — replace body with real CMGetGateVal call ───────
    def poll_tag_value(self):
        """
        TODO: wire to CM API, e.g.:
            val, rc, sec, ms = read_tag(self.tag_name)
            self.update_value(val)
        """
        pass

    def update_value(self, value: float, low_limit=0.0, high_limit=100.0):
        """Call this with a fresh reading to update gauge + readout."""
        pct = (value - low_limit) / (high_limit - low_limit) * 100.0
        self.gauge.set_percent(pct)
        self.lbl_value.setText(f"{value:.1f}")

    # ── Event handlers (equivalents of FormCreate/Click handlers) ───────
    def on_limits_click(self):
        print("Grenzwerte_0Click — TODO: toggle limits panel / open limits editor")

    def on_chart_click(self):
        print("Parameter_0Click — TODO: open trend chart")

    def on_mos_click(self):
        print("Button1Click (MOS) — show password panel")
        self.pw_panel.show()

    def on_close_view(self):
        print("E_Regler_Zu (close VIEW)")
        self.close()

    def on_lo_click(self):
        print("LOClick")

    def on_ro_click(self):
        print("ROClick")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Form3(tag_name="LIRA-0900", description="Sammelbeh. B0900")
    window.show()

    # Demo: simulate a live value for visual testing
    window.update_value(42.0)
    window.limits_panel.set_values(high2=90, high1=80, low1=20, low2=10)
    window.markers.set_limits(high2=90, high1=80, low1=20, low2=10)

    sys.exit(app.exec_())