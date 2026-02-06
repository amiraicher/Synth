
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock sounddevice BEFORE importing AudioEngine
from unittest.mock import MagicMock
sys.modules['sounddevice'] = MagicMock()

from ui.keyboard import VirtualKeyboard
from audio.engine import AudioEngine

# Ensure QApplication exists
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

class TestKeyboardWave(unittest.TestCase):
    def setUp(self):
        # Mock sounddevice before initializing AudioEngine
        self.sd_patcher = patch('sounddevice.OutputStream')
        self.mock_sd = self.sd_patcher.start()
        
        # Initialize Engine with a standard sample rate
        self.engine = AudioEngine(sample_rate=44100, block_size=1024)
        # Ensure pure state
        self.engine.voice_manager.active_voices.clear()
        
        self.keyboard = VirtualKeyboard()
        
        # Connect signals exactly as in main_window.py
        self.keyboard.note_on_signal.connect(self.engine.note_on)
        self.keyboard.note_off_signal.connect(self.engine.note_off)

    def tearDown(self):
        self.sd_patcher.stop()

    def test_key_press_generates_correct_frequency(self):
        # A = 440Hz
        # Qt.Key_H maps to A (440Hz) in VirtualKeyboard
        
        # Simulate Key Press
        self.keyboard.handle_key_press(Qt.Key_H)
        
        # Verify Engine received note_on
        # Check active voices in VoiceManager
        self.assertEqual(len(self.engine.voice_manager.active_voices), 1, "One voice should be active")
        
        # Get frequency
        active_freqs = list(self.engine.voice_manager.active_voices.keys())
        self.assertAlmostEqual(active_freqs[0], 440.0, delta=0.1, msg="Frequency should be 440Hz")
        
        # Generate Audio
        # Process enough samples to detect frequency
        num_samples = 4096 
        audio_data = self.engine.voice_manager.process(num_samples)
        
        # Check if silence (should NOT be silence)
        self.assertFalse(np.allclose(audio_data, 0), "Audio data should not be silence")
        
        # Verify Frequency via FFT
        # Hanning window to reduce leakage
        window = np.hanning(num_samples)
        fft_data = np.fft.rfft(audio_data * window)
        freqs = np.fft.rfftfreq(num_samples, 1/44100)
        
        # Find peak frequency
        peak_idx = np.argmax(np.abs(fft_data))
        peak_freq = freqs[peak_idx]
        
        print(f"Detected Peak Frequency: {peak_freq} Hz")
        self.assertAlmostEqual(peak_freq, 440.0, delta=20.0, msg=f"FFT Peak should be near 440Hz, got {peak_freq}")

    def test_key_release_stops_sound(self):
        print("Testing key release...")
        # Press
        self.keyboard.handle_key_press(Qt.Key_H)
        self.assertEqual(len(self.engine.voice_manager.active_voices), 1)
        
        # Release
        self.keyboard.handle_key_release(Qt.Key_H)
        
        # Active voices maps should clear (eventually, or immediately in current logic?)
        # Looking at voice_manager.py: del self.active_voices[frequency] happens in note_off
        self.assertEqual(len(self.engine.voice_manager.active_voices), 0, "Voice should be removed from active map on release")
        print("Key release test passed.")

if __name__ == '__main__':
    unittest.main()

