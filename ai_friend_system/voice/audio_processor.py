# import numpy as np
# from scipy import signal
# from typing import Optional
# from utils.logger import Logger

# class AudioProcessor:
#     def __init__(self):
#         self.logger = Logger("AudioProcessor")
    
#     def remove_noise(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
#         try:
#             # Simple noise reduction using high-pass filter
#             nyquist = sample_rate / 2
#             cutoff = 300  # Hz
#             normalized_cutoff = cutoff / nyquist
            
#             b, a = signal.butter(5, normalized_cutoff, btype='high')
#             filtered = signal.filtfilt(b, a, audio_data)
            
#             return filtered
#         except Exception as e:
#             self.logger.error(f"Error in noise removal: {e}")
#             return audio_data
    
#     def normalize_volume(self, audio_data: np.ndarray) -> np.ndarray:
#         try:
#             max_val = np.max(np.abs(audio_data))
#             if max_val > 0:
#                 return audio_data / max_val * 0.8
#             return audio_data
#         except Exception as e:
#             self.logger.error(f"Error in normalization: {e}")
#             return audio_data

import numpy as np
from scipy import signal
from typing import Optional
from utils.logger import Logger

class AudioProcessor:
    def __init__(self):
        self.logger = Logger("AudioProcessor")
    
    def remove_noise(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        try:
            if audio_data is None or len(audio_data) == 0:
                return audio_data

            # High-pass filter to remove rumble/noise
            nyquist = sample_rate / 2
            cutoff = 200  # Lowered for human voice clarity
            normalized_cutoff = cutoff / nyquist
            
            b, a = signal.butter(4, normalized_cutoff, btype='high')
            filtered = signal.filtfilt(b, a, audio_data)

            return filtered

        except Exception as e:
            self.logger.error(f"Error in noise removal: {e}")
            return audio_data
    
    def normalize_volume(self, audio_data: np.ndarray) -> np.ndarray:
        try:
            if audio_data is None or len(audio_data) == 0:
                return audio_data

            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                # Normalize within safe range to prevent clipping
                return audio_data / max_val * 0.75
            
            return audio_data

        except Exception as e:
            self.logger.error(f"Error in normalization: {e}")
            return audio_data
