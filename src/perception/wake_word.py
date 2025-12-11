"""
Wake Word Detection Module using Porcupine.
Listens for keywords like 'Jarvis' or 'Computer'.
"""
import pvporcupine
import pyaudio
import struct
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv('config/.env')

class WakeWordListener:
    """Listens for wake words."""
    
    def __init__(self, callback):
        self.callback = callback
        self.access_key = os.getenv('PICOVOICE_ACCESS_KEY')
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.is_listening = False
        
        if not self.access_key:
            logger.warning("PICOVOICE_ACCESS_KEY not found. Wake word disabled.")
            return

        try:
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=['jarvis', 'computer']
            )
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            logger.info("✓ Wake Word Listener initialized (Jarvis/Computer)")
        except Exception as e:
            logger.error(f"Wake word init failed: {e}")

    def start(self):
        """Start listening loop."""
        if not self.porcupine:
            return
            
        self.is_listening = True
        logger.info("Listening for wake word...")
        
        while self.is_listening:
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    logger.info("Wake word detected!")
                    if self.callback:
                        self.callback()
                        
            except Exception as e:
                logger.error(f"Wake word loop error: {e}")
                break

    def stop(self):
        """Stop listening."""
        self.is_listening = False
        if self.audio_stream:
            self.audio_stream.close()
        if self.porcupine:
            self.porcupine.delete()
        if self.pa:
            self.pa.terminate()
