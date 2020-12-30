import pyutilib.subprocess.GlobalData

# Pyomo multithreading error fix
pyutilib.subprocess.GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT = False
