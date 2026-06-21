import os
import ctypes
import ctypes.wintypes

DLL_DIR = r"C:\Program Files (x86)\Elutions\ControlMaestro\ControlMaestro\Bin"

os.add_dll_directory(DLL_DIR)

dll = ctypes.WinDLL(
    os.path.join(DLL_DIR, "Wizpro.dll")
)

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

# temporary guess based on Delphi export
dll.CMGetGateStr.restype = ctypes.c_ushort

hook = ctypes.c_byte()

dll.CMMkClient(
    b"FaceplateManager",
    1,
    ctypes.wintypes.HWND(0),
    ctypes.byref(hook)
)

gate_id = ctypes.c_long()

dll.CMGetGateId(
    hook,
    b"INDICATOR",
    ctypes.byref(gate_id)
)

buf = ctypes.create_string_buffer(256)

try:
    rc = dll.CMGetGateStr(
        hook,
        11,
        gate_id,
        buf,
        0,
        0
    )

    print("RC =", rc)
    print("Value =", buf.value.decode(errors="ignore"))

except Exception as e:
    print(e)