from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt

class VirtualKeyboard(QWidget):
    note_on_signal = Signal(float)
    note_off_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Key Mapping (PC Key -> Note Name)
        # Just a visual representation for now, simpler than full key map logic in UI
        # We will create buttons C3 to C5
        self.notes = [
            ("C", 261.63), ("C#", 277.18), ("D", 293.66), ("D#", 311.13),
            ("E", 329.63), ("F", 349.23), ("F#", 369.99), ("G", 392.00),
            ("G#", 415.30), ("A", 440.00), ("A#", 466.16), ("B", 493.88),
            ("C2", 523.25)
        ]
        
        self.buttons = {}
        
        for name, freq in self.notes:
            btn = QPushButton(name)
            btn.setCheckable(False)
            btn.setFocusPolicy(Qt.NoFocus) # Prevent button from stealing keyboard focus
            btn.setFixedHeight(100)
            
            # Styling
            if "#" in name:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #202025;
                        color: #00f0ff;
                        border: 1px solid #00f0ff;
                        border-radius: 4px;
                        margin-bottom: 40px; /* Make it look like a black key */
                    }
                    QPushButton:pressed {
                        background-color: #00f0ff;
                        color: #000;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #101014;
                        color: #00f0ff;
                        border: 1px solid #00f0ff;
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: #00f0ff;
                        color: #000;
                    }
                """)
                
            btn.pressed.connect(lambda f=freq: self.note_on_signal.emit(f))
            btn.released.connect(lambda f=freq: self.note_off_signal.emit(f))
            
            self.layout.addWidget(btn)
            self.buttons[freq] = btn

        # PC Keyboard Mapping (Qt Key -> Frequency)
        self.key_map = {
            Qt.Key_A: 261.63,  # C
            Qt.Key_W: 277.18,  # C#
            Qt.Key_S: 293.66,  # D
            Qt.Key_E: 311.13,  # D#
            Qt.Key_D: 329.63,  # E
            Qt.Key_F: 349.23,  # F
            Qt.Key_T: 369.99,  # F#
            Qt.Key_G: 392.00,  # G
            Qt.Key_Y: 415.30,  # G#
            Qt.Key_H: 440.00,  # A
            Qt.Key_U: 466.16,  # A#
            Qt.Key_J: 493.88,  # B
            Qt.Key_K: 523.25,  # C2
            Qt.Key_O: 554.37,  # C#2 (Bonus)
            Qt.Key_L: 587.33   # D2 (Bonus)
        }
        self.active_keys = set()

    def handle_key_press(self, key):
        if key in self.active_keys:
            return # Ignore auto-repeat
            
        if key in self.key_map:
            freq = self.key_map[key]
            self.active_keys.add(key)
            self.note_on_signal.emit(freq)
            # Visualize button press
            if freq in self.buttons:
                self.buttons[freq].setDown(True)

    def handle_key_release(self, key):
        if key in self.active_keys:
            if key in self.key_map:
                freq = self.key_map[key]
                self.active_keys.remove(key)
                self.note_off_signal.emit(freq)
                # Visualize button release
                if freq in self.buttons:
                    self.buttons[freq].setDown(False)

    def keyPressEvent(self, event):
        self.handle_key_press(event.key())

    def keyReleaseEvent(self, event):
        self.handle_key_release(event.key())
