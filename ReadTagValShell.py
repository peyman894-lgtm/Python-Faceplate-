import os
import sys
import time
import ctypes
import ctypes.wintypes

DLL_DIR = r"C:\Program Files (x86)\Elutions\ControlMaestro\ControlMaestro\Bin"
os.add_dll_directory(DLL_DIR)

dll = ctypes.WinDLL(os.path.join(DLL_DIR, "Wizpro.dll"))

# --------------------------------------------------
# Command-line argument
# --------------------------------------------------

if len(sys.argv) < 2:
    print("Usage:")
    print("  python ReadTag.py TAG_NAME")
    print("")
    print("Example:")
    print("  python ReadTag.py PT_9200_70_1")
    sys.exit(1)

TAG_NAME = sys.argv[1].encode("ascii")

# --------------------------------------------------
# API declarations
# --------------------------------------------------

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
    ctypes.POINTER(ctypes.c_ushort),
]

WGGV_CURRENT = 0

# --------------------------------------------------
# Connect
# --------------------------------------------------

hook = ctypes.c_byte(0)

rc = dll.CMMkClient(
    b"PythonClient",
    1,
    ctypes.wintypes.HWND(0),
    ctypes.byref(hook)
)

print(f"CMMkClient rc={rc} hook={hook.value}")

if rc != 0:
    sys.exit(rc)

# --------------------------------------------------
# Get Gate ID
# --------------------------------------------------

gate_id = ctypes.c_long(0)

rc = dll.CMGetGateId(
    hook,
    TAG_NAME,
    ctypes.byref(gate_id)
)

print(f"CMGetGateId rc={rc} gate_id={gate_id.value}")

if rc != 0:
    sys.exit(rc)

# --------------------------------------------------
# Read continuously
# --------------------------------------------------

for i in range(30):

    val = ctypes.c_double(0.0)
    seconds = ctypes.c_ulong(0)
    msec = ctypes.c_ushort(0)

    rc = dll.CMGetGateVal(
        hook,
        WGGV_CURRENT,
        gate_id,
        ctypes.byref(val),
        ctypes.byref(seconds),
        ctypes.byref(msec)
    )

    print(
        f"{i:02d}  "
        f"{sys.argv[1]} = {val.value}  "
        f"(rc={rc})"
    )

    time.sleep(1)