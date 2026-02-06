class GlobalClock:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.bpm = 120.0
        self.beats_per_bar = 4
        self.current_time_samples = 0
        
    def set_bpm(self, bpm):
        self.bpm = max(1.0, bpm)
        
    def samples_per_beat(self):
        # 60 seconds / BPM = seconds per beat
        return (60.0 / self.bpm) * self.sample_rate
        
    def samples_per_bar(self):
        return self.samples_per_beat() * self.beats_per_bar

    def get_time_info(self):
        spb = self.samples_per_beat()
        total_beats = self.current_time_samples / spb
        
        bar = int(total_beats / self.beats_per_bar)
        beat = int(total_beats % self.beats_per_bar)
        fraction = total_beats - int(total_beats)
        
        return bar, beat, fraction
