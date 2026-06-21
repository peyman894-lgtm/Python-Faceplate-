import os
import ctypes
import ctypes.wintypes

DLL_DIR = r"C:\Program Files (x86)\Elutions\ControlMaestro\ControlMaestro\Bin"
os.add_dll_directory(DLL_DIR)

# Wiz5API.dll — the GUI/display/macro layer
dll = ctypes.WinDLL(os.path.join(DLL_DIR, "WIZ5API.dll"))
print("WIZ5API.dll loaded OK")

# Still need a hook — but does THIS dll have its own MkClient, or share Wizpro's?
# Looking at the export list you shared, there's no MkClient here at all.
# This DLL likely expects a hook obtained from Wizpro.dll's CMMkClient.
wizpro = ctypes.WinDLL(os.path.join(DLL_DIR, "Wizpro.dll"))
wizpro.CMMkClient.restype  = ctypes.c_ushort
wizpro.CMMkClient.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.wintypes.HWND, ctypes.POINTER(ctypes.c_byte)]

hook = ctypes.c_byte(0)
rc = wizpro.CMMkClient(b"PythonClient", ctypes.c_int(1), ctypes.wintypes.HWND(0), ctypes.byref(hook))
print(f"CMMkClient rc={rc} hook={hook.value}")

dll.CMRunMacroByName.restype  = ctypes.c_ushort
dll.CMRunMacroByName.argtypes = [ctypes.c_byte, ctypes.c_char_p]

for macro_name in [b"PT_9200_70_1_CH", b"PT_9200_70_1_OSR"]:
    rc = dll.CMRunMacroByName(hook, macro_name)
    print(f"CMRunMacroByName('{macro_name.decode()}') rc={rc}")