"""
Text-to-Speech engine for audio output
"""

import os
import time
from typing import Optional
import threading

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: pyttsx3 not available. Audio output disabled.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

class TTSEngine:
    """
    Text-to-Speech engine with multiple backend support
    """
    
    def __init__(self, audio_dir: str = "audio", use_gtts: bool = False):
        """
        Initialize TTS engine
        
        Args:
            audio_dir: Directory to save audio files
            use_gtts: Use Google TTS instead of pyttsx3
        """
        self.audio_dir = audio_dir
        self.use_gtts = use_gtts and GTTS_AVAILABLE
        
        # Create audio directory if it doesn't exist
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # Initialize pyttsx3 engine if available and not using gtts
        self.engine = None
        if TTS_AVAILABLE and not self.use_gtts:
            try:
                self.engine = pyttsx3.init()
                # Configure voice settings
                self.engine.setProperty('rate', 160)  # Speed
                self.engine.setProperty('volume', 0.9)  # Volume
                
                # Try to set a good voice
                voices = self.engine.getProperty('voices')
                if voices:
                    # Prefer English voices
                    for voice in voices:
                        if 'english' in voice.name.lower():
                            self.engine.setProperty('voice', voice.id)
                            break
            except Exception as e:
                print(f"Warning: Could not initialize pyttsx3 engine: {e}")
                self.engine = None
    
    def set_voice_personality(self, personality: str = "neutral"):
        """
        Adjust voice settings based on personality
        
        Args:
            personality: "confident" (CEO) or "analytical" (investor) or "neutral"
        """
        if not self.engine:
            return
        
        try:
            if personality == "confident":
                # CEO voice: slightly faster, higher volume
                self.engine.setProperty('rate', 170)
                self.engine.setProperty('volume', 0.95)
            elif personality == "analytical":
                # Investor voice: moderate pace, clear
                self.engine.setProperty('rate', 155)
                self.engine.setProperty('volume', 0.90)
            else:
                # Neutral
                self.engine.setProperty('rate', 160)
                self.engine.setProperty('volume', 0.90)
        except Exception as e:
            print(f"Warning: Could not set voice personality: {e}")
    
    def speak(self, text: str, save_as: Optional[str] = None, blocking: bool = True):
        """
        Convert text to speech and play
        
        Args:
            text: Text to speak
            save_as: Optional filename to save audio
            blocking: Wait for speech to complete
        """
        if not text:
            return
        
        # Clean text for TTS
        clean_text = self._clean_text(text)
        
        if self.use_gtts:
            self._speak_gtts(clean_text, save_as)
        elif self.engine:
            self._speak_pyttsx3(clean_text, save_as, blocking)
        else:
            print(f"\n[TTS NOT AVAILABLE - TEXT ONLY]\n{text}\n")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text for better TTS output
        """
        # Remove any remaining markdown or special characters
        text = text.replace('*', '').replace('#', '').replace('`', '')
        text = text.replace('_', '').replace('~', '')
        
        # Fix common abbreviations for better pronunciation
        replacements = {
            '$': 'dollars ',
            '%': ' percent',
            '&': ' and ',
            'B': ' billion',
            'M': ' million',
            'K': ' thousand',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _speak_pyttsx3(self, text: str, save_as: Optional[str], blocking: bool):
        """
        Speak using pyttsx3 engine
        """
        try:
            if save_as:
                filepath = os.path.join(self.audio_dir, save_as)
                self.engine.save_to_file(text, filepath)
                self.engine.runAndWait()
                print(f"[Audio saved: {filepath}]")
            
            if blocking:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                # Non-blocking speech
                thread = threading.Thread(target=self._speak_async, args=(text,))
                thread.daemon = True
                thread.start()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def _speak_async(self, text: str):
        """
        Speak asynchronously
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Async TTS Error: {e}")
    
    def _speak_gtts(self, text: str, save_as: Optional[str]):
        """
        Speak using Google TTS
        """
        try:
            filename = save_as if save_as else f"temp_{int(time.time())}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filepath)
            print(f"[Audio saved: {filepath}]")
            
            # Try to play the audio file
            self._play_audio_file(filepath)
        except Exception as e:
            print(f"GTTS Error: {e}")
    
    def _play_audio_file(self, filepath: str):
        """
        Play audio file using system player
        """
        import platform
        import subprocess
        
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", filepath], check=True)
            elif system == "Linux":
                # Try multiple players
                for player in ["mpg123", "ffplay", "aplay"]:
                    try:
                        subprocess.run([player, filepath], check=True, stderr=subprocess.DEVNULL)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            elif system == "Windows":
                os.startfile(filepath)
        except Exception as e:
            print(f"Could not play audio file: {e}")
    
    def cleanup(self):
        """
        Cleanup TTS engine
        """
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

# Singleton instance
_tts_instance = None

def get_tts_engine(audio_dir: str = "audio", personality: str = "neutral") -> TTSEngine:
    """
    Get or create TTS engine singleton
    """
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSEngine(audio_dir=audio_dir)
    
    _tts_instance.set_voice_personality(personality)
    return _tts_instance