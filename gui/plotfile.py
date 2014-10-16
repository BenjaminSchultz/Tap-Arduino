

"""
This is for when we have a bunch data from a file,
and we'll plot the lot
"""


import matplotlib.pyplot as plt
import numpy as np
import sys





# Take the filename from the command line
if len(sys.argv)>1:
    filename=sys.argv[1]
else:

    USE_WX=False


    if USE_WX:
    
        import wx
        app = wx.App()

        dialog = wx.FileDialog ( None, style = wx.OPEN )

        # Show the dialog and get user input
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetPath()
            #print 'Selected:', dialog.GetPath()
        else:
            print "Without a file I can't do anything!"
            sys.exit(-1)

        # The user did not select anything
        dialog.Destroy()   


    else:

        from Tkinter import *
        from tkMessageBox import *
        from tkColorChooser import askcolor              
        from tkFileDialog   import askopenfilename      

        filename = askopenfilename() 
        if filename=="":
            print "Without a file I can't do anything!"
            sys.exit(-1)




predt = np.dtype( [ ('t','i'),
                    ('X','i'),
                    ('P','i') ] )
pretab = np.genfromtxt(filename,skip_header=0,dtype=predt)




(shift,multipl)=1.72459584e+02,3.84644971e-04
def cToF( outputs ):
    return ((outputs/multipl)+np.sqrt(shift))**2-shift


def fsrVtoN( val ):
    """
    Here we calculate the force from the volt signal
    in our FSR, assuming that it is set up with a 10kOhm 
    resistance.

    So val is a volts value (0..5V), and we return the force
    in Newton.
    """
    # This is mostly due to http://www.ladyada.net/learn/sensors/fsr.html
    # The voltage = Vcc * R / (R + FSR) where R = 10K and Vcc = 5V
    # so FSR = ((Vcc - V) * R) / V        yay math!
    fsrR = (5.-val)*(10000)/val
    conductance = 1/fsrR # in microohms
 
    # Use the two FSR guide graphs to approximate the force
    return cToF(conductance)






MAX_READ = 1023 # Arduino can read between 0 and 1023 (voltage read)
VOLTAGE_REF = 5. # Voltage Reference

ACC_POWER_SUPPLY = 3.3 # What we feed to the accelerometer

#ACC_ZERO_BIAS = 1.5 # According to the spec sheet
#ACC_SENSITIVITY = .3 # 300mV/g 

ACC_ZERO_BIAS   = 1.722896  # From our calibration (calibrate.py)
ACC_SENSITIVITY = 0.320187  # From our calibration (calibrate.py)

G = 9.81 # m/sec**2


# Two correction factors to get real g's
#MCORR,PCORR = (4/3.),1.25

dt = np.dtype( [ ('T',  'L'), # unsigned long for big-time data
                 ('X',  'f'),
                 ('ax', 'f'),
                 ('P',  'f') ] )

# Ok, now we need to restructure the time values.
# The reason is, our timestamp has been sent as an int (16 bits),
# meaning we can effectively store 2**16microsecs in there,
# which means it will reset quite often. 
# So here we interpolate the whole thing and make a real
# time column in microsecs.
cycle = 0
INT_SIZE = 2**16
tab = []
(startt,_,_)=pretab[0]
prevt = -1
f = open(filename+".clean.txt","w")
for (t,x,p) in pretab:
    if t<prevt:
        cycle+=1
    tup = ((cycle*INT_SIZE)+t-startt,
           (x*VOLTAGE_REF)/MAX_READ,
           G*(((((x*VOLTAGE_REF)/MAX_READ)-ACC_ZERO_BIAS)/ACC_SENSITIVITY)-1),
           fsrVtoN((p*VOLTAGE_REF)/MAX_READ)
           )
    tab.append( tup )
    f.write( "%i %f %f %f\n"% tup )
    prevt = t
tab = np.array( tab, dtype=dt )
f.close()

# The maximum time (since we started at zero this equals the duration)
(maxt,_,_,_) = tab[-1]


print
print "Time recorded : %i microsec"%(maxt)
print "Items captured: %i, framerate according to arduino= %.3f/sec"%(
    len(tab['T']),(10.**6)*len(tab['T'])/(maxt))
print
print


ax = plt.subplot(2,1,1)
plt.plot( tab['T']/(10.**6), tab['ax'], linewidth=1, alpha=.8, color="blue" )
plt.title("Acceleration")
plt.ylabel("upward acceleration (m/sec^2)")
plt.ylim(-3*G,3*G)
plt.axhline(y=0,color="gray",linewidth=1)
#plt.ylim(0,VOLTAGE_REF)
plt.subplot(2,1,2, sharex=ax)
plt.plot( tab['T']/(10.**6), tab['P'], linewidth=1, alpha=.8, color="red"  )
plt.ylim(0,max(tab['P']))
plt.title("Pressure")
plt.xlabel("time (s)")
plt.ylabel("force (g)")
plt.show()
