from .voice import Voice
import numpy as np

class VoiceManager:
    def __init__(self, sample_rate=44100, max_voices=8):
        self.sample_rate = sample_rate
        self.voices = [Voice(sample_rate) for _ in range(max_voices)]
        self.active_voices = {} # frequency -> voice_index
        
        # Global Synth Params (Should be applied to all voices)
        self.params = {
            'osc_type': 'saw',
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.7,
            'release': 0.3,
            'cutoff': 2000.0,
            'resonance': 0.7
        }

    def set_param(self, name, value):
        self.params[name] = value
        # Update all voices live
        # OPTIMIZATION: Only update active voices? No, Idle voices need correct params for next trigger
        for voice in self.voices:
            if name == 'osc_type':
                voice.set_osc_type(value)
            elif name == 'attack':
                voice.envelope.set_params(value, self.params['decay'], self.params['sustain'], self.params['release'])
            elif name == 'decay':
                voice.envelope.set_params(self.params['attack'], value, self.params['sustain'], self.params['release'])
            elif name == 'sustain':
                voice.envelope.set_params(self.params['attack'], self.params['decay'], value, self.params['release'])
            elif name == 'release':
                voice.envelope.set_params(self.params['attack'], self.params['decay'], self.params['sustain'], value)
            elif name == 'cutoff':
                voice.filter.set_params(value, self.params['resonance'])
            elif name == 'resonance':
                voice.filter.set_params(self.params['cutoff'], value)

    def note_on(self, frequency):
        # Check if note already playing
        if frequency in self.active_voices:
            idx = self.active_voices[frequency]
            self.voices[idx].note_on(frequency) # Retrigger
            return

        # Find free voice
        for idx, voice in enumerate(self.voices):
            if not voice.is_active():
                self.active_voices[frequency] = idx
                
                # Ensure params are fresh (though we update all on param change)
                # But filter state resets? Maybe better not to reset filter to avoid pops? 
                # Voice logic keeps filter state persistence.
                
                voice.note_on(frequency)
                return
        
        # No free voice: Voice stealing (steal oldest? or just ignore)
        # Simple implementation: Ignore
        print("Max polyphony reached!")

    def note_off(self, frequency):
        if frequency in self.active_voices:
            idx = self.active_voices[frequency]
            self.voices[idx].note_off()
            # Don't remove from active_voices yet, wait for envelope to finish
            # We cleanup in process loop
            del self.active_voices[frequency]

    def process(self, num_samples):
        output = np.zeros(num_samples)
        
        # Mix all voices
        # We iterate over all voices because some might be releasing even if not in active_voices map
        for voice in self.voices:
            if voice.is_active():
                output += voice.process(num_samples)
        
        # Soft Clipping / Limiting to prevent massive distortion
        np.clip(output, -2.0, 2.0, out=output)
        output = np.tanh(output) # Soft clip
        
        return output
