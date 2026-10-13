import os
import math
import numpy as np
import subprocess
import hashlib
from typing import Optional
from ...utils.logger import logger
from .base import AudioProvider

class AmbientHarmonicAudioProvider(AudioProvider):
    """
    Dynamic Multi-Layer Procedural Music Synthesizer.
    Generates rich, evolving chord progressions, arpeggiated textures,
    basslines, and rhythmic grooves tailored to the chosen style.
    Each project receives a unique transposed key and rhythm variation.
    """

    # Progressions in semitones relative to root
    STYLE_PROGRESSIONS = {
        "Cinematic": [
            [0, 3, 7, 10],   # i (minor 7th)
            [-4, 0, 3, 7],   # VI
            [-2, 2, 5, 9],   # VII
            [0, 3, 7, 12]    # i (higher octave)
        ],
        "Technology": [
            [0, 4, 7, 11],   # I (major 7th)
            [2, 5, 9, 12],   # ii
            [4, 7, 11, 14],  # iii
            [0, 4, 7, 12]    # I
        ],
        "Energetic": [
            [0, 4, 7],       # I
            [7, 11, 14],     # V
            [9, 12, 16],     # vi
            [5, 9, 12]       # IV
        ],
        "Calm": [
            [0, 4, 7, 9],    # major 6th
            [5, 9, 12, 16],  # IV major
            [2, 5, 9, 12],   # ii minor
            [0, 4, 7, 12]    # I
        ]
    }

    # Base root frequencies (C3, D3, E3, F3, G3, A3)
    ROOT_NOTES = [130.81, 146.83, 164.81, 174.61, 196.00, 220.00]

    async def generate_music(
        self,
        style: str,
        duration: float,
        output_path: str
    ) -> str:
        if style.lower() == "none":
            # Generate silence
            os.system(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t {duration} -q:a 9 -acodec libmp3lame "{output_path}" >nul 2>&1')
            return output_path

        sample_rate = 44100
        total_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, total_samples, False)

        # Derive reproducible seed from output path / project id
        path_hash = int(hashlib.md5(output_path.encode()).hexdigest()[:8], 16)
        root_idx = path_hash % len(self.ROOT_NOTES)
        base_freq = self.ROOT_NOTES[root_idx]

        progression = self.STYLE_PROGRESSIONS.get(style, self.STYLE_PROGRESSIONS["Cinematic"])
        chord_duration = max(3.0, duration / len(progression))

        audio = np.zeros(total_samples)

        # Build chord progression over time
        for step_idx, chord_semitones in enumerate(progression):
            start_time = step_idx * chord_duration
            end_time = min(duration, (step_idx + 1) * chord_duration)
            if start_time >= duration:
                break

            mask = (t >= start_time) & (t < end_time)
            t_section = t[mask] - start_time
            section_samples = len(t_section)
            if section_samples == 0:
                continue

            section_audio = np.zeros(section_samples)

            # 1. Warm lush pad layer for chord
            for semi in chord_semitones:
                freq = base_freq * (2.0 ** (semi / 12.0))
                # Add fundamental sine + subtle harmonics
                pad_wave = np.sin(2 * np.pi * freq * t_section)
                pad_wave += 0.3 * np.sin(2 * np.pi * (freq * 2) * t_section)
                pad_wave += 0.1 * np.sin(2 * np.pi * (freq * 3) * t_section)
                # Gentle analog tremolo
                tremolo = 1.0 + 0.1 * np.sin(2 * np.pi * 0.5 * t_section)
                section_audio += pad_wave * tremolo * (0.10 / len(chord_semitones))

            # 2. Deep sub-bass (Root of this chord / 2)
            root_chord_freq = base_freq * (2.0 ** (chord_semitones[0] / 12.0)) / 2.0
            bass_wave = 0.18 * np.sin(2 * np.pi * root_chord_freq * t_section)
            section_audio += bass_wave

            # 3. Dynamic rhythm / pulse per style
            if style in ["Energetic", "Technology"]:
                tempo_hz = 4.0 if style == "Energetic" else 2.5
                pulse = 0.5 * (1.0 + np.sin(2 * np.pi * tempo_hz * t_section))
                # Rhythmic high arpeggiation
                arp_freq = base_freq * (2.0 ** (chord_semitones[(step_idx % len(chord_semitones))] / 12.0)) * 2.0
                arp_wave = 0.08 * np.sin(2 * np.pi * arp_freq * t_section) * pulse
                section_audio += arp_wave
                section_audio *= (0.75 + 0.25 * pulse)

            # Smooth crossfade between chords (0.4s)
            fade_samples = min(int(0.4 * sample_rate), section_samples // 3)
            if fade_samples > 0:
                section_audio[:fade_samples] *= np.linspace(0.1, 1.0, fade_samples)
                section_audio[-fade_samples:] *= np.linspace(1.0, 0.1, fade_samples)

            audio[mask] += section_audio

        # Overall master fade-in (1.5s) and fade-out (2.0s)
        fade_in = int(sample_rate * 1.5)
        fade_out = int(sample_rate * 2.0)
        if total_samples > (fade_in + fade_out):
            audio[:fade_in] *= np.linspace(0, 1, fade_in)
            audio[-fade_out:] *= np.linspace(1, 0, fade_out)

        # Normalize volume cleanly
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = (audio / max_val) * 0.80
        audio_int16 = (audio * 32767).astype(np.int16)

        # Save to temporary WAV then encode to MP3 via FFmpeg
        temp_wav = output_path.replace(".mp3", "_temp.wav")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        import wave
        with wave.open(temp_wav, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        cmd = [
            "ffmpeg", "-y", "-i", temp_wav,
            "-codec:a", "libmp3lame", "-b:a", "192k",
            output_path
        ]
        subprocess.run(cmd, capture_output=True)

        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

        logger.info(f"[AudioTool] Synthesized {style} music track ({duration:.1f}s, root {base_freq:.1f}Hz) -> {output_path}")
        return output_path

def get_audio_provider() -> AudioProvider:
    return AmbientHarmonicAudioProvider()
