from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                               QPushButton, QLabel, QFrame, QSplitter)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from ..audio.engine import AudioEngine

class TimelineWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(1000)
        self.setMinimumHeight(300)
        self.setStyleSheet("background-color: #15151a;")
        self.clips = [] # List of (track_index, start_time, duration, color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw Grid
        pen = QPen(QColor("#303035"))
        pen.setStyle(Qt.DotLine)
        painter.setPen(pen)
        
        # Vertical grid lines (Time)
        # Assuming 100px per bar for now
        for x in range(0, self.width(), 100):
            painter.drawLine(x, 0, x, self.height())
            
        # Horizontal grid lines (Tracks)
        # Assuming 60px height per track
        track_height = 60
        for y in range(0, self.height(), track_height):
            painter.drawLine(0, y, self.width(), y)
            
        # Draw Clips using placeholders
        # We will add mechanics later
        # Example ghost clip
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#00f0ff40")))
        painter.drawRoundedRect(50, 10, 200, 40, 5, 5)
        
        # Playhead
        # TODO: Get position from engine
        painter.setPen(QPen(QColor("#ff0055"), 2))
        painter.drawLine(100, 0, 100, self.height())


class TrackControlWidget(QFrame):
    def __init__(self, track_index, track_name):
        super().__init__()
        self.track_index = track_index
        self.engine = AudioEngine()
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(60) # Match timeline row height
        self.setStyleSheet("""
            QFrame {
                background-color: #202025;
                border: 1px solid #303035;
                border-right: 2px solid #00f0ff;
            }
            QLabel { color: #fff; font-weight: bold; }
            QPushButton {
                background-color: #303035;
                color: #aaa;
                border: none;
                border-radius: 2px;
                font-size: 10px;
            }
            QPushButton:checked {
                background-color: #00f0ff;
                color: #000;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.name_lbl = QLabel(track_name)
        layout.addWidget(self.name_lbl, stretch=1)
        
        self.rec_btn = QPushButton("R")
        self.rec_btn.setCheckable(True)
        self.rec_btn.setFixedWidth(20)
        self.rec_btn.setStyleSheet("QPushButton:checked { background-color: #ff0055; color: white; }")
        self.rec_btn.toggled.connect(lambda: self.engine.looper_toggle_record(self.track_index))
        
        self.mute_btn = QPushButton("M")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setFixedWidth(20)
        self.mute_btn.setStyleSheet("QPushButton:checked { background-color: #ffcc00; color: black; }")
        
        self.solo_btn = QPushButton("S")
        self.solo_btn.setCheckable(True)
        self.solo_btn.setFixedWidth(20)
        
        layout.addWidget(self.rec_btn)
        layout.addWidget(self.mute_btn)
        layout.addWidget(self.solo_btn)


class LooperPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = AudioEngine()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toolbar (Transport)
        toolbar = QFrame()
        toolbar.setFixedHeight(40)
        toolbar.setStyleSheet("background-color: #1a1a20; border-bottom: 1px solid #303035;")
        tb_layout = QHBoxLayout(toolbar)
        
        self.play_btn = QPushButton("PLAY")
        self.play_btn.clicked.connect(self.engine.transport_play)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.clicked.connect(self.engine.transport_stop)
        
        self.rec_global_btn = QPushButton("REC")
        self.rec_global_btn.clicked.connect(self.engine.transport_global_record)
        
        for btn in [self.play_btn, self.stop_btn, self.rec_global_btn]:
            btn.setFixedSize(60, 25)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #303035; 
                    color: #00f0ff; 
                    border: 1px solid #00f0ff;
                }
                QPushButton:pressed { background-color: #00f0ff; color: black; }
            """)
            tb_layout.addWidget(btn)
        
        tb_layout.addStretch()
        main_layout.addWidget(toolbar)
        
        # Splitter for Track List vs Timeline
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #00f0ff; }")
        
        # Track List Container
        self.track_list_widget = QWidget()
        self.track_layout = QVBoxLayout(self.track_list_widget)
        self.track_layout.setContentsMargins(0, 0, 0, 0)
        self.track_layout.setSpacing(1)
        self.track_layout.setAlignment(Qt.AlignTop)
        
        # Add Dummy Tracks
        for i in range(4):
            self.track_layout.addWidget(TrackControlWidget(i, f"Track {i+1}"))
            
        # Scroll Area for Tracks
        track_scroll = QScrollArea()
        track_scroll.setWidgetResizable(True)
        track_scroll.setWidget(self.track_list_widget)
        track_scroll.setFixedWidth(200)
        track_scroll.setStyleSheet("border: none;")
        
        # Timeline
        self.timeline = TimelineWidget()
        timeline_scroll = QScrollArea()
        timeline_scroll.setWidgetResizable(True) # Only resize if widget is smaller than view
        timeline_scroll.setWidget(self.timeline) # Timeline can grow larger
        timeline_scroll.setStyleSheet("border: none;")
        
        splitter.addWidget(track_scroll)
        splitter.addWidget(timeline_scroll)
        
        main_layout.addWidget(splitter)
