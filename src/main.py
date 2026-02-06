import sys
import os

# Add project root level to sys.path so 'src' module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import setup_logging
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainApplication

def main():
    log_path = setup_logging()
    
    app = QApplication(sys.argv)
    
    # Set Fusion Style for consistent dark theme base
    app.setStyle("Fusion")
    
    window = MainApplication()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
