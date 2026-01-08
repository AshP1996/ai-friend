"""
Pitch and tone analysis from audio for emotion detection
"""
import numpy as np
from typing import Dict, Any, Optional
from utils.logger import Logger

logger = Logger("PitchAnalyzer")

class PitchAnalyzer:
    """Analyze pitch and tone from audio PCM data"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.frame_size = 1024
        self.hop_length = 512
    
    def analyze_pitch(self, pcm_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze pitch characteristics from PCM audio
        Returns pitch, energy, and emotion indicators
        """
        try:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
            audio_data = audio_data / 32768.0  # Normalize
            
            if len(audio_data) < self.frame_size:
                return self._default_analysis()
            
            # Calculate pitch using autocorrelation
            pitch = self._estimate_pitch(audio_data)
            
            # Calculate energy/volume
            energy = np.mean(np.abs(audio_data))
            energy_db = 20 * np.log10(energy + 1e-10)
            
            # Detect voice activity
            is_speech = energy > 0.01
            
            # Analyze pitch variation (emotion indicator)
            pitch_variation = self._calculate_pitch_variation(audio_data)
            
            # Determine emotion from pitch characteristics
            emotion_hint = self._pitch_to_emotion(pitch, pitch_variation, energy)
            
            return {
                "pitch_hz": pitch,
                "energy": float(energy),
                "energy_db": float(energy_db),
                "is_speech": is_speech,
                "pitch_variation": float(pitch_variation),
                "emotion_hint": emotion_hint,
                "confidence": 0.7 if is_speech else 0.3
            }
        except Exception as e:
            logger.debug(f"Pitch analysis error: {e}")
            return self._default_analysis()
    
    def _estimate_pitch(self, audio: np.ndarray) -> float:
        """Estimate fundamental frequency using autocorrelation"""
        try:
            # Use autocorrelation to find pitch
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find peaks (avoid DC component)
            min_period = int(self.sample_rate / 800)  # Max 800 Hz
            max_period = int(self.sample_rate / 80)   # Min 80 Hz
            
            if len(autocorr) < max_period:
                return 0.0
            
            # Find first significant peak in valid range
            for i in range(min_period, min(max_period, len(autocorr))):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    if autocorr[i] > 0.3 * autocorr[0]:  # Significant peak
                        pitch = self.sample_rate / i
                        return max(80.0, min(400.0, pitch))  # Clamp to human range
            
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_pitch_variation(self, audio: np.ndarray) -> float:
        """Calculate pitch variation (indicates emotion intensity)"""
        try:
            # Analyze in chunks
            chunk_size = self.frame_size
            pitches = []
            
            for i in range(0, len(audio) - chunk_size, self.hop_length):
                chunk = audio[i:i+chunk_size]
                pitch = self._estimate_pitch(chunk)
                if pitch > 0:
                    pitches.append(pitch)
            
            if len(pitches) < 2:
                return 0.0
            
            # Calculate standard deviation (variation)
            return float(np.std(pitches))
        except Exception:
            return 0.0
    
    def _pitch_to_emotion(self, pitch: float, variation: float, energy: float) -> str:
        """Map pitch characteristics to emotion hints"""
        if pitch == 0:
            return "neutral"
        
        # High pitch + high variation = excited/happy
        if pitch > 200 and variation > 30:
            return "excited"
        
        # High pitch + low variation = happy
        if pitch > 180:
            return "happy"
        
        # Low pitch + low energy = sad
        if pitch < 120 and energy < 0.05:
            return "sad"
        
        # High variation = emotional
        if variation > 40:
            return "emotional"
        
        # Normal range = neutral
        return "neutral"
    
    def _default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when audio is insufficient"""
        return {
            "pitch_hz": 0.0,
            "energy": 0.0,
            "energy_db": -60.0,
            "is_speech": False,
            "pitch_variation": 0.0,
            "emotion_hint": "neutral",
            "confidence": 0.0
        }
