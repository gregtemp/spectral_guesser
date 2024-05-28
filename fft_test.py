import os
import numpy as np
import torch
import torchaudio
import matplotlib.pyplot as plt
import json

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def compute_fft_frames(audio_path, fft_size=1024, hop_length=256, window_fn=torch.hamming_window, num_frames_to_save=20, save_dir='test'):
    # Load the audio file
    waveform, sample_rate = torchaudio.load(audio_path)
    
    # Convert to mono by averaging channels if necessary
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    
    # Apply the window function
    window = window_fn(fft_size)
    
    # Compute the FFT frames
    num_samples = waveform.shape[1]
    num_frames = (num_samples - fft_size) // hop_length + 1
    fft_frames = []

    for i in range(num_frames):
        start = i * hop_length
        end = start + fft_size
        frame = waveform[:, start:end] * window
        fft = torch.fft.fft(frame, n=fft_size)
        fft_magnitude = torch.abs(fft)
        fft_frames.append(fft_magnitude)

    fft_frames = torch.stack(fft_frames)
    
    # Save the first 20 frames as images
    os.makedirs(save_dir, exist_ok=True)
    for i in range(min(num_frames_to_save, len(fft_frames))):
        frame = fft_frames[i]
        plt.imshow(frame[0].numpy(), aspect='auto', origin='lower')
        plt.colorbar()
        plt.title(f'FFT Frame {i}')
        plt.savefig(os.path.join(save_dir, f'fft_frame_{i}.jpg'))
        plt.close()

# Example usage
with open("samples.json", 'r') as json_file:
    json_dict = json.load(json_file)

audio_files = json_dict["kick"]


audio_path = audio_files[0]
compute_fft_frames(audio_path)
