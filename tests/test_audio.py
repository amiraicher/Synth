import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio.oscillator import SineOsc, SquareOsc
from audio.envelope import ADSREnvelope, EnvelopeState
from audio.voice_manager import VoiceManager

def test_oscillator_output_range():
    osc = SineOsc(44100)
    samples = osc.get_samples(1024, 440.0)
    assert np.max(samples) <= 1.0001
    assert np.min(samples) >= -1.0001
    assert samples.shape == (1024,)

def test_envelope_states():
    mgr = ADSREnvelope(44100)
    mgr.set_params(0.1, 0.1, 0.5, 0.1) # 100ms attack
    
    # Trigger
    mgr.trigger()
    assert mgr.state == EnvelopeState.ATTACK
    
    # Advance time (50ms) -> Still Attack
    out = mgr.get_amplitude(int(44100 * 0.05))
    assert mgr.state == EnvelopeState.ATTACK
    assert 0.0 < mgr.current_level < 1.0
    
    # Advance time (100ms more) -> Should be in Decay or Sustain
    # Total 150ms > 100ms attack -> Decay
    out = mgr.get_amplitude(int(44100 * 0.1))
    assert mgr.state in [EnvelopeState.DECAY, EnvelopeState.SUSTAIN]

def test_polyphony_limit():
    vm = VoiceManager(44100, max_voices=2)
    vm.note_on(440)
    vm.note_on(880)
    
    # 2 voices active
    assert len(vm.active_voices) == 2
    
    # 3rd voice should not crash/force add
    vm.note_on(220)
    # Simple implementation was to ignore, so size still 2
    assert len(vm.active_voices) == 2
