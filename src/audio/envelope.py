import numpy as np
from enum import Enum

class EnvelopeState(Enum):
    IDLE = 0
    ATTACK = 1
    DECAY = 2
    SUSTAIN = 3
    RELEASE = 4

class ADSREnvelope:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.active = False
        self.state = EnvelopeState.IDLE
        self.current_level = 0.0
        
        # Parameters (default values)
        self.attack_time = 0.01  # seconds
        self.decay_time = 0.1    # seconds
        self.sustain_level = 0.7 # 0.0 to 1.0
        self.release_time = 0.3  # seconds
        
        # Increments per sample (calculated on trigger/update)
        self.attack_rate = 0.0
        self.decay_rate = 0.0
        self.release_rate = 0.0

    def set_params(self, attack, decay, sustain, release):
        self.attack_time = max(0.001, attack)
        self.decay_time = max(0.001, decay)
        self.sustain_level = np.clip(sustain, 0.0, 1.0)
        self.release_time = max(0.001, release)

    def trigger(self):
        self.state = EnvelopeState.ATTACK
        self.active = True
        # Calculate rates
        self.attack_rate = 1.0 / (self.attack_time * self.sample_rate)
        
        # Decay rate: drop from 1.0 to sustain_level
        self.decay_rate = (1.0 - self.sustain_level) / (self.decay_time * self.sample_rate)
        
        # Release rate: Standard definition is drop from 1.0 to 0.0 in release_time
        # This ensures constant slope regardless of starting level
        self.release_rate = 1.0 / (self.release_time * self.sample_rate)

    def release(self):
        self.state = EnvelopeState.RELEASE
        # Recalculate release rate from current level to 0
        # For simplicity and standard ADSR behavior, we usually decay from Sustain level 
        # or current level. Here we just set state to Release.
        # Ideally, release rate is constant slope based on release_time
        pass

    def get_amplitude(self, num_samples):
        output = np.zeros(num_samples)
        
        if self.state == EnvelopeState.IDLE:
            return output

        # Process sample by sample (vectorization is harder for state machines, 
        # but for Python performance we can try to process in chunks if state doesn't change.
        # For simplicity in this first pass, we'll do a simple per-sample loop 
        # or small block logic if needed. 
        # OPTIMIZATION: Pure Python loop is slow. 
        # Let's try a simplified block approach assuming state doesn't change rapidly within a block often.
        
        # However, precise timing requires per-sample updates. 
        # Let's implement a generator-like process or a vectorized approach for segments.
        
        start_idx = 0
        while start_idx < num_samples:
            if self.state == EnvelopeState.IDLE:
                output[start_idx:] = 0.0
                self.active = False
                break
                
            elif self.state == EnvelopeState.ATTACK:
                # Target: 1.0
                # Steps needed to reach 1.0 from current
                needed = (1.0 - self.current_level) / self.attack_rate
                steps = int(needed) + 1
                available = num_samples - start_idx
                
                count = min(steps, available)
                # Create ramp
                end_level = self.current_level + self.attack_rate * count
                output[start_idx:start_idx+count] = np.linspace(self.current_level, end_level, count, endpoint=False)
                
                self.current_level = end_level
                start_idx += count
                
                if count == steps or self.current_level >= 1.0:
                    self.current_level = 1.0
                    self.state = EnvelopeState.DECAY

            elif self.state == EnvelopeState.DECAY:
                # Target: sustain_level
                needed = (self.current_level - self.sustain_level) / self.decay_rate
                if needed <= 0: needed = 0 # Should not happen if logic is correct
                steps = int(needed) + 1
                available = num_samples - start_idx
                
                count = min(steps, available)
                end_level = self.current_level - self.decay_rate * count
                output[start_idx:start_idx+count] = np.linspace(self.current_level, end_level, count, endpoint=False)
                
                self.current_level = end_level
                start_idx += count
                
                if count == steps or self.current_level <= self.sustain_level:
                    self.current_level = self.sustain_level
                    self.state = EnvelopeState.SUSTAIN

            elif self.state == EnvelopeState.SUSTAIN:
                # Hold level
                # State only changes on release() call (external)
                # But we just fill the rest of the buffer
                count = num_samples - start_idx
                output[start_idx:] = self.current_level
                start_idx += count
                
            elif self.state == EnvelopeState.RELEASE:
                # Target: 0.0
                needed = self.current_level / self.release_rate
                steps = int(needed) + 1
                available = num_samples - start_idx
                
                count = min(steps, available)
                end_level = self.current_level - self.release_rate * count
                output[start_idx:start_idx+count] = np.linspace(self.current_level, end_level, count, endpoint=False)
                
                self.current_level = end_level
                start_idx += count
                
                if count == steps or self.current_level <= 0.0:
                    self.current_level = 0.0
                    self.state = EnvelopeState.IDLE
                    self.active = False
        
        return output
