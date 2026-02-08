from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QGridLayout, QCheckBox)
from PySide6.QtCore import Qt, QTimer
from ..audio.engine import AudioEngine
from ..audio.looper import PodState

class PodWidget(QFrame):
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.engine = AudioEngine()
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedSize(120, 140)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5,5,5,5)
        
        # Header
        self.lbl_id = QLabel(f"POD {index+1}")
        self.lbl_id.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_id)
        
        # Main Trigger Pad
        self.trigger_btn = QPushButton("EMPTY")
        self.trigger_btn.setFixedSize(100, 60)
        self.trigger_btn.clicked.connect(self.on_trigger)
        layout.addWidget(self.trigger_btn)
        
        # Controls Row
        ctrl_layout = QHBoxLayout()
        
        self.btn_pause = QPushButton("||")
        self.btn_pause.setFixedSize(30, 25)
        self.btn_pause.setToolTip("Pause/Resume")
        self.btn_pause.setObjectName("pauseButton")
        self.btn_pause.clicked.connect(self.on_pause)
        
        self.btn_stop = QPushButton("⬛")
        self.btn_stop.setFixedSize(30, 25)
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.setObjectName("stopButton")
        self.btn_stop.clicked.connect(self.on_stop)
        
        ctrl_layout.addWidget(self.btn_pause)
        ctrl_layout.addWidget(self.btn_stop)
        layout.addLayout(ctrl_layout)
        
        # Repeat Toggle
        self.chk_repeat = QCheckBox("Repeat")
        self.chk_repeat.setChecked(True) # Default Loop
        self.chk_repeat.toggled.connect(self.on_repeat_toggled)
        layout.addWidget(self.chk_repeat)
        
        # Update Timer (Poll state for UI update)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui_state)
        self.timer.start(100) # 10fps update
        
    def on_trigger(self):
        self.engine.looper_trigger(self.index)
        self.update_ui_state() # Immediate update attempt
        
    def on_pause(self):
        self.engine.looper_pause(self.index)
        
    def on_stop(self):
        self.engine.looper_stop(self.index)

    def on_repeat_toggled(self, checked):
        self.engine.looper_set_repeat(self.index, checked)
        
    def update_ui_state(self):
        state = self.engine.looper_get_state(self.index)
        if state is None: return
        
        state_str = "empty"
        if state == PodState.EMPTY:
            self.trigger_btn.setText("REC")
            state_str = "empty"
        elif state == PodState.RECORDING:
            self.trigger_btn.setText("REC...")
            state_str = "recording"
        elif state == PodState.PLAYING:
            self.trigger_btn.setText("PLAYING")
            state_str = "playing"
        elif state == PodState.PAUSED:
            self.trigger_btn.setText("PAUSED")
            state_str = "paused"
        elif state == PodState.STOPPED:
            self.trigger_btn.setText("PLAY")
            state_str = "stopped"
            
        self.trigger_btn.setProperty("loopState", state_str)
        self.trigger_btn.style().unpolish(self.trigger_btn)
        self.trigger_btn.style().polish(self.trigger_btn)


class LooperPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = AudioEngine()
        
        main_layout = QVBoxLayout(self)
        
        # Header / Global Controls
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>LOOPER PODS</h2>"))
        header.addStretch()
        
        self.btn_stop_all = QPushButton("STOP ALL")
        self.btn_stop_all.setFixedSize(100, 30)
        self.btn_stop_all.setObjectName("stopAllButton")
        self.btn_stop_all.clicked.connect(self.engine.looper_stop_all)
        header.addWidget(self.btn_stop_all)
        
        main_layout.addLayout(header)
        
        # Grid of Pods
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.pods = []
        for i in range(10):
            pod = PodWidget(i)
            row = i // 5
            col = i % 5
            grid.addWidget(pod, row, col)
            self.pods.append(pod)
            
        main_layout.addLayout(grid)
        main_layout.addStretch()
