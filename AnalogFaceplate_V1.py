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
# Tag name from command line
# ==================================================

if len(sys.argv) < 2:
    print("Usage:")
    print("python AnalogFaceplate.py TAG_NAME")
    sys.exit()

TAG_NAME = sys.argv[1]

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

WGGV_CURRENT = 0

# ==================================================
# Connect to ControlMaestro
# ==================================================

hook = ctypes.c_byte()

dll.CMMkClient(
    b"PyQtFaceplate",
    1,
    ctypes.wintypes.HWND(0),
    ctypes.byref(hook)
)

gate_id = ctypes.c_long()

dll.CMGetGateId(
    hook,
    TAG_NAME.encode(),
    ctypes.byref(gate_id)
)

# ==================================================
# Faceplate
# ==================================================

class Faceplate(QWidget):

    def __init__(self):
        super().__init__()

        self.pinned = False

        self.setWindowTitle(TAG_NAME)

        # Fixed size
        self.setFixedSize(300, 180)

        layout = QVBoxLayout()

        # Pin Button
        self.pin_button = QPushButton("📍")
        self.pin_button.clicked.connect(self.toggle_pin)

        # Tag Label
        self.tag_label = QLabel(TAG_NAME)
        self.tag_label.setAlignment(Qt.AlignCenter)
        self.tag_label.setFont(QFont("Arial", 12))

        # Value Label
        self.value_label = QLabel("0.00")
        self.value_label.setAlignment(Qt.AlignCenter)

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

        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_value)
        self.timer.start(1000)

    # ------------------------------------------
    # Read Tag
    # ------------------------------------------

    def read_value(self):

        value = ctypes.c_double()
        sec = ctypes.c_ulong()
        msec = ctypes.c_ushort()

        dll.CMGetGateVal(
            hook,
            WGGV_CURRENT,
            gate_id,
            ctypes.byref(value),
            ctypes.byref(sec),
            ctypes.byref(msec)
        )

        self.value_label.setText(
            f"{value.value:.2f}"
        )

    # ------------------------------------------
    # Pin Window
    # ------------------------------------------

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

    # ------------------------------------------
    # Save Position
    # ------------------------------------------

    def save_position(self):

        try:
            with open(LAYOUT_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {}

        data[TAG_NAME] = {
            "x": self.x(),
            "y": self.y()
        }

        with open(LAYOUT_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # ------------------------------------------
    # Restore Position
    # ------------------------------------------

    def load_position(self):

        try:
            with open(LAYOUT_FILE, "r") as f:
                data = json.load(f)

            if TAG_NAME in data:

                self.move(
                    data[TAG_NAME]["x"],
                    data[TAG_NAME]["y"]
                )

        except:
            pass

    # ------------------------------------------
    # Save on Close
    # ------------------------------------------

    def closeEvent(self, event):

        self.save_position()

        event.accept()


# ==================================================
# Start Application
# ==================================================

app = QApplication(sys.argv)

window = Faceplate()
window.show()

sys.exit(app.exec_())