import numpy as np
from scipy import signal

class Filter:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.cutoff = 1000.0
        self.resonance = 0.7  # Q factor
        self.filter_type = 'lowpass'
        self.zi = None # Filter state
        self._update_coefficients()

    def set_params(self, cutoff, resonance):
        self.cutoff = np.clip(cutoff, 20.0, self.sample_rate / 2.0 - 100)
        self.resonance = max(0.1, resonance)
        self._update_coefficients()

    def _update_coefficients(self):
        # Design a 2nd order Butterworth filter (12dB/octave)
        # Using output='sos' (Second-Order Sections) is generally more stable usually
        # But lfilter_zi with ba format is easier for state management in simple real-time
        # Let's try 'ba' first.
        nyquist = self.sample_rate / 2.0
        norm_cutoff = self.cutoff / nyquist
        
        # Calculate b, a coefficients
        # Warning: iirfilter resonance is not directly 'Q' in this function easily.
        # better to use iirfilter or specialized functions.
        # For a standard synth filter, we might want a resonant Lowpass.
        # We can use 'bessel', 'butter', etc. with iirfilter.
        
        # Let's use a standard biquad calculation if we want precise control over Q (Resonance)
        # Or use scipy's design. 
        # For simplicity, we'll use butterworth. High resonance in digital filters 
        # via standard butterworth Q is minimal. 
        
        # Alternative: Manual Biquad implementation for proper "Resonance" control
        # This is often better for synths.
        pass 
        # Actually, let's stick to scipy for now as requested.
        # We will map 'resonance' to something available or just ignore Q for butterworth
        # (Butterworth has fixed Q=0.707).
        # PROPOSED CHECK: If user wants "Resonance", we usually need a Chebyshev or custom Biquad.
        
        # Let's use `scipy.signal.iirpeak` or similar if we want resonance? 
        # No, let's implement a simple Biquad manually for best synth sound.
        # BUT requirements said "Integration of SciPy.signal IIR filters".
        # So we MUST use scipy.
        
        # Resonant Lowpass in scipy:
        # We can use Chebyshev Type I (cheby1) which allows ripple (resonance kind of).
        
        if self.resonance > 1.0:
            # Emulate resonance with ripple
            # rp is decibels of ripple
             self.b, self.a = signal.cheby1(N=2, rp=self.resonance, Wn=norm_cutoff, btype=self.filter_type, output='ba')
        else:
             self.b, self.a = signal.butter(N=2, Wn=norm_cutoff, btype=self.filter_type, output='ba')
             
        if self.zi is None:
             self.zi = signal.lfilter_zi(self.b, self.a)

    def process(self, data):
        if self.zi is None:
            self.zi = signal.lfilter_zi(self.b, self.a) * data[0]
            
        # For block processing with state retention
        # We must re-calculate zi if coefficients changed, but keeping continuity is hard if coeffs change.
        # Resetting zi on coeff change can cause pops.
        # For this logic, we will just apply lfilter.
        # Note: Scipy lfilter state management can be tricky with changing coeffs.
        
        out_data, self.zi = signal.lfilter(self.b, self.a, data, zi=self.zi)
        return out_data
