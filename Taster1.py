"""
f_taster.py — PyQt5 port of the original Delphi TF_Taster form
(STR_Indication.exe Taster.DAT panel — ON/OFF + MOS Startup/Maintenance switches)

Original: bsNone border, stays-on-top, 171x678 px, German labels (Einblendregler).
This is a layout/structure port. Event handler bodies (EINClick, AUSClick,
MOS_SETClick, etc.) are stubs — wire them to CMPutGateVal/CMRunMacroByName
once we confirm which tags/macros each button should drive.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SwareButton(QPushButton):
    """Equivalent of the original TSwareCtl custom button (hand-cursor, blink-capable)."""
    def __init__(self, caption, parent=None):
        super().__init__(caption, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Arial", 11))
        self.setFixedSize(97, 33)


class OnOffPanel(QFrame):
    """ON_OFF panel: EIN (activate) / AUS (remove) / Confirm switches."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)

        self.lbl_ein = QLabel("T_EIN")
        self.lbl_aus = QLabel("T_AUS")

        self.btn_ein = SwareButton("activate")
        self.btn_aus = SwareButton("remove")
        self.btn_confirm = SwareButton("Confirm")

        self.btn_ein.clicked.connect(self.on_ein_click)
        self.btn_aus.clicked.connect(self.on_aus_click)
        self.btn_confirm.clicked.connect(self.on_confirm_click)

        layout.addWidget(self.lbl_ein)
        layout.addWidget(self.btn_ein)
        layout.addWidget(self.lbl_aus)
        layout.addWidget(self.btn_aus)
        layout.addWidget(self.btn_confirm)

    # ── Event handlers (wire to CM API here) ────────────────────────────
    def on_ein_click(self):
        print("EINClick — TODO: CMPutGateVal(valve_tag, 1)")

    def on_aus_click(self):
        print("AUSClick — TODO: CMPutGateVal(valve_tag, 0)")

    def on_confirm_click(self):
        print("Confirm click — TODO: CMRunMacroByName(...)")


class MosStartupPanel(QFrame):
    """MOS Startup panel: activate / remove / confirm."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        title = QLabel(" MOS-Startup")
        title.setAlignment(Qt.AlignCenter)
        title.setFrameShape(QFrame.Panel)
        title.setFrameShadow(QFrame.Sunken)

        self.btn_set_sa = SwareButton("activate")
        self.btn_reset_sa = SwareButton("remove")
        self.btn_confirm_sa = SwareButton("Confirm")
        self.btn_mos_set = SwareButton("activate")
        self.btn_mos_reset = SwareButton("activate")
        self.btn_confirm = SwareButton("Confirm")

        self.btn_set_sa.clicked.connect(lambda: print("MOS_SET_SAClick"))
        self.btn_reset_sa.clicked.connect(lambda: print("MOS_RESET_SAClick"))
        self.btn_confirm_sa.clicked.connect(lambda: print("CONFIRM_SAClick"))
        self.btn_mos_set.clicked.connect(lambda: print("MOS_SETClick"))
        self.btn_mos_reset.clicked.connect(lambda: print("MOS_RESETClick"))
        self.btn_confirm.clicked.connect(lambda: print("CONFIRMClick"))

        layout.addWidget(title)
        layout.addWidget(self.btn_set_sa)
        layout.addWidget(self.btn_reset_sa)
        layout.addWidget(self.btn_confirm_sa)

        maint_title = QLabel(" MOS-Maintenance")
        maint_title.setAlignment(Qt.AlignCenter)
        maint_title.setFrameShape(QFrame.Panel)
        maint_title.setFrameShadow(QFrame.Sunken)
        layout.addWidget(maint_title)
        layout.addWidget(self.btn_mos_set)
        layout.addWidget(self.btn_mos_reset)
        layout.addWidget(self.btn_confirm)


class MosMaintenancePanel(QFrame):
    """MOS1 panel: activate / remove / confirm (standalone maintenance panel)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        title = QLabel(" MOS-Maintenance")
        title.setAlignment(Qt.AlignCenter)
        title.setFrameShape(QFrame.Panel)
        title.setFrameShadow(QFrame.Sunken)

        self.btn_set = SwareButton("activate")
        self.btn_reset = SwareButton("remove")
        self.btn_confirm = SwareButton("Confirm")

        self.btn_set.clicked.connect(lambda: print("MOS_SETClick"))
        self.btn_reset.clicked.connect(lambda: print("MOS_RESETClick"))
        self.btn_confirm.clicked.connect(lambda: print("CONFIRMClick"))

        layout.addWidget(title)
        layout.addWidget(self.btn_set)
        layout.addWidget(self.btn_reset)
        layout.addWidget(self.btn_confirm)


