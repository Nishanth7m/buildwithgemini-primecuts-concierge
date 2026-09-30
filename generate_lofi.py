"""Generate an upbeat, groovy lo-fi background music track as a WAV file.
Uses numpy + scipy to synthesize a cozy beat with warm electric piano chords,
vinyl crackle, a smooth bassline, and punchy drum groove.
"""

import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100
BPM = 84
BEAT_DUR = 60.0 / BPM
BAR_DUR = BEAT_DUR * 4
NUM_BARS = 8
TOTAL_DUR = BAR_DUR * NUM_BARS
TOTAL_SAMPLES = int(SAMPLE_RATE * TOTAL_DUR)

t = np.linspace(0, TOTAL_DUR, TOTAL_SAMPLES, endpoint=False)

def envelope(duration, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
    length = int(duration * SAMPLE_RATE)
    a_len = int(attack * SAMPLE_RATE)
    d_len = int(decay * SAMPLE_RATE)
    r_len = int(release * SAMPLE_RATE)
    s_len = max(0, length - a_len - d_len - r_len)
    
    env = np.concatenate([
        np.linspace(0, 1, a_len),
        np.linspace(1, sustain, d_len),
        np.full(s_len, sustain),
        np.linspace(sustain, 0, r_len)
    ])
    if len(env) < length:
        env = np.pad(env, (0, length - len(env)))
    return env[:length]

# 1. Warm Vinyl Crackle & Ambient Warmth
np.random.seed(42)
crackle = np.random.normal(0, 0.015, TOTAL_SAMPLES)
crackle_pops = np.random.choice([0, 0.08, -0.08], size=TOTAL_SAMPLES, p=[0.9995, 0.00025, 0.00025])
ambient = crackle + crackle_pops

# 2. Electric Piano / Rhodes chord progression (Warm, Jazz/Lo-Fi 7th & 9th chords)
# Progression: Cmaj7 - Am7 - Dm7 - G7 (Classic upbeat feel)
chords = [
    [261.63, 329.63, 392.00, 493.88], # Cmaj7
    [220.00, 261.63, 329.63, 392.00], # Am7
    [293.66, 349.23, 440.00, 523.25], # Dm7
    [196.00, 246.94, 293.66, 349.23], # G7
]

rhodes = np.zeros(TOTAL_SAMPLES)

for bar in range(NUM_BARS):
    bar_start_time = bar * BAR_DUR
    chord = chords[bar % len(chords)]
    for strum_idx in range(2):
        start_t = bar_start_time + strum_idx * (2 * BEAT_DUR)
        start_idx = int(start_t * SAMPLE_RATE)
        chord_dur = 1.9 * BEAT_DUR
        chord_samples = int(chord_dur * SAMPLE_RATE)
        
        env = envelope(chord_dur, attack=0.03, decay=0.3, sustain=0.4, release=0.3)
        tone = np.zeros(len(env))
        for freq in chord:
            # Fundamental + soft harmonics with vibrato
            vibrato = 1.0 + 0.004 * np.sin(2 * np.pi * 5.0 * np.linspace(0, chord_dur, len(env)))
            tone += 0.25 * np.sin(2 * np.pi * freq * vibrato * np.linspace(0, chord_dur, len(env)))
            tone += 0.10 * np.sin(2 * np.pi * freq * 2 * np.linspace(0, chord_dur, len(env)))
            tone += 0.04 * np.sin(2 * np.pi * freq * 3 * np.linspace(0, chord_dur, len(env)))
        
        end_idx = min(TOTAL_SAMPLES, start_idx + len(env))
        rhodes[start_idx:end_idx] += (tone * env)[:end_idx - start_idx]

# 3. Smooth Bassline (Sub warm sine)
bass_notes = [65.41, 55.00, 73.42, 49.00] # C2, A1, D2, G1
bass = np.zeros(TOTAL_SAMPLES)
for bar in range(NUM_BARS):
    root_freq = bass_notes[bar % len(bass_notes)]
    # Play on beat 1 and beat 3.5
    for beat_offset in [0.0, 1.5, 2.5]:
        b_start = bar * BAR_DUR + beat_offset * BEAT_DUR
        b_idx = int(b_start * SAMPLE_RATE)
        b_dur = BEAT_DUR * 0.9
        env = envelope(b_dur, attack=0.02, decay=0.2, sustain=0.6, release=0.1)
        b_tone = 0.5 * np.sin(2 * np.pi * root_freq * np.linspace(0, b_dur, len(env)))
        b_tone += 0.2 * np.sin(2 * np.pi * root_freq * 2 * np.linspace(0, b_dur, len(env)))
        end_idx = min(TOTAL_SAMPLES, b_idx + len(env))
        bass[b_idx:end_idx] += (b_tone * env)[:end_idx - b_idx]

# 4. Drums: Lo-Fi Kick, Snare/Clap, & Closed Hat
drums = np.zeros(TOTAL_SAMPLES)
for bar in range(NUM_BARS):
    bar_start = bar * BAR_DUR
    # Kick on beat 0 and 2.5
    for kick_beat in [0.0, 1.75, 2.5]:
        k_time = bar_start + kick_beat * BEAT_DUR
        k_idx = int(k_time * SAMPLE_RATE)
        k_dur = 0.25
        k_len = int(k_dur * SAMPLE_RATE)
        kt = np.linspace(0, k_dur, k_len)
        freq_sweep = 140 * np.exp(-kt * 25) + 45
        kick = 0.7 * np.sin(2 * np.pi * freq_sweep * kt) * np.exp(-kt * 15)
        end_idx = min(TOTAL_SAMPLES, k_idx + k_len)
        drums[k_idx:end_idx] += kick[:end_idx - k_idx]

    # Snare on beat 1 and 3
    for snare_beat in [1.0, 3.0]:
        s_time = bar_start + snare_beat * BEAT_DUR
        s_idx = int(s_time * SAMPLE_RATE)
        s_dur = 0.2
        s_len = int(s_dur * SAMPLE_RATE)
        st = np.linspace(0, s_dur, s_len)
        snare_body = 0.3 * np.sin(2 * np.pi * 180 * st) * np.exp(-st * 25)
        snare_noise = 0.25 * np.random.normal(0, 1, s_len) * np.exp(-st * 18)
        snare = snare_body + snare_noise
        end_idx = min(TOTAL_SAMPLES, s_idx + s_len)
        drums[s_idx:end_idx] += snare[:end_idx - s_idx]

    # Hi-hat on every 8th note (swing feel)
    for hat_idx in range(8):
        h_time = bar_start + hat_idx * (BEAT_DUR / 2) + (0.02 if hat_idx % 2 == 1 else 0.0)
        h_sample_idx = int(h_time * SAMPLE_RATE)
        h_dur = 0.06
        h_len = int(h_dur * SAMPLE_RATE)
        ht = np.linspace(0, h_dur, h_len)
        hat = 0.12 * np.random.normal(0, 1, h_len) * np.exp(-ht * 50)
        end_idx = min(TOTAL_SAMPLES, h_sample_idx + h_len)
        drums[h_sample_idx:end_idx] += hat[:end_idx - h_sample_idx]

# Mix everything down
mix = (ambient * 0.4) + (rhodes * 0.55) + (bass * 0.6) + (drums * 0.65)
# Soft limiter / normalization
max_val = np.max(np.abs(mix))
if max_val > 0:
    mix = (mix / max_val) * 0.85

audio_int16 = (mix * 32767).astype(np.int16)
wavfile.write("/config/Desktop/BuildWithGemini/lofi_beat.wav", SAMPLE_RATE, audio_int16)
print(f"Lo-fi background music generated successfully: {TOTAL_DUR:.1f}s at {SAMPLE_RATE}Hz")
