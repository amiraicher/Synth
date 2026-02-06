from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QTimer, Qt
import pyqtgraph as pg
import numpy as np
from ..audio.engine import AudioEngine

class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = AudioEngine()
        
        # Main Layout (Vertical)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # PyQtGraph Config
        pg.setConfigOption('background', '#101014')
        pg.setConfigOption('foreground', '#00f0ff')
        pg.setConfigOption('antialias', True)
        
        # --- Oscilloscope (Top) ---
        self.osc_plot = pg.PlotWidget(title="OSCILLOSCOPE")
        self.osc_plot.setYRange(-1.0, 1.0)
        self.osc_plot.showGrid(x=True, y=True, alpha=0.3)
        self.osc_plot.getPlotItem().hideAxis('bottom')
        self.osc_plot.getPlotItem().hideAxis('left')
        
        # Curves
        self.osc_curve = self.osc_plot.plot(pen=pg.mkPen(color='#00f0ff', width=2))
        self.glow_curve = self.osc_plot.plot(pen=pg.mkPen(color='#00f0ff20', width=6))
        
        main_layout.addWidget(self.osc_plot, stretch=2)
        
        # --- Bottom Row (Spectrum + ADSR) ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)
        
        # 1. Spectrum Analyzer
        self.fft_plot = pg.PlotWidget(title="SPECTRUM")
        self.fft_plot.setLogMode(x=True, y=False)
        self.fft_plot.setYRange(0, 1)
        self.fft_plot.getPlotItem().hideAxis('left')
        self.fft_plot.getPlotItem().setLabel('bottom', 'Frequency', units='Hz')
        
        self.fft_curve = self.fft_plot.plot(pen=pg.mkPen(color='#00a8ff', width=1), fillLevel=0, brush=(0, 168, 255, 50))
        bottom_row.addWidget(self.fft_plot, stretch=1)
        
        # 2. ADSR Envelope Graph
        self.adsr_plot = pg.PlotWidget(title="ENVELOPE")
        self.adsr_plot.setYRange(0, 1.1)
        self.adsr_plot.getPlotItem().hideAxis('left')
        self.adsr_plot.getPlotItem().setLabel('bottom', 'Time', units='s')
        
        self.adsr_curve = self.adsr_plot.plot(pen=pg.mkPen(color='#ff00ff', width=2), fillLevel=0, brush=(255, 0, 255, 30))
        
        bottom_row.addWidget(self.adsr_plot, stretch=1)
        
        main_layout.addLayout(bottom_row, stretch=2)
        
        # Update Timer (30 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(33)

    def update_plots(self):
        # --- 1. Audio Buffer Updates ---
        buffer = self.engine.get_buffer()
        if buffer is not None and len(buffer) > 0:
            # Oscilloscope
            self.osc_curve.setData(buffer)
            self.glow_curve.setData(buffer)
            
            # FFT
            fft_data = np.fft.rfft(buffer)
            fft_mag = np.abs(fft_data)
            # Normalize
            if len(buffer) > 0:
                fft_mag = fft_mag / (len(buffer) / 2)
            
            # Frequency Axis
            freqs = np.linspace(20, self.engine.sample_rate / 2, len(fft_mag))
            self.fft_curve.setData(freqs, fft_mag)
            
        # --- 2. ADSR Visualization Update ---
        # Get current params from engine
        # Note: Accessing internal structure strictly, but for visualizer tight coupling is acceptable
        try:
            params = self.engine.voice_manager.params
            a = params.get('attack', 0.01)
            d = params.get('decay', 0.1)
            s_level = params.get('sustain', 0.7)
            r = params.get('release', 0.3)
            
            # Construct points for the ADSR shape
            # Phases: 
            # 0: Start (0,0)
            # 1: Attack End (A, 1.0)
            # 2: Decay End (A+D, S)
            # 3: Sustain Hold (A+D+Hold, S) - Arbitrary hold time for viz
            # 4: Release End (A+D+Hold+R, 0)
            
            hold_time = 0.5 # Visual representation of holding the key
            
            t0 = 0
            t1 = a
            t2 = a + d
            t3 = a + d + hold_time
            t4 = a + d + hold_time + r
            
            x = [t0, t1, t2, t3, t4]
            y = [0.0, 1.0, s_level, s_level, 0.0]
            
            self.adsr_curve.setData(x, y)
             
        except AttributeError:
             pass # Engine might not be fully initialized or structure changed

