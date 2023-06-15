import numpy as np
from matplotlib import pyplot as plt
import mne
import pandas as pd
import time
import matplotlib.animation as ani


def data_csv(path: str, drop: list[str]):
    # Function to get the data from our own measurements
    # Only works with no labels
    df = pd.read_csv(path)
    df.drop(drop, axis=1, inplace=True)
    Xt = df.to_numpy()  # Containing time and channel data
    t = Xt[:, 0]
    X = Xt[:, 1:]
    n = X.shape[1]
    return t, X


def createInfo(channel_names, fs):
    channel_types = 'eeg'
    # montage = 'biosemi16'

    info = mne.create_info(channel_names, fs, channel_types)

    return info


def EEG_topo(i):
    ax.cla()
    for j, data_idx in enumerate([0, 1, 3, 7, 6, 8, 12, 10]):
        data[data_idx] = x_tr[j, i]

    evokedArray = mne.EvokedArray(data, info)
    evokedArray.set_montage(standard_montage)

    mne.viz.plot_topomap(evokedArray.data[:, 0], evokedArray.info, axes=ax)


standard_montage = mne.channels.make_standard_montage('biosemi16')
n_channels = len(standard_montage.ch_names)
info = createInfo(channel_names=standard_montage.ch_names, fs=250)
drop = ['Event Id', 'Event Date', 'Event Duration', 'Channel 9',
        'Channel 10', 'Channel 11', 'Epoch']
t, X = data_csv('Thib_lefthand_filtered_1.csv', drop)
x_tr = np.transpose(X)
data = np.zeros((n_channels, 1))
fig, ax = plt.subplots(figsize=(10, 10))
animator = ani.FuncAnimation(fig, EEG_topo, frames=15, interval=500)
plt.show()
