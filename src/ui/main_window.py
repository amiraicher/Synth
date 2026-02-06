from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDockWidget, QLabel
from PySide6.QtCore import Qt
from .synth_panel import SynthPanel
from .looper_panel import LooperPanel
from .visualizer import Visualizer
from .keyboard import VirtualKeyboard
from ..audio.engine import AudioEngine

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python DAW Lite - Cyberpunk Edition")
        self.resize(1200, 800)
        self.setFocusPolicy(Qt.StrongFocus) # Ensure we catch key events
        
        # Audio Engine Start
        self.audio_engine = AudioEngine()
        self.audio_engine.start()
        
        # Central Widget & Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.setSpacing(0)
        
        # Styling allows global theme.qss to take effect without conflicts
        # self.setStyleSheet(...) code removed


        # Top Section: Synth Panel & Visualizer
        top_layout = QHBoxLayout()
        
        # Synth Panel
        self.synth_panel = SynthPanel()
        top_layout.addWidget(self.synth_panel, stretch=1)
        
        # Visualizer
        self.visualizer = Visualizer()
        top_layout.addWidget(self.visualizer, stretch=1)
        
        main_layout.addLayout(top_layout, stretch=2)
        
        # Middle Section: Looper / Arrangement
        self.looper_panel = LooperPanel()
        main_layout.addWidget(self.looper_panel, stretch=3)
        
        # Bottom Section: Keyboard
        self.keyboard = VirtualKeyboard()
        self.keyboard.note_on_signal.connect(self.audio_engine.note_on)
        self.keyboard.note_off_signal.connect(self.audio_engine.note_off)
        main_layout.addWidget(self.keyboard, stretch=1)

    def keyPressEvent(self, event):
        # Forward to keyboard
        if not event.isAutoRepeat():
            self.keyboard.handle_key_press(event.key())
        else:
            # Swallow auto-repeat? Or let keyboard handle checks (it does)
            self.keyboard.handle_key_press(event.key())
            
    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.keyboard.handle_key_release(event.key())

    def closeEvent(self, event):
        self.audio_engine.stop()
        event.accept()
