import numpy as np
from enum import Enum
from src.utils.clock import GlobalClock

class LoopState(Enum):
    STOPPED = 0
    RECORDING = 1
    PLAYING = 2

class LooperTrack:
    def __init__(self, name="Track", sample_rate=44100):
        self.name = name
        self.buffer = None
        self.state = LoopState.STOPPED
        self.is_muted = False
        self.volume = 1.0
        
        # Playback/Recording heads
        self.head_position = 0
        
        # Temp buffer for recording
        self.rec_buffer_list = []

class Looper:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.clock = GlobalClock(sample_rate)
        self.tracks = [LooperTrack(f"Track {i+1}", sample_rate) for i in range(4)]
        self.is_playing = False
        
        # Transport
        self.current_loop_length_samples = 0
        self.master_head = 0

    def toggle_record(self, track_index):
        track = self.tracks[track_index]
        if track.state == LoopState.RECORDING:
            # Stop Recording -> PLAYING
            track.state = LoopState.PLAYING
            # Finalize buffer
            if track.rec_buffer_list:
                full_rec = np.concatenate(track.rec_buffer_list)
                track.buffer = full_rec
                # For simplicity, assume loop length is defined by first track or global
                if self.current_loop_length_samples == 0:
                    self.current_loop_length_samples = len(track.buffer)
                    
                track.rec_buffer_list = []
                # Normalize length? Or logic to handle differing lengths?
                # Simplest: Fixed loop length or master length
        else:
            # Start Recording
            track.state = LoopState.RECORDING
            track.rec_buffer_list = []
            # If logic requires defined length, we might wrap
            # If free running, we record until toggle
            
    def process(self, input_audio, num_samples):
        # Input audio is what we are recording (e.g. from Synth)
        output = np.zeros(num_samples)
        
        if not self.is_playing:
            # If not playing global transport, we might still record?
            # Let's simple: Transport Play must be active to move heads
            pass

        # If master transport playing
        if self.is_playing:
            # Advance master
            # Wrap logic
            limit = self.current_loop_length_samples if self.current_loop_length_samples > 0 else 999999999
            
            # Simple per-sample or block logic
            # Block logic:
            
            # For each track
            for track in self.tracks:
                if track.is_muted:
                    continue
                    
                if track.state == LoopState.RECORDING:
                    # Append input to record buffer
                    # We need to copy input_audio
                    track.rec_buffer_list.append(np.copy(input_audio))
                    
                elif track.state == LoopState.PLAYING and track.buffer is not None:
                    # Add to output
                    # Complex wrapping logic if block crosses loop boundary
                    # Simplified: Assume loop buffer is long enough or handle wrap
                    buf_len = len(track.buffer)
                    if buf_len == 0: continue
                    
                    # Read pointer
                    pos = self.master_head % buf_len
                    
                    # If block fits remaining
                    available = buf_len - pos
                    
                    if available >= num_samples:
                        chunk = track.buffer[pos:pos+num_samples]
                        output += chunk * track.volume
                    else:
                        # Wrap around
                        part1 = track.buffer[pos:]
                        part2 = track.buffer[0:num_samples-available]
                        output[:available] += part1 * track.volume
                        output[available:] += part2 * track.volume
            
            self.master_head += num_samples
            
        return output

    def start_transport(self):
        self.is_playing = True
    
    def stop_transport(self):
        self.is_playing = False
        self.master_head = 0
