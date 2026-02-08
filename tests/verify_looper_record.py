import sys
import os

# Create a dummy dependency for sounddevice if it's not installed or we can't run audio
# But since we are just testing logic, maybe we can mock it or just import LooperPod directly if it doesn't depend on sounddevice at import time.
# engine.py imports sounddevice. looper.py imports numpy and enum. looper.py seems safe.

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from audio.looper import LooperPod, PodState
import numpy as np

def test_looper_record():
    print("Testing LooperPod.record()...")
    pod = LooperPod(0)
    
    # Initial State
    assert pod.state == PodState.EMPTY
    print("Initial state: EMPTY - OK")
    
    # Start Recording via trigger (standard way)
    pod.trigger()
    assert pod.state == PodState.RECORDING
    print("Trigger -> RECORDING - OK")
    
    # Simulate recording some data
    pod.process(np.zeros(1024), 1024)
    assert len(pod.rec_buffer_list) == 1
    
    # Stop
    pod.stop()
    assert pod.state == PodState.STOPPED
    print("Stop -> STOPPED - OK")
    
    # Now use the new RECORD method
    pod.record()
    assert pod.state == PodState.RECORDING
    assert pod.rec_buffer_list == [] # Should be cleared
    assert pod.buffer is None # Should be cleared
    print("Record() -> RECORDING (Forced & Cleared) - OK")
    
    print("All tests passed!")

if __name__ == "__main__":
    test_looper_record()
