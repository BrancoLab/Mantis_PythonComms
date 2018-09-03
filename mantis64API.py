import socket
import numpy as np

def mantisComms(func, traceObjects):
    '''
    Basic function for setting up socket communication between Mantis and
    Python. Python acts as server so the function has to be called before
    initiating the Mantis experiment.

    :param func: function callback for processing data chunks
    :param traceObjects: pyqygraph plot objects passed from plotUI for
                         plotting data
    '''

    # Hardcoded information about the data received. Useful for
    # reconstructing sweeps from the data chunks
    # TODO: read this info from Mantis
    chunkSize = 50
    sweepSize = int(0.5*25000/10)
    sweepArray = np.zeros(sweepSize)
    sweepInfo = [chunkSize, sweepSize, sweepArray]
    chunkCounter=0

    # Setup sockets
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8079))
    server.listen(1)
    conn, addr = server.accept() # use the same TCP/IP refnum for the experiment
    print("Mantis comms started")

    # Main loop
    while True:
        # 1st TCP packet: The default 16byte Mantis header  ACTION/CHID/DATASIZE/ e.g @INIT@001@00353@
        cmnd = conn.recv(16)
        # convert 'command' type to a normal python string
        MantisHeader=str(cmnd)
        # all strings from Mantis are @ separated so we make it a list
        Header_list = MantisHeader.split('@')
        # delete first dummy element before first @ python autoappends characters here
        #Header_list.pop()
        # delete last dummy element after last @  python autoappends characters here too
        #Header_list.pop(0)
        # the first element is the action to be performed on the data
        action= Header_list[1]
        # the second element indicates the channel number that is transmitted
        ch_id= Header_list[2]
        # the third header element indicates the size of data for the next packet
        size=Header_list[3]
        size=float(size)
        size=int(size)
        #print(size)
        conn.sendall(b'size')

        # 2nd TCP packet: wait to read the exact length of data that the Mantis Header indicated
        cmnd =conn.recv(size)

        # actions
        # Do the initialization action by parsing the command send by Mantis each time an experiment starts
        if 'INIT' in str(action):

             # delete the 'INIT' tag from the list- this list contains all the initialization data
             #Header_list.pop(0)
             # assume the first element in the list is the sampling frequency and so on
             #fs=Header_list[0]
             #fs=float(fs)
             #print(fs)
             conn.sendall(b'INIT ok.')  # feedback to Mantis that the initialization was successful

        # Do the lay action
        elif 'PLAY' in str(cmnd):
            conn.sendall(cmnd)

        # Do the quit action
        elif 'QUIT' in str(cmnd):
            conn.sendall(b'QUIT ok.')
            break

        # The data sent by Mantis in runtime has the prefix 'DATA'
        elif 'DATA' in str(action):
            MantisData=str(cmnd)
            Mantis_list = MantisData.split('@')
            # delete the 'DATA' prefix from the list to cast to nparray
            Mantis_list.pop(0)
            Mantis_list.pop()
            array = np.asarray(Mantis_list)
            # convert to float nparray for online analysis
            array = array.astype(np.float)

            # Keep track of chuncks received to build sweeps
            if chunkCounter<(sweepSize-chunkSize):
                chunkCounter+=chunkSize
            else:
                chunkCounter=0

            # call function for data processing
            func(array, traceObjects, sweepInfo, chunkCounter)

            # TODO: Mantis currently needs to receive something back so we send this
            avg = sum(array)/len(array)
            # returns little endian DBL float 8 byte that Mantis can read and plot
            conn.sendall(avg)
    server.close()
