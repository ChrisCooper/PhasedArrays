import wavio
import math
import numpy as np
from dataclasses import dataclass
from IPython.display import Audio
from IPython.core.display import display
import matplotlib.pyplot as plt

speed_of_sound = 343 # m/s

def play(filename):
    display(Audio(filename, autoplay=True))

def play_tmp(x, sample_rate):
    wavio.write('tmp.wav', x, sample_rate, sampwidth=3)
    play('tmp.wav')


@dataclass
class SampleData:
    duration: float # sample duration (seconds)
    sample_rate: float = 44100 # samples per second

def gen_tone(frequency, duration, sample_rate):
    duration = duration
    rate = sample_rate
    # Timestamps of each individual sample
    t = np.linspace(0, duration, int(duration*rate), endpoint=False)
    x = np.sin(2*np.pi * frequency * t)
    return x

def gen_chord(freqs, duration, sample_rate):
    return add_waves([gen_tone(f, duration, sample_rate) for f in freqs])

def delay(samples, time, sample_rate):
    num_new_samples = int(time * sample_rate)
    new_samples = np.zeros(num_new_samples, dtype=samples[0].dtype)
    
    return np.concatenate([new_samples, samples])

def pad_even(waves):
    target_length = max(len(w) for w in waves)
    
    result = [np.zeros(target_length, dtype=w.dtype) for w in waves]
    
    # wish we could just np.sum(waves, axis=0)
    for i, w in enumerate(waves):
        result[i][:len(w)] = w

    return result

def add_waves(waves):
    waves = pad_even(waves)

    return np.sum(waves, axis=0)

def travel_time(pos1, pos2):
    dx = (pos2[0] - pos1[0])**2
    dy = (pos2[1] - pos1[1])**2
    
    return math.sqrt(dx + dy) / speed_of_sound

def wavelength(f):
    return speed_of_sound / f

def gen_listener_locs(num_listeners, spacing=0.1):
    xs = np.arange(-spacing * num_listeners/2, spacing * num_listeners/2, spacing)
    return np.column_stack((xs, np.zeros(num_listeners)))

def gen_listener_waves(listener_locs, source_locs, sounds, sample_rate):
    listener_sounds = [[] for i in range(len(listener_locs))]
        
    # Create the delayed version of each sound clip for each listener
    for i in range(len(listener_locs)):
        for j in range(len(source_locs)):
            tt = travel_time(source_locs[j], listener_locs[i])
            delayed = delay(sounds[j], tt, sample_rate)
            listener_sounds[i].append(delayed)

    # Combine tracks to create unified listener waves for each listener
    listener_waves = [add_waves(ls) for ls in listener_sounds]
    listener_waves = pad_even(listener_waves)
    return listener_waves

def read_wav(filename):
    return wavio.read(filename).data.flatten()

def plot_wav_file(filename):
    wav = read_wav(filename)
    plt.plot(wav.transpose())
    plt.show()

def play_wav_file(filename, sample_rate):
    wav = read_wav(filename)
    play_tmp(wav, sample_rate)

def listen_to_coordinates(listener_locs, listener_waves, target_coords, sample_rate):
        # Calculate travel_time for each listener
        travel_times = [travel_time(l_loc, target_coords) for l_loc in listener_locs]
        max_tt = max(travel_times)

        # Calculate appropriate dely given travel times
        delays = [max_tt - travel_times[i] for i in range(len(travel_times))]
        
        # Delay each clip by its appropriate delay
        delayed_clips = [delay(listener_waves[i], delays[i], sample_rate) for i in range(len(delays))]
        
        # Combine all delayed wave into one clip
        result = add_waves(delayed_clips)
        
        return result
