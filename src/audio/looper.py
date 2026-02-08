import numpy as np
from enum import Enum

class PodState(Enum):
    EMPTY = 0
    RECORDING = 1
    PLAYING = 2
    PAUSED = 3
    STOPPED = 4

class LooperPod:
    def __init__(self, index, sample_rate=44100):
        self.index = index
        self.sample_rate = sample_rate
        self.buffer = None
        self.state = PodState.EMPTY
        self.play_head = 0
        self.is_repeat = True  # True = Loop, False = One-Shot
        
        # Temp buffer for recording
        self.rec_buffer_list = []

    def record(self):
        """
        Force start recording.
        Clears previous data.
        """
        self.state = PodState.RECORDING
        self.rec_buffer_list = []
        self.buffer = None # Clear old buffer
        self.play_head = 0

    def trigger(self):
        """
        Main trigger action (Pad Click).
        Empty -> Recording
        Recording -> Playing
        Playing -> Overdub (Not yet implemented) OR Retrigger? 
        Let's stick to Record -> Play -> Retrigger for now.
        Use Stop for stopping.
        Use Pause for pausing.
        """
        if self.state == PodState.EMPTY:
            self.start_recording()
        elif self.state == PodState.RECORDING:
            self.finish_recording()
        elif self.state == PodState.PLAYING:
            # Retrigger
            self.play_head = 0
        elif self.state == PodState.PAUSED:
            self.resume_playback()
        elif self.state == PodState.STOPPED:
            self.start_playback()

    def start_recording(self):
        self.state = PodState.RECORDING
        self.rec_buffer_list = []
        self.play_head = 0

    def finish_recording(self):
        if self.rec_buffer_list:
            self.buffer = np.concatenate(self.rec_buffer_list)
            self.rec_buffer_list = []
            self.state = PodState.PLAYING
            self.play_head = 0
        else:
            # Nothing recorded
            self.state = PodState.EMPTY

    def start_playback(self):
        if self.buffer is not None:
            self.state = PodState.PLAYING
            self.play_head = 0

    def resume_playback(self):
        if self.buffer is not None:
            self.state = PodState.PLAYING
            # Keep play_head

    def stop(self):
        if self.state != PodState.EMPTY:
            self.state = PodState.STOPPED
            self.play_head = 0
            
    def pause(self):
        if self.state == PodState.PLAYING:
            self.state = PodState.PAUSED
        elif self.state == PodState.PAUSED:
            self.resume_playback()

    def clear(self):
        self.buffer = None
        self.state = PodState.EMPTY
        self.play_head = 0
        self.rec_buffer_list = []

    def set_repeat(self, enabled):
        self.is_repeat = enabled

    def process(self, input_chunk, num_samples):
        output = np.zeros(num_samples)

        if self.state == PodState.RECORDING:
            # Record input
            # Copy to avoid reference issues
            self.rec_buffer_list.append(np.copy(input_chunk))
            # Passthrough? Usually loopers play thru or mute. 
            # Let's simple pass thru happens at mixer level if input is monitored.
            # Here we just return 0.
            
        elif self.state == PodState.PLAYING and self.buffer is not None:
            buf_len = len(self.buffer)
            if buf_len > 0:
                pos = self.play_head
                
                # How much can we read?
                available = buf_len - pos
                
                if available >= num_samples:
                    chunk = self.buffer[pos:pos+num_samples]
                    output += chunk
                    self.play_head += num_samples
                else:
                    # End of buffer reached
                    # Part 1
                    part1 = self.buffer[pos:]
                    output[:available] += part1
                    
                    if self.is_repeat:
                        # Wrap around
                        remaining = num_samples - available
                        # Handle case where remaining > buf_len (very short loop)
                        # For simplicity, assume loop > block size (otherwise utilize mod)
                        # But to be safe:
                        read_ptr = 0
                        while remaining > 0:
                            can_take = min(remaining, buf_len)
                            output[available:available+can_take] += self.buffer[:can_take]
                            available += can_take
                            remaining -= can_take
                            read_ptr = can_take % buf_len # Update pointer if we consumed exactly logic...
                            # Actually simplified:
                            # play_head should wrap.
                        
                        self.play_head = (pos + num_samples) % buf_len
                    else:
                        # One shot: stop after part1
                        self.play_head = 0
                        self.state = PodState.STOPPED

        return output


class Looper:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.pods = [LooperPod(i, sample_rate) for i in range(10)]

    def process(self, input_audio, num_samples):
        # Mix all pods
        mixed_output = np.zeros(num_samples)
        
        for pod in self.pods:
            mixed_output += pod.process(input_audio, num_samples)
            
        return mixed_output

    def stop_all(self):
        for pod in self.pods:
            pod.stop()
            
    def get_pod_state(self, index):
        if 0 <= index < len(self.pods):
            return self.pods[index].state
        return PodState.EMPTY
