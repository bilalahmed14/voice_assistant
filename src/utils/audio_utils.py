import numpy as np
import torch
import torchaudio
import librosa
from typing import Tuple, Optional

def load_audio_file(file_path: str, target_sr: int = 22050) -> Tuple[torch.Tensor, int]:
    """
    Load and preprocess an audio file.
    
    Args:
        file_path: Path to the audio file
        target_sr: Target sample rate
        
    Returns:
        Tuple of (audio tensor, sample rate)
    """
    waveform, sample_rate = torchaudio.load(file_path)
    
    # Resample if necessary
    if sample_rate != target_sr:
        resampler = torchaudio.transforms.Resample(sample_rate, target_sr)
        waveform = resampler(waveform)
    
    return waveform, target_sr

def preprocess_audio(waveform: torch.Tensor, sample_rate: int) -> torch.Tensor:
    """
    Preprocess audio for voice cloning.
    
    Args:
        waveform: Audio waveform tensor
        sample_rate: Sample rate of the audio
        
    Returns:
        Preprocessed audio tensor
    """
    # Convert to mono if stereo
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    
    # Normalize audio
    waveform = waveform / torch.max(torch.abs(waveform))
    
    return waveform

def extract_mel_spectrogram(
    waveform: torch.Tensor,
    sample_rate: int,
    n_fft: int = 1024,
    hop_length: int = 256,
    n_mels: int = 80
) -> torch.Tensor:
    """
    Extract mel spectrogram from audio.
    
    Args:
        waveform: Audio waveform tensor
        sample_rate: Sample rate of the audio
        n_fft: FFT window size
        hop_length: Hop length for STFT
        n_mels: Number of mel bands
        
    Returns:
        Mel spectrogram tensor
    """
    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        n_mels=n_mels
    )
    
    mel_spec = mel_transform(waveform)
    mel_spec = torch.log(torch.clamp(mel_spec, min=1e-5))
    
    return mel_spec

def save_audio(
    waveform: torch.Tensor,
    sample_rate: int,
    file_path: str,
    format: Optional[str] = None
) -> None:
    """
    Save audio to file.
    
    Args:
        waveform: Audio waveform tensor
        sample_rate: Sample rate of the audio
        file_path: Path to save the audio file
        format: Audio format (e.g., 'wav', 'mp3'). If None, inferred from file_path
    """
    torchaudio.save(
        file_path,
        waveform,
        sample_rate,
        format=format
    ) 