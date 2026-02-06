import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio.looper import Looper, LoopState

def test_looper_recording():
    looper = Looper(44100)
    looper.start_transport()
    
    # Start Recording Track 0
    looper.toggle_record(0)
    assert looper.tracks[0].state == LoopState.RECORDING
    
    # Process audio (100 samples of 1.0)
    input_audio = np.ones(100)
    looper.process(input_audio, 100)
    
    # Check if recorded
    assert len(looper.tracks[0].rec_buffer_list) == 1
    assert np.array_equal(looper.tracks[0].rec_buffer_list[0], input_audio)
    
    # Stop Recording
    looper.toggle_record(0)
    assert looper.tracks[0].state == LoopState.PLAYING
    assert looper.tracks[0].buffer is not None
    assert len(looper.tracks[0].buffer) == 100

def test_looper_playback():
    looper = Looper(44100)
    # Pre-load track 0 with data
    track0 = looper.tracks[0]
    track0.buffer = np.full(100, 0.5) # 100 samples of 0.5
    track0.state = LoopState.PLAYING
    
    looper.current_loop_length_samples = 100
    looper.start_transport()
    
    # Process 50 samples
    dummy_input = np.zeros(50)
    output = looper.process(dummy_input, 50)
    
    assert np.allclose(output, 0.5)
    assert looper.master_head == 50
    
    # Process next 50 (should finish loop)
    output2 = looper.process(dummy_input, 50)
    assert np.allclose(output2, 0.5)
    assert looper.master_head == 100
    
    # Process next 50 (loop wrapped)
    output3 = looper.process(dummy_input, 50)
    assert np.allclose(output3, 0.5)
