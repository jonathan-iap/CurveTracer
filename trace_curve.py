
import sys, serial, argparse
import numpy as np
from time import sleep
from collections import deque

import matplotlib.pyplot as plt 
import matplotlib.animation as animation
INTERVAL = 10
SPAN = 500
    
# plot class
class AnalogPlot:
    def __init__(self, strPort, maxLen):
        # open serial port
        self.ser = serial.Serial(strPort, 9600)
        self.val = deque([0.0]*maxLen)
        self.lowpass = deque([0.0]*maxLen)
        self.kalman = deque([0.0]*maxLen)
        self.maxLen = maxLen

    # add to buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # add data
    def add(self, data):
        self.addToBuf(self.val, data[0])
        self.addToBuf(self.lowpass, data[1])
        self.addToBuf(self.kalman, data[2])
    
    # update plot
    def update(self, frameNum, a0, a1, a2):
        try:
            line = self.ser.readline()
            try:
                data = [float(val) for val in line.split()]
            except ValueError:
                return
            if not len(data) == 3:
                return
            self.add(data)
            a0.set_data(range(self.maxLen), self.val)
            a1.set_data(range(self.maxLen), self.lowpass)
            a2.set_data(range(self.maxLen), self.kalman)
        
        except KeyboardInterrupt:
            print('exiting')
        return a0, a1, a2 

    # clean up
    def close(self):
        # close serial
        self.ser.flush()
        self.ser.close()    

# main() function
def main():
    strPort = '/dev/ttyACM1'
    # strPort = args.port

    print('reading from serial port %s...' % strPort)

    # plot parameters
    analogPlot = AnalogPlot(strPort, SPAN)

    print('plotting data...')

    # set up animation
    fig = plt.figure()
    ax = plt.axes(xlim=(0, SPAN), ylim=(3100, 3300))
    a0, = ax.plot([], [], 'k-', label='Raw')
    a1, = ax.plot([], [], 'g-', label='Low pass')
    a2, = ax.plot([], [], 'b-', label='Kalman')
    ax.legend()
    anim = animation.FuncAnimation(fig, analogPlot.update, 
                                   fargs=(a0, a1, a2), 
                                   interval=INTERVAL)

    # show plot
    plt.show()
  
    # clean up
    analogPlot.close()

    print('exiting.')

if __name__ == '__main__':
    main()
