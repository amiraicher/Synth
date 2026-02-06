import numpy as np
from abc import ABC, abstractmethod

class Oscillator(ABC):
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.phase = 0.0

    @abstractmethod
    def get_samples(self, num_samples, frequency):
        pass

    def _advance_phase(self, num_samples, frequency):
        # Calculate phase increment per sample
        # frequency (Hz) / sample_rate (Hz) = cycles per sample
        phase_increment = frequency / self.sample_rate
        
        # Create an array of phase steps for the current block
        # np.arange(0, num_samples) creates [0, 1, 2, ... N-1]
        # Multiplying by phase_increment gives relative phase for each sample in block
        time_steps = np.arange(num_samples) * phase_increment
        
        # Add current base phase to all steps
        phases = self.phase + time_steps
        
        # Update self.phase for the next block
        # We start from the phase *after* the last sample in this block
        self.phase += num_samples * phase_increment
        self.phase %= 1.0  # Keep phase in [0.0, 1.0) range for precision
        
        return phases

class SineOsc(Oscillator):
    def get_samples(self, num_samples, frequency):
        phases = self._advance_phase(num_samples, frequency)
        return np.sin(2 * np.pi * phases)

class SquareOsc(Oscillator):
    def get_samples(self, num_samples, frequency):
        phases = self._advance_phase(num_samples, frequency)
        # Apply modulo 1.0 to the phases array locally to wrap the wave
        t = phases % 1.0
        # Square wave: 1.0 if phase < 0.5 else -1.0
        return np.where(t < 0.5, 1.0, -1.0)

class SawOsc(Oscillator):
    def get_samples(self, num_samples, frequency):
        phases = self._advance_phase(num_samples, frequency)
        t = phases % 1.0
        # Saw wave: linearly from -1.0 to 1.0
        return 2.0 * t - 1.0

class TriangleOsc(Oscillator):
    def get_samples(self, num_samples, frequency):
        phases = self._advance_phase(num_samples, frequency)
        t = phases % 1.0
        # Triangle wave logic
        return 2.0 * np.abs(2.0 * t - 1.0) - 1.0
