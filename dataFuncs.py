import numpy as np

def plotLiveData(array, traceObjects, sweepInfo, chunkCounter):
    '''
    Process data received from Mantis and plot in PyQt Widget
    created with PlotUI

    Chunk counter keeps track of number of data chunks received
    so that a full sweep can be reconstructed

    : param array: nparray with data chunk
    : param traceObject: list with pyqtgraph plot objects
    : param sweepInfo: list containing chunkSize, sweepSize, sweepArray
    : param chunkCounter: chunk number in sweep
    '''

    dataTraceObject, statsObject = traceObjects
    chunkSize, sweepSize, sweepArray = sweepInfo

    stats, avgdata = [], []
    dataTraceObject.setData(sweepArray)
    sweepArray[chunkCounter:chunkCounter+chunkSize] = array

    if chunkCounter==0:
        #dataTraceObject.setData(sweepArray)
        statsObject.data.append(np.max(sweepArray))
        statsObject.setData(np.array(statsObject.data))
        print("sweep")
