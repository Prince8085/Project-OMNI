"""
Voice module for Project OMNI - Phase 4.
Speech-to-text and text-to-speech capabilities.
"""

import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


class VoiceModule:
    """Voice input/output capabilities."""
    
    def __init__(self, stt_provider: str = "whisper", tts_provider: str = "pyttsx3"):
        """
        Initialize voice module.
        
        Args:
            stt_provider: Speech-to-text provider ('whisper', 'google')
            tts_provider: Text-to-speech provider ('pyttsx3', 'elevenlabs')
        """
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider
        self.tts_engine = None
        
        self._init_tts()
    
    def _init_tts(self):
        """Initialize text-to-speech engine."""
        try:
            if self.tts_provider == "pyttsx3":
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                
                # Configure voice properties
                self.tts_engine.setProperty('rate', 150)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                
                logger.info("Initialized pyttsx3 TTS engine")
        except ImportError:
            logger.warning(f"TTS provider {self.tts_provider} not available")
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful
        """
        try:
            if not self.tts_engine:
                logger.warning("TTS engine not initialized")
                return False
            
            logger.info(f"Speaking: {text[:50]}...")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            return False
    
    def listen(self, duration: int = 5, language: str = "en") -> Optional[str]:
        """
        Listen for speech and convert to text.
        
        Args:
            duration: Recording duration in seconds
            language: Language code
            
        Returns:
            Transcribed text or None
        """
        try:
            # This is a placeholder - actual implementation would use
            # microphone recording and Whisper API
            logger.info(f"Listening for {duration} seconds...")
            
            # TODO: Implement actual speech recognition
            # For now, return None to indicate not implemented
            logger.warning("Speech recognition not yet implemented")
            return None
            
        except Exception as e:
            logger.error(f"Error listening: {e}")
            return None
    
    def set_voice(self, voice_id: int = 0) -> bool:
        """
        Set the TTS voice.
        
        Args:
            voice_id: Voice index
            
        Returns:
            True if successful
        """
        try:
            if not self.tts_engine:
                return False
            
            voices = self.tts_engine.getProperty('voices')
            if voice_id < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_id].id)
                logger.info(f"Set voice to: {voices[voice_id].name}")
                return True
            else:
                logger.warning(f"Voice ID {voice_id} out of range")
                return False
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def list_voices(self) -> list:
        """
        List available TTS voices.
        
        Returns:
            List of voice names
        """
        try:
            if not self.tts_engine:
                return []
            
            voices = self.tts_engine.getProperty('voices')
            return [v.name for v in voices]
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return []
