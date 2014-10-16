

"""
This is for when we have a bunch data from a file,
and we'll plot the lot
"""


import matplotlib.pyplot as plt
import numpy as np
import sys





def show(filename,reporter):


    # First read in the raw data
    predt = np.dtype( [ ('T','i'), ('P','i'), ('X','i'), ('Y','i'), ('Z','i'), ('M','i') ] )
    pretab = np.genfromtxt(filename,skip_header=0,dtype=predt)

    # Then we need to transform the time column, since
    # we run in cycles of 2**16 microsec.
    cycle = 0
    INT_SIZE = 2**16
    tab = []
    startt=pretab["T"][0]
    prevt = -1
    i = 0

    for x in pretab:
        (t,z,p,m)=(x['T'],x['Z'],x['P'],x['M'])
        if t<prevt:
            cycle+=1
        if (i%10)==0: # downsample so that it's faster
            tup = ((cycle*INT_SIZE)+t-startt,p,z,m)
            tab.append( tup )
        prevt = t
        i+=1
    tab = np.array( tab, dtype=np.dtype( [ ('T','L'), ('P','i'), ('Z','i'), ('M','i') ] ) )
    maxt = tab["T"][-1]



    #
    # Show a report of how much data we captured, etc.
    #
    reporter.report("\n")
    reporter.report("Time recorded: %i microsec\n"%(maxt))
    reporter.report("Items captured: %i, framerate according to arduino= %.3f/sec\n"%(
        len(pretab['T']),(10.**6)*len(pretab['T'])/(maxt)))
    reporter.report("\n")
    reporter.report("\n")
 

    
    #
    # 
    #
    ax = plt.subplot(3,1,1)
    plt.plot( tab['T']/(10.**6), tab['Z'], linewidth=1, alpha=1, color="blue" )
    plt.title("Acceleration -- downsampled")
    plt.ylabel("upward acceleration (g)")
    plt.axhline(y=0,color="gray",linewidth=1)
    #plt.ylim(0,VOLTAGE_REF)
    plt.subplot(3,1,2, sharex=ax)
    plt.plot( tab['T']/(10.**6), tab['P'], linewidth=1, alpha=1, color="red"  )
    plt.ylim(0,max(tab['P']))
    plt.title("Pressure -- downsampled")
    plt.xlabel("time (s)")
    plt.ylabel("force (no unit)")

    plt.subplot(3,1,3, sharex=ax)
    plt.plot( tab['T']/(10.**6), tab['M'], linewidth=1, alpha=1, color="purple"  )
    plt.title("Metronome")
    plt.xlabel("time (s)")
    plt.ylabel("signal (on/off)")
    plt.show()






def showTransformed(filename,reporter):


    predt = np.dtype( [ ('T','i'), 
                        ('P','i'),
                        ('X','i'),
                        ('Y','i'),
                        ('Z','i'),
                        ('M','i')
                        ] )
    pretab = np.genfromtxt(filename,skip_header=0,dtype=predt)

   
    dt = np.dtype( [ ('T',  'L'), # unsigned long for big-time data
                     ('X',  'f'),
                     ('P',  'f') ] )

    # Ok, now we need to restructure the time values.
    # The reason is, our timestamp has been sent as an int (16 bits),
    # meaning we can effectively store 2**16microsecs in there,
    # which means it will reset quite often. 
    # So here we interpolate the whole thing and make a real
    # time column in microsecs.
    MAX_READ = 1023 # Arduino can read between 0 and 1023 (voltage read)
    VOLTAGE_REF = 5. # Voltage Reference
    

    ACC_ZERO_BIAS   = 1.722896  # From our calibration (calibrate.py)
    ACC_SENSITIVITY = 0.320187  # From our calibration (calibrate.py)


    cycle = 0
    INT_SIZE = 2**16
    tab = []
    startt=pretab["T"][0]
    prevt = -1
    i = 0
    for (t,x,p) in pretab:
        if t<prevt:
            cycle+=1
        if (i%100)==0: # downsample so that it's faster
            tup = ((cycle*INT_SIZE)+t-startt,
                   (((((x*VOLTAGE_REF)/MAX_READ)-ACC_ZERO_BIAS)/ACC_SENSITIVITY)-1),
                   (p*VOLTAGE_REF)/MAX_READ
                   )
            tab.append( tup )
        prevt = t
        i+=1
    tab = np.array( tab, dtype=dt )

    # The maximum time (since we started at zero this equals the duration)
    maxt = tab["T"][-1]


    reporter.report("\n")
    reporter.report("Time recorded: %i microsec\n"%(maxt))
    reporter.report("Items captured: %i, framerate according to arduino= %.3f/sec\n"%(
        len(pretab['t']),(10.**6)*len(pretab['t'])/(maxt)))
    reporter.report("\n")
    reporter.report("\n")


    ax = plt.subplot(2,1,1)
    plt.plot( tab['T']/(10.**6), tab['X'], linewidth=1, alpha=1, color="blue" )
    plt.title("Acceleration -- downsampled")
    plt.ylabel("upward acceleration (g)")
    plt.ylim(-3,3)
    plt.axhline(y=0,color="gray",linewidth=1)
    #plt.ylim(0,VOLTAGE_REF)
    plt.subplot(2,1,2, sharex=ax)
    plt.plot( tab['T']/(10.**6), tab['P'], linewidth=1, alpha=1, color="red"  )
    plt.ylim(0,max(tab['P']))
    plt.title("Pressure -- downsampled")
    plt.xlabel("time (s)")
    plt.ylabel("force (no unit)")
    plt.show()
