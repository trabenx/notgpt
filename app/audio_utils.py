import base64
import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy.io.wavfile import write
import tempfile
from PySide6.QtCore import QTimer
from io import BytesIO

def record_audio(duration=5, sample_rate=44100):
    """Record audio from microphone"""
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), 
                       samplerate=sample_rate, 
                       channels=1, 
                       dtype='float32')
    sd.wait()
    return audio_data, sample_rate

def audio_to_base64(audio_data, sample_rate):
    """Convert audio data to base64 encoded WAV"""
    try:
        # Convert to proper format
        if isinstance(audio_data, np.ndarray):
            # Normalize to int16
            audio_data = (audio_data * 32767).astype(np.int16)
        
        # Create in-memory WAV file
        buffer = BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        
        # Convert to base64
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')
    except Exception as e:
        print(f"Audio conversion error: {str(e)}")
        return None

def base64_to_audio(base64_str):
    """Convert base64 string to audio data"""
    audio_bytes = base64.b64decode(base64_str)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()
        return sf.read(temp_file.name)