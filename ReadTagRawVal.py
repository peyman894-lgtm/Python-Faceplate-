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

dll.CMGetGateRawValue.restype  = ctypes.c_ushort
dll.CMGetGateRawValue.argtypes = [ctypes.c_byte, ctypes.c_long, ctypes.POINTER(ctypes.c_ulong), ctypes.c_short]

hook = ctypes.c_byte(0)
rc = dll.CMMkClient(b"PythonClient", ctypes.c_int(1), ctypes.wintypes.HWND(0), ctypes.byref(hook))
print(f"CMMkClient rc={rc} hook={hook.value}")

gate_id = ctypes.c_long(0)
rc = dll.CMGetGateId(hook, b"LEVEL", ctypes.byref(gate_id))
print(f"CMGetGateId rc={rc} gate_id={gate_id.value}")

def read_level():
    raw_val = ctypes.c_ulong(0)
    dll.CMGetGateRawValue(hook, gate_id, ctypes.byref(raw_val), ctypes.c_short(1))
    return (raw_val.value >> 16) & 0xFFFF   # actual value is the high word

print("\nPolling LEVEL...")
for i in range(30):
    val = read_level()
    print(f"[{i}] LEVEL = {val}")
    time.sleep(2)