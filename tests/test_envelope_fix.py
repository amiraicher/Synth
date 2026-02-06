import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio.envelope import ADSREnvelope, EnvelopeState

def test_envelope_zero_sustain_release_crash():
    """
    Test that releasing the envelope with Sustain=0.0 does not cause DivisionByZero or OverflowError.
    Previously, release_rate was calculated using sustain_level in the numerator.
    If sustain was 0, release_rate was 0.
    Releasing while current_level > 0 caused needed_steps = current / 0 = Inf -> OverflowError.
    """
    env = ADSREnvelope(44100)
    # Set Start Parameters: Attack 0.1, Decay 0.1, Sustain 0.0, Release 0.1
    env.set_params(0.1, 0.1, 0.0, 0.1)
    
    # Trigger (Enter Attack)
    env.trigger()
    
    # Process some samples to increase level > 0
    # Attack rate = 1/(0.1*44100)
    # Process 0.05s -> level should be approx 0.5
    env.get_amplitude(int(44100 * 0.05))
    
    assert env.current_level > 0.0
    assert env.state == EnvelopeState.ATTACK
    
    # Release now!
    env.release()
    assert env.state == EnvelopeState.RELEASE
    
    # Process release phase - this caused the crash
    try:
        env.get_amplitude(100)
    except OverflowError:
        pytest.fail("OverflowError during envelope release with zero sustain!")
    except ZeroDivisionError:
        pytest.fail("ZeroDivisionError during envelope release with zero sustain!")
    
    print("Test Passed: No crash during release phase.")
