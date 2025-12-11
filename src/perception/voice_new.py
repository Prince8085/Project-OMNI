"""
Advanced Voice Module using Edge-TTS (Neural) and Pygame.
Provides high-quality, realistic voice output.
"""
import asyncio
import edge_tts
import pygame
import os
import tempfile
import threading
import logging

logger = logging.getLogger(__name__)

class AdvancedVoiceModule:
    """Voice module using Edge-TTS for neural speech."""
    
    def __init__(self):
        self.voice = "en-IN-NeerjaNeural" # Indian English (good for Hindlish)
        # self.voice = "en-US-ChristopherNeural" # Alternative male voice
        self.rate = "+0%"
        self.volume = "+0%"
        self.pitch = "+0Hz"
        
        # Init audio
        try:
            pygame.mixer.init()
            logger.info("✓ Audio mixer initialized")
        except Exception as e:
            logger.error(f"Audio init failed: {e}")
            
    async def _generate_audio(self, text: str, output_file: str):
        """Generate audio file from text."""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume, pitch=self.pitch)
        await communicate.save(output_file)
        
    def speak(self, text: str):
        """Speak text using neural voice (blocking or threaded)."""
        if not text:
            return
            
        def _speak_thread():
            try:
                # Create temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    temp_filename = fp.name
                
                # Generate audio with new loop for thread safety
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._generate_audio(text, temp_filename))
                loop.close()
                
                # Play audio
                pygame.mixer.music.load(temp_filename)
                pygame.mixer.music.play()
                
                # Wait for playback
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
                # Cleanup
                pygame.mixer.music.unload()
                try:
                    os.remove(temp_filename)
                except PermissionError:
                    pass # File might be locked briefly
                
            except Exception as e:
                logger.error(f"Speech error: {e}")
        
        # Run in thread to not block GUI
        threading.Thread(target=_speak_thread, daemon=True).start()

    def list_voices(self):
        """List available voices (async wrapper)."""
        async def _get_voices():
            voices = await edge_tts.list_voices()
            return voices
        return asyncio.run(_get_voices())

if __name__ == "__main__":
    # Test
    v = AdvancedVoiceModule()
    print("Speaking...")
    v.speak("Hello sir, I am OMNI. This is my new neural voice.")
    import time
    time.sleep(5)
