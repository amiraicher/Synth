
import sys
import os
sys.path.append(os.getcwd())

print("Checking imports...")
try:
    from src.audio.engine import AudioEngine
    from src.audio.looper import Looper
    from src.ui.main_window import MainApplication
    from src.ui.visualizer import Visualizer
    print("Imports success.")
except Exception as e:
    print(f"Import Error: {e}")
    sys.exit(1)

print("Checking AudioEngine init...")
try:
    engine = AudioEngine() # Singleton
    print("AudioEngine init success.")
except Exception as e:
    print(f"AudioEngine init error: {e}")

print("Checking UI init (requires QApplication)...")
from PySide6.QtWidgets import QApplication
app = QApplication([])

try:
    viz = Visualizer()
    print("Visualizer init success.")
except Exception as e:
    print(f"Visualizer init error: {e}")
    import traceback
    traceback.print_exc()

try:
    win = MainApplication()
    print("MainApplication init success.")
    win.close()
except Exception as e:
    print(f"MainApplication init error: {e}")
    import traceback
    traceback.print_exc()

print("Done.")
