from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QGroupBox, QDial
from PySide6.QtCore import Qt
from ..audio.engine import AudioEngine

class SynthPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = AudioEngine()
        
        main_layout = QHBoxLayout(self)
        
        # Oscillator Section
        osc_group = QGroupBox("OSCILLATOR")
        osc_layout = QVBoxLayout(osc_group)
        
        self.osc_combo = QComboBox()
        self.osc_combo.addItems(["saw", "sine", "square", "triangle"])
        self.osc_combo.currentTextChanged.connect(lambda t: self.engine.set_synth_param('osc_type', t))
        
        osc_layout.addWidget(QLabel("Waveform"))
        osc_layout.addWidget(self.osc_combo)
        main_layout.addWidget(osc_group)
        
        # Filter Section
        filter_group = QGroupBox("FILTER")
        filter_layout = QVBoxLayout(filter_group)
        
        self.cutoff_dial = self.create_dial("Cutoff", 20, 10000, 2000, lambda v: self.engine.set_synth_param('cutoff', v))
        self.res_dial = self.create_dial("Resonance", 0, 10, 7, lambda v: self.engine.set_synth_param('resonance', v / 10.0)) # 0.0 to 1.0 mostly
        
        filter_layout.addWidget(QLabel("Cutoff"))
        filter_layout.addWidget(self.cutoff_dial)
        filter_layout.addWidget(QLabel("Resonance"))
        filter_layout.addWidget(self.res_dial)
        main_layout.addWidget(filter_group)
        
        # Envelope Section
        env_group = QGroupBox("ENVELOPE (ADSR)")
        env_layout = QHBoxLayout(env_group)
        
        self.attack_slider = self.create_slider("A", 0, 100, 1, lambda v: self.engine.set_synth_param('attack', v / 100.0))
        self.decay_slider = self.create_slider("D", 0, 100, 10, lambda v: self.engine.set_synth_param('decay', v / 100.0))
        self.sustain_slider = self.create_slider("S", 0, 100, 70, lambda v: self.engine.set_synth_param('sustain', v / 100.0))
        self.release_slider = self.create_slider("R", 0, 100, 30, lambda v: self.engine.set_synth_param('release', v / 100.0))
        
        env_layout.addLayout(self.attack_slider)
        env_layout.addLayout(self.decay_slider)
        env_layout.addLayout(self.sustain_slider)
        env_layout.addLayout(self.release_slider)
        main_layout.addWidget(env_group)
        
        # Styling
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #00f0ff;
                margin-top: 20px;
                color: #00f0ff;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLabel { color: #00a8ff; }
            QSlider::groove:vertical {
                background: #1a1a20;
                width: 6px;
                border-radius: 3px;
            }
            QSlider::handle:vertical {
                background: #00f0ff;
                height: 10px;
                margin: 0 -4px;
                border-radius: 5px;
            }
            QDial {
                background-color: #101014; 
                /* QDial styling is tricky in CSS only, might keep default or basic */
            }
        """)

    def create_slider(self, label, min_val, max_val, default, callback):
        layout = QVBoxLayout()
        lbl = QLabel(label)
        slider = QSlider(Qt.Vertical)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(callback)
        layout.addWidget(slider, alignment=Qt.AlignHCenter)
        layout.addWidget(lbl, alignment=Qt.AlignHCenter)
        return layout

    def create_dial(self, label, min_val, max_val, default, callback):
        dial = QDial()
        dial.setRange(min_val, max_val)
        dial.setValue(default)
        dial.setNotchesVisible(True)
        dial.valueChanged.connect(callback)
        return dial
