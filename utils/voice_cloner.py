import os
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import resample
import base64
import time
import shutil

class VoiceCloner:
    def __init__(self, tts_provider="openai"):
        self.sample_rate = 44100
        self.channels = 1
        self.voice_samples_dir = 'voice_samples'
        self.static_dir = 'static'
        self.voice_features = None
        self.tts_provider = tts_provider.lower()
        self.cloned_voice_id = None
        
        # Initialize TTS clients
        if self.tts_provider == "openai":
            self.openai_client = OpenAI()
        elif self.tts_provider == "elevenlabs":
            self.elevenlabs_client = ElevenLabs(
                api_key=os.getenv("ELEVENLABS_API_KEY")
            )
        
        # Create necessary directories
        os.makedirs(self.voice_samples_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)

    def ensure_wav_format(self, input_path, output_path):
        """Convert audio to proper WAV format"""
        try:
            # Load audio with librosa for better format handling
            audio, sr = librosa.load(input_path, sr=self.sample_rate, mono=True)
            # Save with soundfile for better quality
            sf.write(output_path, audio, self.sample_rate)
            return True
        except Exception as e:
            print(f"Error converting audio: {str(e)}")
            return False

    def extract_voice_features(self, audio_path):
        """Extract voice features from the audio sample"""
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract features
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            pitch, magnitudes = librosa.piptrack(y=audio, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            
            # Calculate average pitch
            pitch_values = pitch[magnitudes > np.median(magnitudes)]
            avg_pitch = np.mean(pitch_values) if len(pitch_values) > 0 else 0
            
            # Calculate pitch range
            pitch_range = np.ptp(pitch_values) if len(pitch_values) > 0 else 0
            
            # Calculate speaking rate (syllables per second)
            onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
            tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
            
            # Calculate energy envelope
            energy = librosa.feature.rms(y=audio)[0]
            
            # Store features
            self.voice_features = {
                'mfccs': mfccs,
                'avg_pitch': avg_pitch,
                'pitch_range': pitch_range,
                'spectral_centroid': spectral_centroid,
                'tempo': tempo,
                'energy': energy,
                'duration': librosa.get_duration(y=audio, sr=sr)
            }
            
            return self.voice_features
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return None

    def process_voice_sample(self, input_path):
        """Process the voice sample and create a voice clone"""
        try:
            if self.tts_provider != "elevenlabs":
                raise Exception("Voice cloning is only supported with ElevenLabs provider")

            # Create a unique temporary file name
            temp_wav = os.path.join(self.voice_samples_dir, f'temp_{int(time.time())}.wav')
            
            # Convert to proper WAV format
            if not self.ensure_wav_format(input_path, temp_wav):
                raise Exception("Failed to convert audio to WAV format")

            try:
                # Clone the voice using ElevenLabs
                voice = self.elevenlabs_client.clone(
                    name="Cloned Voice",
                    description="A cloned voice from user sample",
                    files=[temp_wav]
                )
                
                # Store the cloned voice ID
                self.cloned_voice_id = voice.voice_id
                
                # Extract features for additional processing
                features = self.extract_voice_features(temp_wav)
                if not features:
                    raise Exception("Failed to extract voice features")
                
                # Save the original sample for reference
                modified_path = os.path.join(self.voice_samples_dir, 'modified_sample.wav')
                sf.write(modified_path, librosa.load(temp_wav, sr=self.sample_rate)[0], self.sample_rate)
                
                return True
            finally:
                # Clean up temporary file in a finally block to ensure it runs
                try:
                    if os.path.exists(temp_wav):
                        os.remove(temp_wav)
                except Exception as e:
                    print(f"Warning: Could not remove temporary file: {str(e)}")
            
        except Exception as e:
            print(f"Error processing voice sample: {str(e)}")
            return False

    def generate_with_openai(self, text):
        """Generate speech using OpenAI's TTS API"""
        try:
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # You can choose from: alloy, echo, fable, onyx, nova, shimmer
                input=text
            )
            temp_mp3 = os.path.join(self.static_dir, 'temp_tts.mp3')
            response.stream_to_file(temp_mp3)
            return temp_mp3
        except Exception as e:
            print(f"Error generating speech with OpenAI: {str(e)}")
            return None

    def generate_with_elevenlabs(self, text):
        """Generate speech using ElevenLabs API"""
        try:
            if not self.cloned_voice_id:
                raise Exception("No cloned voice available. Please record a voice sample first.")

            # Generate audio using ElevenLabs
            audio_stream = self.elevenlabs_client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=self.cloned_voice_id,
                model_id="eleven_multilingual_v2"
            )
            
            # Save to temporary file
            temp_mp3 = os.path.join(self.static_dir, 'temp_tts.mp3')
            with open(temp_mp3, 'wb') as f:
                for chunk in audio_stream:
                    if isinstance(chunk, bytes):
                        f.write(chunk)
            
            return temp_mp3
        except Exception as e:
            print(f"Error generating speech with ElevenLabs: {str(e)}")
            return None

    def generate_cloned_voice(self, text):
        """Generate speech using selected TTS provider"""
        try:
            print(f"Generating voice with provider: {self.tts_provider}")  # Debug log
            
            # Generate speech using selected provider
            if self.tts_provider == "openai":
                temp_mp3 = self.generate_with_openai(text)
            elif self.tts_provider == "elevenlabs":
                temp_mp3 = self.generate_with_elevenlabs(text)
            else:
                raise Exception(f"Unsupported TTS provider: {self.tts_provider}")

            if not temp_mp3:
                raise Exception(f"Failed to generate speech using {self.tts_provider}")
            
            try:
                print(f"Processing audio file: {temp_mp3}")  # Debug log
                # Load the generated audio
                audio, sr = librosa.load(temp_mp3, sr=self.sample_rate)
                
                # Generate unique filename with timestamp
                timestamp = int(time.time())
                output_filename = f'test_output_{timestamp}.wav'
                output_path = os.path.join(self.static_dir, output_filename)
                
                # Save the final audio
                sf.write(output_path, audio, self.sample_rate)
                
                # Clean up old output files
                for file in os.listdir(self.static_dir):
                    if file.startswith('test_output_') and file != output_filename:
                        try:
                            os.remove(os.path.join(self.static_dir, file))
                        except Exception as e:
                            print(f"Warning: Could not remove old file {file}: {str(e)}")
                
                return output_path
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(temp_mp3):
                        os.remove(temp_mp3)
                except Exception as e:
                    print(f"Warning: Could not remove temporary file: {str(e)}")
            
        except Exception as e:
            print(f"Error generating cloned voice: {str(e)}")
            return None 