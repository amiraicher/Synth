
print("Start")
import sys
try:
    from PySide6.QtWidgets import QApplication
    print("Imported QApplication")
    app = QApplication(sys.argv)
    print("Created QApplication")
except Exception as e:
    print(f"Error: {e}")
print("Done")
