from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtCore import Signal, Qt, QEvent, QPoint
from PySide6.QtGui import QTouchEvent, QEventPoint

class VirtualKeyboard(QWidget):
    note_on_signal = Signal(float)
    note_off_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
        
        # Remove layout, we will use absolute positioning (resizeEvent)
        # self.layout = QHBoxLayout(self) 
        
        self.setMinimumHeight(120)

        # Full definition of keys to help with ordering and identification
        # (Note Name, Frequency, IsBlackKey, PrecedingWhiteKeyIndex)
        # PrecedingWhiteKeyIndex: The white key index (0-based) after which this black key appears.
        # e.g. C# is after C (index 0). D# is after D (index 1).
        
        self.white_keys_data = [
            ("C", 261.63), ("D", 293.66), ("E", 329.63), ("F", 349.23),
            ("G", 392.00), ("A", 440.00), ("B", 493.88), 
            ("C2", 523.25), ("D2", 587.33), ("E2", 659.25), ("F2", 698.46),
            ("G2", 783.99), ("A2", 880.00), ("B2", 987.77), ("C3", 1046.50)
        ]
        
        # Correct indices for black keys:
        # Slot x means centered on boundary between White[x-1] and White[x]
        self.black_keys_spec = [
            ("C#", 277.18, 1),   # Between C(0) and D(1)
            ("D#", 311.13, 2),   # Between D(1) and E(2)
            ("F#", 369.99, 4),   # Between F(3) and G(4)
            ("G#", 415.30, 5),   # Between G(4) and A(5)
            ("A#", 466.16, 6),   # Between A(5) and B(6)
            
            ("C#2", 554.37, 8),  # Between C2(7) and D2(8)
            ("D#2", 622.25, 9),  # Between D2(8) and E2(9)
            ("F#2", 739.99, 11), # Between F2(10) and G2(11)
            ("G#2", 830.61, 12), # Between G2(11) and A2(12)
            ("A#2", 932.33, 13)  # Between A2(12) and B2(13)
        ]

        self.white_buttons = []
        self.black_buttons = []
        self.buttons_by_freq = {}
        
        # Create White Keys
        for name, freq in self.white_keys_data:
            btn = QPushButton(name, self)
            btn.setCheckable(False)
            btn.setFocusPolicy(Qt.NoFocus)
            # White Key Style: Dark background, Cyan border
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a20;
                    color: #00f0ff;
                    border: 1px solid #00f0ff;
                    border-bottom-left-radius: 4px;
                    border-bottom-right-radius: 4px;
                    text-align: bottom center;
                    padding-bottom: 5px;
                }
                QPushButton:pressed {
                    background-color: #00f0ff;
                    color: #101014;
                }
            """)
            btn.pressed.connect(lambda f=freq: self.note_on_signal.emit(f))
            btn.released.connect(lambda f=freq: self.note_off_signal.emit(f))
            self.white_buttons.append(btn)
            self.buttons_by_freq[freq] = btn

        # Create Black Keys
        for name, freq, slot_idx in self.black_keys_spec:
            btn = QPushButton(name, self)
            btn.setCheckable(False)
            btn.setFocusPolicy(Qt.NoFocus)
            # Black Key Style: Cyan/Dark mix, raised look
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #101014;
                    color: #00f0ff;
                    border: 1px solid #00f0ff;
                    border-top: none; 
                    border-bottom-left-radius: 2px;
                    border-bottom-right-radius: 2px;
                }
                QPushButton:pressed {
                    background-color: #00f0ff;
                    color: #101014;
                }
            """)
            btn.pressed.connect(lambda f=freq: self.note_on_signal.emit(f))
            btn.released.connect(lambda f=freq: self.note_off_signal.emit(f))
            self.black_buttons.append((btn, slot_idx))
            self.buttons_by_freq[freq] = btn

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
            Qt.Key_O: 554.37,  # C#2 (Bonus - not in visual but mappable)
            Qt.Key_L: 587.33   # D2 (Bonus)
        }
        self.active_keys = set()

    def resizeEvent(self, event):
        """Manually position keys to create a piano layout."""
        super().resizeEvent(event)
        
        w = self.width()
        h = self.height()
        
        count_white = len(self.white_buttons)
        if count_white == 0:
            return

        white_key_width = w / count_white
        
        # Position White Keys
        for i, btn in enumerate(self.white_buttons):
            x = i * white_key_width
            btn.setGeometry(int(x), 0, int(white_key_width), h)
            btn.lower() # Send to back

        # Position Black Keys
        # User Req: Width 30% of white key, Height 60% of white key
        black_key_width = white_key_width * 0.30
        black_key_height = h * 0.60
        
        for btn, slot_idx in self.black_buttons:
            # Slot Index determines the boundary line. 
            # Slot 1 means boundary between key 0 and 1. x = 1 * white_width - half_black_width
            center_x = slot_idx * white_key_width
            x = center_x - (black_key_width / 2)
            
            btn.setGeometry(int(x), 0, int(black_key_width), int(black_key_height))
            btn.raise_() # Bring to front

    def handle_key_press(self, key):
        if key in self.active_keys:
            return # Ignore auto-repeat
            
        if key in self.key_map:
            freq = self.key_map[key]
            self.active_keys.add(key)
            self.note_on_signal.emit(freq)
            # Visualize button press
            if freq in self.buttons_by_freq:
                self.buttons_by_freq[freq].setDown(True)

    def handle_key_release(self, key):
        if key in self.active_keys:
            if key in self.key_map:
                freq = self.key_map[key]
                self.active_keys.remove(key)
                self.note_off_signal.emit(freq)
                # Visualize button release
                if freq in self.buttons_by_freq:
                    self.buttons_by_freq[freq].setDown(False)

    def keyPressEvent(self, event):
        self.handle_key_press(event.key())

    def keyReleaseEvent(self, event):
        self.handle_key_release(event.key())

    def event(self, event):
        """Handle Touch Events for Multi-Touch Support."""
        t = event.type()
        if t in (QEvent.TouchBegin, QEvent.TouchUpdate, QEvent.TouchEnd):
            self._process_touch_event(event)
            return True
        return super().event(event)

    def _process_touch_event(self, event):
        # Map touch points to keys
        # We need to track which touch ID is holding which note to handle slides (glissando)
        if not hasattr(self, 'touch_map'):
            self.touch_map = {} # touch_id -> freq

        points = event.points()
        
        active_ids = set()

        for point in points:
            pid = point.id()
            active_ids.add(pid)
            state = point.state()
            
            if state == QEventPoint.Pressed or state == QEventPoint.Updated or state == QEventPoint.Stationary:
                # Find which key is under this point
                # Use globalPosition() to be safe and map to local
                pos = point.globalPosition()
                local_pos = self.mapFromGlobal(pos.toPoint())
                
                found_freq = None
                
                # Check Black Keys First (Z-Order)
                for btn, _ in self.black_buttons:
                    if btn.geometry().contains(local_pos):
                        # Find freq for this btn
                        for f, b in self.buttons_by_freq.items():
                            if b == btn:
                                found_freq = f
                                break
                        break
                
                # Check White Keys if no black key found
                if found_freq is None:
                    for btn in self.white_buttons:
                        if btn.geometry().contains(local_pos):
                             for f, b in self.buttons_by_freq.items():
                                if b == btn:
                                    found_freq = f
                                    break
                             break
                
                # Logic for status change
                original_freq = self.touch_map.get(pid)
                
                if found_freq != original_freq:
                    # If we were playing a note with this finger, stop it
                    if original_freq is not None:
                        self.note_off_signal.emit(original_freq)
                        if original_freq in self.buttons_by_freq:
                            self.buttons_by_freq[original_freq].setDown(False)
                    
                    # Start new note
                    if found_freq is not None:
                        self.note_on_signal.emit(found_freq)
                        if found_freq in self.buttons_by_freq:
                            self.buttons_by_freq[found_freq].setDown(True)
                        self.touch_map[pid] = found_freq
                    else:
                        # Finger moved off any key
                        if pid in self.touch_map:
                            del self.touch_map[pid]

            elif state == QEventPoint.Released:
                # Note Off
                freq = self.touch_map.get(pid)
                if freq is not None:
                    self.note_off_signal.emit(freq)
                    if freq in self.buttons_by_freq:
                        self.buttons_by_freq[freq].setDown(False)
                    del self.touch_map[pid]
        
        # Cleanup any stale IDs (though Released event should handle it)
        # In some cases, if a touch is cancelled, we might need to verify.
