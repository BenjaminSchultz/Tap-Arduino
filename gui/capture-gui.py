#$Id: entryfield.py,v 1.2 2004/03/17 04:29:31 mandava Exp $
#this is a program depicting the use of entry field widget.
#entry widgets are basic widgets used to collect input from the user.
#entry widgets are limited to a single line of text which can be in only
#one font. 
#the root is also packed with 4 buttons along with the entry widget..
import threading

import Tkinter 
import tkFileDialog
from Tkinter import *
from tkFileDialog import asksaveasfilename
root =Tk()
root.title('iMMMotion Capture')

from FileDialog import LoadFileDialog, SaveFileDialog

#import wx


#
# This looks also really useful:
# http://balau82.wordpress.com/2011/03/26/capturing-an-analog-signal-with-arduino-and-python/
#


#
# Ok, so arduino is sending in blocks of 8 bytes:
#      byte1    byte2&3   byte4&5    byte6&7     byte8
#       "B"       int       int         int       "E"
#     'begin'    t(ms)    X-accel    Pressure    'end'
#

import sys
import serial, time
#baudrate = 115200 # the maximum for arduino
baudrate = 1000000 # the maximum for arduino


import preview as previewer # for making a preview from captured data


# Making a bunch of variables
usbS = StringVar()
usbS.set("/dev/ttyACM0")
fileS = StringVar()
fileS.set("")

keepGoingB = BooleanVar()


PACKET_LENGTH = 12




class Reporter:

    def __init__(self):
        self.thread = None

    
    def report(self,message):
        self.text.insert(END,message)

    def settextreceiver(self,textreceiver):
        self.text = textreceiver

    def startNew(self):
        # Clear the text field
        self.text.delete(1.0, END)



reporter = Reporter()




def askSaveFile():
    # Asks where to save the file

    #from FileDialog import LoadFileDialog, SaveFileDialog
    #rt = Tk()
    #fd = SaveFileDialog(rt)
    #filename = fileS.get()
    #filename = fd.go(default=filename)

    filename = asksaveasfilename(parent=root,
                                 defaultextension=".txt",
                                 initialfile=fileS.get(),
                                 filetypes=[("text files","*.txt"),
                                            ("all files","*")])

    if filename:
        fileS.set(filename)
        reporter.captureB.configure( state=NORMAL,
                                     bg="darkgreen" )

    """
    app = wx.App()

    dialog = wx.FileDialog ( None, style = wx.SAVE )

    # Show the dialog and get user input
    if dialog.ShowModal() == wx.ID_OK:
        filename = dialog.GetPath()
        #print 'Selected:', dialog.GetPath()
        
        fileS.set(filename) # update the filename variable
        reporter.captureB.configure( state=NORMAL,
                                     bg="darkgreen" )

    # The user did not select anything
    dialog.Destroy()   
    """
    


        


def stopCapture():
    keepGoingB.set(False)
    reporter.report("Capture stopped.\n\n")
    reporter.thread=None




def runcapture():
        

    # Start up the serial communication
    commport = usbS.get()

    try:
        comm = serial.Serial(commport, baudrate, timeout=0.25)
    except:
        reporter.report("Cannot open USB port %s. Is the device connected?\n"%commport)
        stopCapture()
        return -1

    filename = fileS.get() # get the filename we are supposed to output to

    if len(filename)==0:
        reporter.report("Please select an output file.\n")
        stopCapture()
        return -1

        
    dumpfile = open(filename,'w')

    do_continue=True
    keepGoingB.set(do_continue)
    reporter.report("Starting capture (%s)\n"%filename)

    i=0
    while do_continue:

        # Ok, let's read something
        r = comm.read(1)

        if r=="B": # This could be the beginning of a signal

            avail=0 # how many bytes are available
            while avail<PACKET_LENGTH: # we need at least 7 bytes
                avail=comm.inWaiting()

            # all right, now we can read
            r = comm.read(PACKET_LENGTH) # read the whole thing straight away


            # Now continue to work with this
            if len(r)==PACKET_LENGTH and r[-1]=="E": # if we have the correct ending also

                b1 = ord(r[0])+256*ord(r[1])
                b2 = ord(r[2])+256*ord(r[3])
                b3 = ord(r[4])+256*ord(r[5])
                b4 = ord(r[6])+256*ord(r[7])
                b5 = ord(r[8])+256*ord(r[9])
                b6 = r[10]

                #print b1,b2
                output = "%i %i %i %i %i %s\n"%(b1,b2,b3,b4,b5,b6)
                dumpfile.write(output)


                # Occasionally give a bleep so the user knows
                # we're still working
                i+=1
                if i>5000:
                    reporter.report(output+"\n")
                    do_continue = keepGoingB.get()
                    i=0

            else:
                if len(r)>0:
                    reporter.report("rejected")


    # Update which button is enabled etc.
    reporter.previewB.configure(state=NORMAL,background="yellow")
    reporter.stopB.configure(state=DISABLED,background="gray")






