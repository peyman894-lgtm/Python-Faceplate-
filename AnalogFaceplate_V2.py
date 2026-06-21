import os
import sys
import json
import ctypes
import ctypes.wintypes

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


# ==================================================
# SETTINGS
# ==================================================

INDICATOR_TAG = "INDICATOR"
LAYOUT_FILE = "faceplates.json"

# ==================================================
# ControlMaestro DLL
# ==================================================

DLL_DIR = r"C:\Program Files (x86)\Elutions\ControlMaestro\ControlMaestro\Bin"

os.add_dll_directory(DLL_DIR)

dll = ctypes.WinDLL(
    os.path.join(DLL_DIR, "Wizpro.dll")
)

# ==================================================
# API Definitions
# ==================================================

dll.CMMkClient.restype = ctypes.c_ushort
dll.CMMkClient.argtypes = [
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.wintypes.HWND,
    ctypes.POINTER(ctypes.c_byte)
]

dll.CMGetGateId.restype = ctypes.c_ushort
dll.CMGetGateId.argtypes = [
    ctypes.c_byte,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_long)
]

dll.CMGetGateVal.restype = ctypes.c_ushort
dll.CMGetGateVal.argtypes = [
    ctypes.c_byte,
    ctypes.c_ushort,
    ctypes.c_long,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_ulong),
    ctypes.POINTER(ctypes.c_ushort)
]

dll.CMGetGateStr.restype = ctypes.c_ushort

WGGV_CURRENT = 0

# ==================================================
# ONE GLOBAL CONTROLMAESTRO CONNECTION
# ==================================================

hook = ctypes.c_byte()

dll.CMMkClient(
    b"PythonFaceplateManager",
    1,
    ctypes.wintypes.HWND(0),
    ctypes.byref(hook)
)

print("Connected. Hook =", hook.value)

# ==================================================
# Get Indicator Gate ID
# ==================================================

indicator_gate_id = ctypes.c_long()

dll.CMGetGateId(
    hook,
    INDICATOR_TAG.encode(),
    ctypes.byref(indicator_gate_id)
)

print("Indicator Gate ID =", indicator_gate_id.value)

# ==================================================
# FACEPLATE
# ==================================================

class Faceplate(QWidget):

    def __init__(self, tag_name):
        super().__init__()

        self.tag_name = tag_name
        self.pinned = False

        self.gate_id = ctypes.c_long()

        dll.CMGetGateId(
            hook,
            tag_name.encode(),
            ctypes.byref(self.gate_id)
        )

        self.setWindowTitle(tag_name)
        self.setFixedSize(300, 180)

        layout = QVBoxLayout()

        self.pin_button = QPushButton("📍")
        self.pin_button.clicked.connect(
            self.toggle_pin
        )

        self.tag_label = QLabel(tag_name)
        self.tag_label.setAlignment(Qt.AlignCenter)
        self.tag_label.setFont(
            QFont("Arial", 12)
        )

        self.value_label = QLabel("0.00")
        self.value_label.setAlignment(
            Qt.AlignCenter
        )

        self.value_label.setFont(
            QFont("Consolas", 32, QFont.Bold)
        )

        self.value_label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: lime;
                border: 2px solid gray;
                padding: 10px;
            }
        """)

        layout.addWidget(self.pin_button)
        layout.addWidget(self.tag_label)
        layout.addWidget(self.value_label)

        self.setLayout(layout)

        self.load_position()

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.read_value
        )

        self.timer.start(1000)

    # --------------------------------

    def read_value(self):

        value = ctypes.c_double()
        sec = ctypes.c_ulong()
        msec = ctypes.c_ushort()

        dll.CMGetGateVal(
            hook,
            WGGV_CURRENT,
            self.gate_id,
            ctypes.byref(value),
            ctypes.byref(sec),
            ctypes.byref(msec)
        )

        self.value_label.setText(
            f"{value.value:.2f}"
        )

    # --------------------------------

    def toggle_pin(self):

        self.pinned = not self.pinned

        self.setWindowFlag(
            Qt.WindowStaysOnTopHint,
            self.pinned
        )

        if self.pinned:
            self.pin_button.setText("📌")
        else:
            self.pin_button.setText("📍")

        self.show()

    # --------------------------------

    def save_position(self):

        try:
            with open(LAYOUT_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {}

        data[self.tag_name] = {
            "x": self.x(),
            "y": self.y()
        }

        with open(LAYOUT_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # --------------------------------

    def load_position(self):

        try:
            with open(LAYOUT_FILE, "r") as f:
                data = json.load(f)

            if self.tag_name in data:

                self.move(
                    data[self.tag_name]["x"],
                    data[self.tag_name]["y"]
                )

        except:
            pass

    # --------------------------------

    def closeEvent(self, event):

        self.save_position()

        event.accept()


# ==================================================
# FACEPLATE MANAGER
# ==================================================

class FaceplateManager:

    def __init__(self):

        self.faceplates = {}

        self.last_indicator = ""

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.check_indicator
        )

        self.timer.start(500)

    # --------------------------------

    def read_indicator(self):

        buf = ctypes.create_string_buffer(256)

        dll.CMGetGateStr(
            hook,
            11,
            indicator_gate_id,
            buf,
            0,
            0
        )

        return buf.value.decode(
            errors="ignore"
        ).strip()

    # --------------------------------

    def check_indicator(self):

        tag_name = self.read_indicator()

        if not tag_name:
            return

        if tag_name == self.last_indicator:
            return

        self.last_indicator = tag_name

        print("Indicator =", tag_name)

        # Already open
        if tag_name in self.faceplates:

            fp = self.faceplates[tag_name]

            fp.raise_()
            fp.activateWindow()

            return

        # Create new faceplate
        fp = Faceplate(tag_name)

        fp.show()

        self.faceplates[tag_name] = fp


# ==================================================
# START APPLICATION
# ==================================================

app = QApplication(sys.argv)

manager = FaceplateManager()

sys.exit(app.exec_())