from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Qt
import pyqtgraph as pg
import numpy as np
from ..audio.engine import AudioEngine

class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = AudioEngine()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # PyQtGraph Config
        pg.setConfigOption('background', '#101014')
        pg.setConfigOption('foreground', '#00f0ff')
        
        # Oscilloscope
        self.osc_plot = pg.PlotWidget(title="OSCILLOSCOPE")
        self.osc_plot.setYRange(-1.0, 1.0)
        self.osc_plot.showGrid(x=True, y=True, alpha=0.3)
        self.osc_curve = self.osc_plot.plot(pen=pg.mkPen(color='#00f0ff', width=2, style=Qt.SolidLine))
        
        # Shadow effect (simulated by plotting same data with thicker transparent line? cheap glow)
        self.glow_curve = self.osc_plot.plot(pen=pg.mkPen(color='#00f0ff10', width=8))
        
        layout.addWidget(self.osc_plot)
        
        # FFT Spectrum
        self.fft_plot = pg.PlotWidget(title="SPECTRUM")
        self.fft_plot.setLogMode(x=True, y=False)
        self.fft_plot.setYRange(0, 1)
        self.fft_curve = self.fft_plot.plot(pen=pg.mkPen(color='#00a8ff', width=1), fillLevel=0, brush=(0, 168, 255, 50))
        
        layout.addWidget(self.fft_plot)
        
        # Update Timer (30 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(33)

    def update_plots(self):
        buffer = self.engine.get_buffer()
        if buffer is None or len(buffer) == 0:
            return
            
        # Oscilloscope
        self.osc_curve.setData(buffer)
        self.glow_curve.setData(buffer)
        
        # FFT
        # Simple FFT
        fft_data = np.fft.rfft(buffer)
        fft_mag = np.abs(fft_data)
        # Normalize
        fft_mag = fft_mag / (len(buffer) / 2)
        
        # Frequency Axis (Log)
        # Just plotting magnitude array against index
        # To match log scale, we generally pass x values or just set log mode.
        # Log mode x expects x values to be log10 of actual freq? No, pyqtgraph handles log mapping if x is linear freq.
        # Efficient way:
        freqs = np.linspace(20, self.engine.sample_rate / 2, len(fft_mag))
        
        self.fft_curve.setData(freqs, fft_mag)
