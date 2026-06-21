import os
import ctypes
import ctypes.wintypes
import time

DLL_DIR = r"C:\Program Files (x86)\Elutions\ControlMaestro\ControlMaestro\Bin"
os.add_dll_directory(DLL_DIR)

dll = ctypes.WinDLL(os.path.join(DLL_DIR, "Wizpro.dll"))

dll.CMMkClient.restype  = ctypes.c_ushort
dll.CMMkClient.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.wintypes.HWND, ctypes.POINTER(ctypes.c_byte)]

dll.CMGetGateId.restype  = ctypes.c_ushort
dll.CMGetGateId.argtypes = [ctypes.c_byte, ctypes.c_char_p, ctypes.POINTER(ctypes.c_long)]

dll.CMGetGateVal.restype  = ctypes.c_ushort
dll.CMGetGateVal.argtypes = [
    ctypes.c_byte,
    ctypes.c_ushort,
    ctypes.c_long,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_ulong),
    ctypes.POINTER(ctypes.c_ushort),
]

WGGV_CURRENT = 0

# Connect
hook = ctypes.c_byte(0)
dll.CMMkClient(b"PythonClient", ctypes.c_int(1), ctypes.wintypes.HWND(0), ctypes.byref(hook))

# Get tag ID
gate_id = ctypes.c_long(0)
dll.CMGetGateId(hook, b"PT_9200_70_1", ctypes.byref(gate_id))

# Read value



for i in range(30):
    print(i)
    val = ctypes.c_double(0.0)
    seconds = ctypes.c_ulong(0)
    msec = ctypes.c_ushort(0)
    dll.CMGetGateVal(hook, ctypes.c_ushort(WGGV_CURRENT), gate_id,
                  ctypes.byref(val), ctypes.byref(seconds), ctypes.byref(msec))
    print(f"PT_9200_70_1 = {val.value}")
    
    time.sleep(1)