class PasswordPanel(QFrame):
    """PW panel: password entry for MOS button."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.label = QLabel("enter Password")
        self.label.setFont(QFont("Arial", 11))

        self.edit = QLineEdit()
        self.edit.setEchoMode(QLineEdit.Password)
        self.edit.returnPressed.connect(self.on_enter)

        layout.addWidget(self.label)
        layout.addWidget(self.edit)

    def on_enter(self):
        print(f"Edit1KeyPress — password entered: {'*' * len(self.edit.text())}")


class FTaster(QWidget):
    """
    Main faceplate window — port of TF_Taster.
    Original: 171x678px, no border, stays on top.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Einblendregler")
        self.setFixedSize(171, 678)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(7, 13, 7, 13)

        # ── Header (instrument tag label, e.g. "LIRA-0900 / Sammelbeh. B090") ──
        header = QFrame()
        header.setFrameShape(QFrame.Panel)
        header.setFrameShadow(QFrame.Raised)
        header_layout = QVBoxLayout(header)

        self.lbl_tag = QLabel("LIRA-0900")
        self.lbl_tag.setAlignment(Qt.AlignCenter)
        self.lbl_tag.setFont(QFont("Arial Narrow", 12, QFont.Bold))

        self.lbl_desc = QLabel("Sammelbeh. B090")
        self.lbl_desc.setAlignment(Qt.AlignCenter)
        self.lbl_desc.setFont(QFont("Small Fonts", 8, QFont.Bold))

        header_layout.addWidget(self.lbl_tag)
        header_layout.addWidget(self.lbl_desc)
        main_layout.addWidget(header)

        # ── Stacked panel area (only one visible at a time, like the
        #    Delphi version's Visible=False toggling) ──────────────────
        self.stack = QStackedWidget()
        self.on_off_panel = OnOffPanel()
        self.mos_startup_panel = MosStartupPanel()
        self.mos_maint_panel = MosMaintenancePanel()
        self.pw_panel = PasswordPanel()

        self.stack.addWidget(self.on_off_panel)
        self.stack.addWidget(self.mos_startup_panel)
        self.stack.addWidget(self.mos_maint_panel)
        self.stack.addWidget(self.pw_panel)

        main_layout.addWidget(self.stack)

        # ── Bottom buttons ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.btn_lo = QPushButton("<")
        self.btn_ro = QPushButton(">")
        self.btn_lo.setFixedSize(27, 14)
        self.btn_ro.setFixedSize(27, 14)
        self.btn_lo.clicked.connect(self.on_lo_click)
        self.btn_ro.clicked.connect(self.on_ro_click)
        btn_row.addWidget(self.btn_lo)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_ro)
        main_layout.addLayout(btn_row)

        self.btn_mos = QPushButton("MOS")
        self.btn_mos.setCursor(Qt.PointingHandCursor)
        self.btn_mos.setFont(QFont("Arial", 11))
        self.btn_mos.clicked.connect(self.on_mos_click)
        main_layout.addWidget(self.btn_mos)

        self.btn_close = QPushButton("close VIEW")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.on_close_view)
        main_layout.addWidget(self.btn_close)

    # ── Event handlers — equivalents of FormCreate/FormActivate/etc ────
    def on_lo_click(self):
        print("LOClick")

    def on_ro_click(self):
        print("ROClick")

    def on_mos_click(self):
        print("Button1Click (MOS) — show password panel")
        self.stack.setCurrentWidget(self.pw_panel)

    def on_close_view(self):
        print("E_Regler_Zu (close VIEW)")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FTaster()
    window.show()
    sys.exit(app.exec_())