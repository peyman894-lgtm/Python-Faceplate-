import os
import ctypes
import ctypes.wintypes

DLL_DIR = r"C:\Program Files (x86)\Elutions\ControlMaestro\ControlMaestro\Bin"
os.add_dll_directory(DLL_DIR)

dll = ctypes.WinDLL(os.path.join(DLL_DIR, "Wizpro.dll"))
print("DLL loaded OK")

dll.Wiz5MkClient.restype  = ctypes.c_byte
dll.Wiz5MkClient.argtypes = [
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.wintypes.HWND,
    ctypes.POINTER(ctypes.c_byte),
]

hook = ctypes.c_byte(0)
rc = dll.Wiz5MkClient(b"PythonClient", ctypes.c_int(1), ctypes.wintypes.HWND(0), ctypes.byref(hook))
print(f"Wiz5MkClient rc={rc} hook={hook.value}")