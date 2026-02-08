import sounddevice as sd
import numpy as np
from .voice_manager import VoiceManager
from .looper import Looper
import threading
import logging

class AudioEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AudioEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self, sample_rate=44100, block_size=1024):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        
        self.sample_rate = sample_rate
        self.block_size = block_size
        
        self.voice_manager = VoiceManager(sample_rate)
        self.looper = Looper(sample_rate)
        
        # Audio Stream
        self.stream = None
        self.is_running = False
        
        # Visualization Buffer
        self.current_buffer = np.zeros(block_size)
        self.buffer_lock = threading.Lock()
        
        # Master Volume
        self.volume = 0.5

    def start(self):
        if self.is_running:
            return

        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=1,
                callback=self._callback,
                latency='low' # Try low latency
            )
            self.stream.start()
            self.is_running = True
            logging.info(f"Audio Engine Started: Sample Rate={self.sample_rate}, Block Size={self.block_size}, Latency=low")
        except Exception as e:
            logging.error(f"Error starting audio stream: {e}", exc_info=True)
            print(f"Error starting audio stream: {e}")

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.is_running = False
            logging.info("Audio Engine Stopped")
            print("Audio Engine Stopped")

    def _callback(self, outdata, frames, time, status):
        if status:
            logging.warning(f"Stream Status: {status}")
            print(f"Stream Status: {status}")
            
        try:
            # 1. Get audio from Synth Voices
            voice_block = self.voice_manager.process(frames)
            
            # 2. Process Looper (Record Input: voice_block)
            # Returns: Looper Playback Output
            looper_block = self.looper.process(voice_block, frames)
            
            # 3. Mix Synth + Looper
            mixed_block = voice_block + looper_block
            
            # Master Volume
            mixed_block *= self.volume
            
            # Update Visualization Buffer (Copy safely)
            with self.buffer_lock:
                # If buffer sizes act weird, just take what fits or pad
                if len(mixed_block) == len(self.current_buffer):
                    self.current_buffer[:] = mixed_block
                else:
                     # Should match frames == block_size generally
                     pass
            
            # Write to output (reshape for sounddevice channels)
            outdata[:] = mixed_block.reshape(-1, 1)
        except Exception as e:
            logging.error(f"Error in Audio Callback: {e}", exc_info=True)
            # Silence output on error to avoid noise
            outdata.fill(0)

    # Proxy methods to VoiceManager
    def note_on(self, freq):
        self.voice_manager.note_on(freq)

    def note_off(self, freq):
        self.voice_manager.note_off(freq)

    def set_synth_param(self, name, value):
        self.voice_manager.set_param(name, value)
        
    def get_buffer(self):
        with self.buffer_lock:
            return np.copy(self.current_buffer)

    # Looper Controls
    def looper_trigger(self, pod_index):
        if self.looper:
            # Bounds check managed by looper or panel, but safe to check here
            if 0 <= pod_index < len(self.looper.pods):
                self.looper.pods[pod_index].trigger()
                logging.info(f"Looper Pod {pod_index} Triggered. New State: {self.looper.pods[pod_index].state}")

    def looper_stop(self, pod_index):
        if self.looper:
            if 0 <= pod_index < len(self.looper.pods):
                self.looper.pods[pod_index].stop()
                logging.info(f"Looper Pod {pod_index} Stopped.")

    def looper_record(self, pod_index):
        if self.looper:
            if 0 <= pod_index < len(self.looper.pods):
                self.looper.pods[pod_index].record()
                logging.info(f"Looper Pod {pod_index} Record (Forced).")

    def looper_pause(self, pod_index):
        if self.looper:
            if 0 <= pod_index < len(self.looper.pods):
                self.looper.pods[pod_index].pause()
                logging.info(f"Looper Pod {pod_index} toggle Pause.")

    def looper_set_repeat(self, pod_index, enabled):
        if self.looper:
            if 0 <= pod_index < len(self.looper.pods):
                self.looper.pods[pod_index].set_repeat(enabled)
                logging.info(f"Looper Pod {pod_index} Repeat: {enabled}")

    def looper_stop_all(self):
        if self.looper:
            self.looper.stop_all()
            logging.info("Looper Stop All")

    def looper_get_state(self, pod_index):
        if self.looper:
             if 0 <= pod_index < len(self.looper.pods):
                 return self.looper.pods[pod_index].state
        return None
