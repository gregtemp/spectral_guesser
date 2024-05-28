import torch
from torch.utils.data import Dataset, DataLoader
import torchaudio
import os
import numpy as np
import matplotlib.pyplot as plt
import json

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class AudioFFTDataset(Dataset):
    def __init__(self, audio_files, sample_rate=44100, fft_size=512, hop_length=256):
        """
        Args:
            audio_files (list of str): List of paths to audio files.
            sample_rate (int): Sample rate for loading audio.
            fft_size (int): Number of FFT points.
            hop_length (int): Number of samples between successive frames.
        """
        self.audio_files = audio_files
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.hop_length = hop_length

    def __len__(self):
        return len(self.audio_files)

    def __getitem__(self, idx):
        # Load the audio file
        audio_path = self.audio_files[idx]
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # Resample if necessary
        if sample_rate != self.sample_rate:
            resample_transform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=self.sample_rate)
            waveform = resample_transform(waveform)
        
        # Convert to stereo by duplicating channels if necessary
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1)
        
        # Compute the FFT frames using numpy
        waveform_np = waveform.numpy()
        num_frames = (waveform_np.shape[1] - self.fft_size) // self.hop_length + 1
        fft_frames = []

        for i in range(num_frames):
            start = i * self.hop_length
            end = start + self.fft_size
            frame = waveform_np[:, start:end]
            fft = np.fft.fft(frame, n=self.fft_size)
            fft_magnitude = np.abs(fft)
            fft_frames.append(torch.tensor(fft_magnitude, dtype=torch.float32))

        return torch.stack(fft_frames)


# Example usage
# List all audio files in a directory (adjust the path to your dataset)
with open("samples.json", 'r') as json_file:
    json_dict = json.load(json_file)

audio_files = json_dict["kick"]

# Create the dataset and dataloader
audio_fft_dataset = AudioFFTDataset(audio_files)
audio_fft_dataloader = DataLoader(audio_fft_dataset, batch_size=1, shuffle=True)

# Example usage
for batch in audio_fft_dataloader:
    print(batch.shape)  # Should print (batch_size, num_frames, 2, fft_size)
    # Pass the batch to your model here
    break  # Just to show the shape

