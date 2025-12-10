# import sounddevice as sd
# from typing import List, Optional, Dict
# from utils.logger import Logger

# class MicrophoneDetector:
#     def __init__(self):
#         self.logger = Logger("MicrophoneDetector")
#         self.available_devices = []
#         self.default_device = None
    
#     def detect_microphones(self) -> List[Dict]:
#         try:
#             devices = sd.query_devices()
#             self.available_devices = []
            
#             for idx, device in enumerate(devices):
#                 if device['max_input_channels'] > 0:
#                     self.available_devices.append({
#                         'index': idx,
#                         'name': device['name'],
#                         'channels': device['max_input_channels'],
#                         'sample_rate': device['default_samplerate']
#                     })
            
#             if self.available_devices:
#                 self.default_device = self.available_devices[0]
#                 self.logger.info(f"Detected {len(self.available_devices)} microphone(s)")
#             else:
#                 self.logger.warning("No microphones detected")
            
#             return self.available_devices
#         except Exception as e:
#             self.logger.error(f"Error detecting microphones: {e}")
#             return []
    
#     def get_default_device(self) -> Optional[Dict]:
#         if not self.default_device:
#             self.detect_microphones()
#         return self.default_device
    
#     def set_default_device(self, device_index: int):
#         for device in self.available_devices:
#             if device['index'] == device_index:
#                 self.default_device = device
#                 self.logger.info(f"Set default device to: {device['name']}")
#                 return True
#         return False

import sounddevice as sd
from typing import List, Optional, Dict
from utils.logger import Logger

class MicrophoneDetector:
    def __init__(self):
        self.logger = Logger("MicrophoneDetector")
        self.available_devices = []
        self.default_device = None
    
    def detect_microphones(self) -> List[Dict]:
        try:
            devices = sd.query_devices()
            self.available_devices = []

            for idx, d in enumerate(devices):
                # Skip devices with no input channels
                if d.get("max_input_channels", 0) <= 0:
                    continue

                name = d.get("name", "").lower()

                # Skip monitor/loopback devices (they are not mics)
                if "monitor" in name:
                    continue

                # Store real microphone devices
                self.available_devices.append({
                    "index": idx,
                    "name": d.get("name", ""),
                    "channels": d.get("max_input_channels", 1),
                    "sample_rate": 44100,  # Force stable rate for Ubuntu mics
                })

            # Auto-select best microphone
            self.default_device = self._select_best_microphone()

            if self.default_device:
                self.logger.info(f"Default microphone: {self.default_device['name']} (index {self.default_device['index']})")
            else:
                self.logger.warning("No usable microphone found.")

            return self.available_devices

        except Exception as e:
            self.logger.error(f"Error detecting microphones: {e}")
            return []

    def _select_best_microphone(self) -> Optional[Dict]:
        """
        Prefer:
        1. 'alsa_input.*analog-stereo'
        2. any remaining input device
        """
        if not self.available_devices:
            return None

        # Priority device (most Ubuntu laptops)
        for d in self.available_devices:
            if "analog" in d["name"].lower():
                return d
        
        # Fallback: first available mic
        return self.available_devices[0]

    def get_default_device(self) -> Optional[Dict]:
        if not self.default_device:
            self.detect_microphones()
        return self.default_device
    
    def set_default_device(self, device_index: int):
        for device in self.available_devices:
            if device["index"] == device_index:
                self.default_device = device
                self.logger.info(f"Manually set default mic: {device['name']}")
                return True
        return False
