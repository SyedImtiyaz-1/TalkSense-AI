import pyttsx3
import pygame
import edge_tts
import tempfile
import asyncio
from config.settings import (
    CUSTOMER_VOICE_EDGE,
    AGENT_VOICE_EDGE,
    CUSTOMER_VOICE_ALT,
    AGENT_VOICE_ALT
)

class TTSService:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Initialize pyttsx3 engine for offline TTS
        try:
            self.engine = pyttsx3.init()
            self.setup_voices()
        except:
            self.engine = None
            print("⚠️ Offline TTS engine not available. Using Edge TTS only.")
    
    def setup_voices(self):
        """Setup different voices for customer and agent using pyttsx3"""
        if self.engine:
            voices = self.engine.getProperty('voices')
            if len(voices) >= 2:
                self.customer_voice = voices[0].id
                self.agent_voice = voices[1].id if len(voices) > 1 else voices[0].id
            else:
                self.customer_voice = voices[0].id if voices else None
                self.agent_voice = voices[0].id if voices else None
    
    def speak_offline(self, text, speaker_type="customer", rate=200):
        """Use pyttsx3 for offline TTS"""
        if not self.engine:
            return False
        
        try:
            # Set voice based on speaker type
            if speaker_type == "customer":
                self.engine.setProperty('voice', self.customer_voice)
                self.engine.setProperty('rate', rate)
            else:
                self.engine.setProperty('voice', self.agent_voice)
                self.engine.setProperty('rate', rate - 20)
            
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Offline TTS Error: {str(e)}")
            return False
    
    async def _generate_edge_tts_async(self, text, voice):
        """Async function to generate speech using Edge TTS"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_filename = tmp_file.name
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_filename)
            
            return tmp_filename
        except Exception as e:
            print(f"Edge TTS Generation Error: {str(e)}")
            return None
    
    def speak_edge_tts(self, text, speaker_type="customer", use_alt_voice=False):
        """Use Microsoft Edge TTS for speech synthesis"""
        try:
            # Select voice based on speaker type and alt preference
            if speaker_type == "customer":
                voice = CUSTOMER_VOICE_ALT if use_alt_voice else CUSTOMER_VOICE_EDGE
            else:
                voice = AGENT_VOICE_ALT if use_alt_voice else AGENT_VOICE_EDGE
            
            # Generate speech file
            tmp_filename = asyncio.run(self._generate_edge_tts_async(text, voice))
            if not tmp_filename:
                return False
            
            # Play the generated audio
            pygame.mixer.music.load(tmp_filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            return True
        except Exception as e:
            print(f"Edge TTS Error: {str(e)}")
            return False
    
    def stop_audio(self):
        """Stop any playing audio"""
        try:
            pygame.mixer.music.stop()
        except:
            pass

# Create a singleton instance
tts_service = TTSService() 