def doCapture():

    if reporter.thread!=None:
        reporter.report("Already running!\n")
        return -1

    reporter.startNew()
    reporter.stopB.configure(state=NORMAL,background="red")
    reporter.captureB.configure(state=DISABLED,background="gray")
    reporter.thread = threading.Thread(target=runcapture)
    print ("Starting capture")
    reporter.thread.start()



    

def preview():
    # Here we give a preview of the file we just captured
    
    filename = fileS.get() # get the filename we are supposed to output to
    if len(filename)==0:
        reporter.report("No output file selected.\n")
        return -1

    
    thread = threading.Thread(target=previewer.show, args=(filename,reporter))
    thread.start()
    #thread.join()

    







usbF = Frame(root)
Label (usbF,text='usb port').pack(side=LEFT,padx=10,pady=10)
usbEntry = Entry (usbF,width=30,textvariable=usbS)
#usbEntry = Frame (usbF,background="red")
usbEntry.pack(expand=True,side=LEFT,padx=10,pady=10,fill=BOTH)
#Label (usbEntry,text="this will expand?").pack(side=LEFT,padx=10,pady=10,fill=BOTH)
#usbEntry.pack(side=LEFT,padx=10,pady=10,fill=BOTH)
usbF.pack(side=TOP,padx=10,fill=X)



fileF = Frame(root)
Label (fileF,text='save to file').pack(side=LEFT,padx=10)
fileEntry = Entry (fileF,width=30,textvariable=fileS)
fileEntry.pack(side=LEFT,expand=True,padx=10,pady=10,fill=X)
fileB = Button(fileF,text="select",command=askSaveFile)
fileB.pack(side=RIGHT,padx=10,pady=10)
fileF.pack(padx=10,pady=0,fill=X)



reportF = Frame(root)
s       = Scrollbar(reportF)
reportT = Text(reportF,height=8,width=8)
reporter.settextreceiver(reportT)
reportT.pack(side=LEFT, padx=5, pady=5,fill=BOTH,expand=True)
s.pack(side=RIGHT,fill=Y)
s.config(command=reportT.yview)
reportT.config(yscrollcommand=s.set)               
reportF.pack(side=TOP,fill=BOTH,expand=True)

#for i in range(80): 
#   reportT.insert(END, "This is line %d\n" % i)


buttonF = Frame(root)
captureB = Button(buttonF, text='capture', command=doCapture, background="darkgreen" )
captureB.configure(state=DISABLED,background="darkgray")
captureB.pack(side=LEFT,padx=10,pady=10)
stopB = Button(buttonF, text='stop', command=stopCapture, background="red" )
stopB.pack(side=LEFT,padx=10,pady=10)
previewB = Button(buttonF, text='preview', command=preview)
previewB.pack(side=LEFT,padx=10,pady=10)
buttonF.pack(side=BOTTOM,padx=10,pady=10)
previewB.configure(state=DISABLED,background="darkgray")
stopB.configure(state=DISABLED,background="darkgray")

reporter.stopB    = stopB
reporter.captureB = captureB
reporter.previewB = previewB




root.geometry("500x600")

root.mainloop()
