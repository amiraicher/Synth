from .oscillator import SineOsc, SquareOsc, SawOsc, TriangleOsc
from .envelope import ADSREnvelope
from .filter import Filter
import numpy as np

class Voice:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.active = False
        self.note = None
        
        # Components
        # Initialize one of each osc to switch quickly? 
        # Or just instantiate active one. Let's keep instances.
        self.oscillators = {
            'sine': SineOsc(sample_rate),
            'square': SquareOsc(sample_rate),
            'saw': SawOsc(sample_rate),
            'triangle': TriangleOsc(sample_rate)
        }
        self.current_osc = self.oscillators['saw']
        self.osc_type = 'saw'
        
        self.envelope = ADSREnvelope(sample_rate)
        self.filter = Filter(sample_rate)
        
    def set_osc_type(self, osc_type):
        if osc_type in self.oscillators:
            self.current_osc = self.oscillators[osc_type]
            # Sync phase? Maybe not needed for simple synth.
            self.osc_type = osc_type

    def note_on(self, frequency):
        self.note = frequency
        self.active = True
        self.envelope.trigger()
        
    def note_off(self):
        self.envelope.release()
        
    def is_active(self):
        return self.envelope.active
        
    def process(self, num_samples):
        if not self.active:
            return np.zeros(num_samples)
            
        # Get Oscillator block
        raw_signal = self.current_osc.get_samples(num_samples, self.note)
        
        # Apply Filter
        filtered_signal = self.filter.process(raw_signal)
        
        # Get Envelope block
        amp_env = self.envelope.get_amplitude(num_samples)
        
        # Apply Envelope controls active state
        if not self.envelope.active:
            self.active = False
            
        return filtered_signal * amp_env
