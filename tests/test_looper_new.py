import unittest
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio.looper import Looper, PodState

class TestLooperPod(unittest.TestCase):
    def setUp(self):
        self.looper = Looper(sample_rate=44100)
        self.pod = self.looper.pods[0]

    def test_initial_state(self):
        self.assertEqual(self.pod.state, PodState.EMPTY)
        self.assertEqual(self.pod.play_head, 0)
        self.assertIsNone(self.pod.buffer)

    def test_recording(self):
        # 1. Trigger -> Recording
        self.pod.trigger()
        self.assertEqual(self.pod.state, PodState.RECORDING)
        
        # 2. Process Audio (Record)
        input_chunk = np.ones(100) # 1.0s
        self.pod.process(input_chunk, 100)
        self.assertEqual(len(self.pod.rec_buffer_list), 1)
        
        # 3. Trigger -> Finish Rec -> Playing
        self.pod.trigger()
        self.assertEqual(self.pod.state, PodState.PLAYING)
        self.assertIsNotNone(self.pod.buffer)
        self.assertEqual(len(self.pod.buffer), 100)
        self.assertEqual(self.pod.play_head, 0) # Just started playing

    def test_playback_looping(self):
        # Setup recorded buffer
        self.pod.buffer = np.arange(100, dtype=float) # 0..99
        self.pod.state = PodState.PLAYING
        self.pod.is_repeat = True
        
        # Process 50 samples
        out = self.pod.process(np.zeros(50), 50)
        self.assertTrue(np.allclose(out, np.arange(50)))
        self.assertEqual(self.pod.play_head, 50)
        
        # Process 50 samples (Reach end)
        out = self.pod.process(np.zeros(50), 50)
        self.assertTrue(np.allclose(out, np.arange(50, 100)))
        self.assertEqual(self.pod.play_head, 0) # Wrapped

        # Process next 50 (Loop start)
        out = self.pod.process(np.zeros(50), 50)
        self.assertTrue(np.allclose(out, np.arange(50)))
        self.assertEqual(self.pod.play_head, 50)

    def test_playback_oneshot(self):
        self.pod.buffer = np.arange(100, dtype=float)
        self.pod.state = PodState.PLAYING
        self.pod.is_repeat = False
        
        # 0-50
        self.pod.process(np.zeros(50), 50)
        
        # 50-100 (End)
        out = self.pod.process(np.zeros(50), 50)
        self.assertTrue(np.allclose(out, np.arange(50, 100)))
        self.assertEqual(self.pod.state, PodState.STOPPED) # Stopped after playing
        self.assertEqual(self.pod.play_head, 0) # Reset

    def test_pause(self):
        self.pod.buffer = np.zeros(100)
        self.pod.state = PodState.PLAYING
        self.pod.play_head = 50
        
        self.pod.pause()
        self.assertEqual(self.pod.state, PodState.PAUSED)
        self.assertEqual(self.pod.play_head, 50)
        
        # Process should return silence and not move head
        out = self.pod.process(np.zeros(10), 10)
        self.assertTrue(np.allclose(out, np.zeros(10)))
        self.assertEqual(self.pod.play_head, 50)
        
        # Trigger -> Resume
        self.pod.trigger()
        self.assertEqual(self.pod.state, PodState.PLAYING)
        self.assertEqual(self.pod.play_head, 50)

    def test_stop(self):
        self.pod.buffer = np.zeros(100)
        self.pod.state = PodState.PLAYING
        self.pod.play_head = 50
        
        self.pod.stop()
        self.assertEqual(self.pod.state, PodState.STOPPED)
        self.assertEqual(self.pod.play_head, 0)

if __name__ == '__main__':
    unittest.main()
