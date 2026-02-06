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
    
    # Load and apply QSS Stylesheet
    style_file = os.path.join(os.path.dirname(__file__), 'assets', 'styles', 'theme.qss')
    try:
        with open(style_file, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Warning: Stylesheet not found at {style_file}")
        # Fallback to Fusion if stylesheet is missing
        app.setStyle("Fusion")
    
    window = MainApplication()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
