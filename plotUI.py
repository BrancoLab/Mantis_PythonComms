import numpy as np
import pyqtgraph as pg
import sys, time
import socket
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QRunnable, QThreadPool
from mantis64API import mantisComms
from dataFuncs import plotLiveData


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    https://martinfitzpatrick.name/article/multithreading-pyqt-applications-with-qthreadpool/
    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)


class LivePlot(QtWidgets.QWidget):
    '''
    A basic PyQt Widget for plotting live data received from Mantis

    Data handling is done by a new thread using the Worker Class,
    as otherwise the UI freezes and doesn't update the plot.
    '''

    def __init__(self):
        super().__init__()
        self.w = QtGui.QWidget()

        # Plot Widgets
        self.plotWidget = pg.PlotWidget()
        self.plotWidget2 = pg.PlotWidget()

        # Plot objects
        self.trace = self.plotWidget.plot()
        self.avgTrace = self.plotWidget.plot(pen='c')
        self.stats = self.plotWidget2.plot(pen='r', symbol='o', symbolPen='r', symbolBrush='r')

        # Add data properties to plot objects to store data
        self.stats.data = []

        # Button for initiating sockets with Mantis
        self.commsButton = QtWidgets.QPushButton('Start Mantis Comms', self)
        self.commsButton.clicked.connect(self.startPlot)

        # UI layout
        self.layout = QtGui.QGridLayout()
        self.w.setLayout(self.layout)
        self.layout.addWidget(self.plotWidget)
        self.layout.addWidget(self.plotWidget2)
        self.layout.addWidget(self.commsButton)
        self.w.show()

        # Ininiate the thread pool
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    @pyqtSlot()
    def startPlot(self):
        '''
        Slot for sockets the initiation button
        '''
        worker = Worker(mantisComms, plotLiveData, [self.trace, self.stats])
        self.threadpool.start(worker)
        print('push')

    def testFunc(self):
        print("test")


app = QtWidgets.QApplication(sys.argv)
plot = LivePlot()
sys.exit(app.exec_())
