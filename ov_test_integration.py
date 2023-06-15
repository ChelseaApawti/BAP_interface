# -*- coding: utf-8 -*-
"""
Created on Wed May 31 14:42:45 2023

@author: chels
"""

import numpy
from matplotlib import pyplot as plt
import matplotlib
import mne
import time


# Box class that inherits from OVBox
class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.signalHeader = None
        self.fig=plt.figure(figsize=(10,10))
        self.standard_montage = mne.channels.make_standard_montage('biosemi16')
        self.n_channels = len(self.standard_montage.ch_names)
        self.info = mne.create_info(ch_names=self.standard_montage.ch_names, sfreq=250, ch_types='eeg', verbose=None)
        self.info.set_montage(self.standard_montage)
        self.data = numpy.zeros((self.n_channels,32))

    # The process method will be called by openvibe on every clock tick
    def process(self):
       # Iterate over all the input chunks in the input buffer
       for chunkIndex in range( len(self.input[0]) ):
          # If it is a header, it is saved
          if(type(self.input[0][chunkIndex]) == OVSignalHeader):
             self.signalHeader = self.input[0].pop()
                          

          # If it is a buffer, it gets popped and put in a numpy array at the right dimensions
          elif(type(self.input[0][chunkIndex]) == OVSignalBuffer):
             chunk = self.input[0].pop()
             numpyBuffer = numpy.array(chunk).reshape(tuple(self.signalHeader.dimensionSizes))
             chunk = OVSignalBuffer(chunk.startTime, chunk.endTime, numpyBuffer.tolist())
             
             # Put the data of the channels corresponding to the sensors in the data array
             for j, data_idx in enumerate([0,1,3,7,6,8,12,10]):
                 self.data[data_idx,:]=numpyBuffer[j]
                 
             # Average the data of each channel    
             data_avg=numpy.zeros((16,1))
             for n in range(16):
                 data_avg[n] = numpy.average(self.data[n,:])
                 
             # Create an evoked object and set the montage 
             evokedArray = mne.EvokedArray(data_avg, self.info)
             evokedArray.set_montage(self.standard_montage)
             
             # Clear the window and create a new subplot
             plt.clf()
             ax=plt.subplot(1,1,1)
             
             # Plot the topomap in the new subplot
             mne.viz.plot_topomap(evokedArray.data[:,0], self.info,axes=ax)
             
             
          # At the end-of-stream, print a message
          elif(type(self.input[0][chunkIndex]) == OVSignalEnd):
             self.output[0].append(self.input[0].pop())
             print("End of signal")

# Notify OpenVibe that the box instance 'box' is now an instance of MyOVBox.
box = MyOVBox()