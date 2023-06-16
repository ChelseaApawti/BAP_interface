import math

import numpy as np
from matplotlib import pyplot as plt, cm
import mne
import pandas as pd
from scipy import signal
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import time
import matplotlib.animation as ani


# get correct data columns from csv file by dropping certain elements
def data_csv(path: str, drop: list[str]):
    df = pd.read_csv(path)
    df.drop(drop, axis=1, inplace=True)
    Xt = df.to_numpy()
    t = Xt[:, 0]
    X = Xt[:, 1:]
    n = X.shape[1]
    return t, X  # return time array and data array (n_times, n_channels)


# create info object from MNE library. Info hold information needed for creating MNE raw object
def createInfo(channel_names, fs):
    channel_types = 'eeg'
    # montage = 'biosemi16'

    info = mne.create_info(channel_names, fs, channel_types)

    return info


# plot PSD
def plot_PSD(raw):
    raw.compute_psd().plot(picks="data", exclude="bads")
    plt.show()
    return


# plot raw eeg signals
def plot_raw(raw, ch_picks):
    raw.plot(n_channels=len(ch_picks), scalings='auto', title='EEG data',
             show=True, block=False, show_scrollbars=False, duration=5)
    return


# plot 16 short time averaged topomaps to show behaviour in time
def topomap_temporal(raw):
    x = raw._data
    times_seconds = np.arange(0, 0 + 17 * 0.1, 0.1)  # Define the time points in seconds
    times_samples = (times_seconds * raw.info['sfreq']).astype(int)  # Convert time points to sample indices
    n_subplots = min(len(times_samples) - 1, 16)
    fig, axes = plt.subplots(4, 4, figsize=(12, 12))  # Adjust the subplot layout as per your preference

    for i in range(n_subplots):
        ax = axes[i // 4, i % 4]  # Adjust the indexing for subplot layout
        t0 = times_samples[i]
        t1 = times_samples[i + 1]
        mne.viz.plot_topomap(x[:, t0:t1].mean(axis=1), raw.info, axes=ax, show=False)
        ax.set_title(f'Time: {times_seconds[i]:.1f}s-{times_seconds[i + 1]:.1f}s')
    plt.show()
    return


# plot power topomap at specific frequency
def plot_power_topomap(raw, sfreq):
    x = raw._data
    n_samples = x.shape[1]
    times = np.arange(n_samples) / sfreq

    # power spectrum of all channels
    power_spectrum = np.abs(np.fft.fft(x, axis=1)) ** 2

    # find index of frequency of interest
    frequency_of_interest = 15  # Frequency of interest (Hz)
    freq_index = int(frequency_of_interest * n_samples / sfreq)

    # get power values of freq of interest for all channels
    power_at_freq = power_spectrum[:, freq_index]

    # plot power topomap
    fig, ax = plt.subplots()
    mne.viz.plot_topomap(power_at_freq, raw.info, axes=ax, show=True)
    return


# plot power topomap at specific frequency bands
def plot_PSD_bands_topomap(raw):
    raw.compute_psd().plot_topomap()
    plt.show()
    return


# plot potential topomap averaged over time (you lose temporal dynamics)
def plot_potential_topomap(raw):
    x = raw._data
    fig, ax = plt.subplots(figsize=(10, 10))
    im, cm = mne.viz.plot_topomap(x.mean(axis=1), raw.info, contours=0, axes=ax, show=False)
    # colorbar
    ax_x_start = 0.8
    ax_x_width = 0.04
    ax_y_start = 0.1
    ax_y_height = 0.7
    cbar_ax = fig.add_axes([ax_x_start, ax_y_start, ax_x_width, ax_y_height])
    clb = fig.colorbar(im, cax=cbar_ax)
    clb.ax.set_title('Volt', fontsize=10)
    plt.show()
    return


# plot small segment of eeg data of one channel
def plot_zoomed_in_raw(raw, pick):
    raw.pick(pick)
    x = raw._data
    x = x[0]  # fix format of x for plt.plot
    # prepare data for plot
    Nx = x.size
    t = np.arange(0, Nx / fs, 1 / fs)
    # plot data
    plt.plot(t, x)
    plt.ylabel('Amplitude [μV]')
    plt.xlabel('Time [s]')
    plt.title('Checkerboard test O1 data segment')
    plt.show()
    return


# create a montage/info needed for plotting
# biosemi16 = standard 16 channel config using 10-20 system
standard_montage = mne.channels.make_standard_montage('biosemi16')
n_channels = len(standard_montage.ch_names)
info = createInfo(channel_names=standard_montage.ch_names, fs=250)
info.set_montage(standard_montage)
# names of biosemi16 channels
ch_names = ['Fp1', 'Fp2', 'F4', 'Fz', 'F3', 'T7', 'C3', 'Cz', 'C4', 'T8', 'P4', 'Pz', 'P3', 'O1', 'Oz', 'O2']
# measurement group only used these for motor imagery
motor_imagery = [0, 1, 3, 7, 6, 8, 12, 10]
# we only used these for visual functions
visual = [4, 2, 12, 11, 10, 13, 14, 15]
drop = ['Event Id', 'Event Date', 'Event Duration', 'Channel 9',
        'Channel 10', 'Channel 11', 'Epoch']
fs = 250
# time and data array
t, X = data_csv('short_hair3.csv', drop)
# mne expects data(n_channels, n_times) so need to transpose
x_tr = np.transpose(X)

# mne still expects 16 channels of data due to biosemi 16 config
# create empty array with zeros and fill in the channels we used
data = np.zeros((n_channels, x_tr.shape[1]))
for j, data_idx in enumerate(motor_imagery):
    data[data_idx, :] = x_tr[j, :]

# create raw object, contains data and other information
raw = mne.io.RawArray(data, info)
# mne expects data in V not uV so scale the data
raw.apply_function(lambda x: x * 1e-6)

# pick certain channels only
ch_picks = motor_imagery
ch_pick_names = ch_names[ch_picks[0]]
raw.pick(ch_picks)

# take only a portion of total data. First 10 to 20s were rest
raw.crop(tmin=13, tmax=15, include_tmax=True)
topomap_temporal(raw)
