#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#### IMPORTING LIBRARIES ####
import tkinter as tk
from tkinter import filedialog
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import scipy.io
import pandas as pd
from scipy.signal import chirp, spectrogram, find_peaks
from scipy import interpolate
from scipy.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D

#Main Window of the GUI
window = tk.Tk()
window.title("Reverb Calibration")
window.geometry('900x550')

#Frames Declaration & Placement
frame1 = tk.Frame(window, height = 405, width = 250, borderwidth=2)
frame1.place(x=0, y=100)

#Labels, Entry's & checkboxes Declaration & Placement
lbl_kpd = tk.Label(window, text="Known Position Devices:")
lbl_upd = tk.Label(window, text="Unknown Position Devices:")
lbl_kpd_file = tk.Label(window, text="Known Devices File")
lbl_fs = tk.Label(window, text="Sampling Frequency:", wraplength=100, justify="left")
lbl_hz = tk.Label(window, text="Hz")
lbl_room_x = tk.Label(window, text="X:       meters")
lbl_room_y = tk.Label(window, text="Y:        meters")
lbl_room_z = tk.Label(window, text="Z:        meters")
r_x_txt = tk.Entry(window,width=2)
r_y_txt = tk.Entry(window,width=2)
r_z_txt = tk.Entry(window,width=2)
lbl_delta_cal = tk.Label(window) 
lbl_rir={}
lbl_rir_loc={}
kpd_txt = tk.Entry(window,width=5)
upd_txt = tk.Entry(window,width=5)
fs_txt = tk.Entry(window, width=6)
dly_checkbox_fun = tk.IntVar()
dly_checkbox= tk.Checkbutton(window, text = "Activate Delay", 
                      variable = dly_checkbox_fun,
                      onvalue = 1,
                      offvalue = 0,
                      height = 4,
                      width = 10)
lbl_kpd.place(x=0, y=10)
lbl_upd.place(x=0, y=40)
kpd_txt.place(x=180, y=10)
upd_txt.place(x=180, y=40)
dly_checkbox.place_forget()
lbl_fs.place_forget()
lbl_hz.place_forget()
lbl_kpd_file.place_forget()
#lbl_delta_cal.place_forget()
fs_txt.place_forget()
lbl_room_x.place(x=500,y=23)
lbl_room_y.place(x=640,y=23)
lbl_room_z.place(x=780,y=23)
r_x_txt.place(x=515,y=23)
r_y_txt.place(x=655,y=23)
r_z_txt.place(x=795,y=23)


#Function for choosing between 2-dimension or 3-dimension (GUI function)
def dimension():
    print(var_dim.get())
    if var_dim.get() == 1:
        r_z_txt['state'] = tk.DISABLED
        lbl_room_z.place_forget()
        r_z_txt.place_forget()
    else:
        r_z_txt['state'] = tk.NORMAL
        lbl_room_z.place(x=780,y=23)
        r_z_txt.place(x=795,y=23) 
var_dim = tk.IntVar()
checkbox_2d= tk.Checkbutton(window, text = "Select 2D Room Bounds", 
                  command = dimension,
                  variable = var_dim,
                  onvalue = 1,
                  offvalue = 0,
                  height = 2,
                  width = 20)
checkbox_2d.place(x=600, y=43)


#Declaration of variables 
global RIRlen
c = 343; #Sound velocity
RIRlen = 1332; #Size of the RIR's

#### Declaration of functions ####

#Function to open a file with a RIR (GUI function)
def open_file(i):
    dd = {}
    dd["filename{0}".format(i)] = filedialog.askopenfilename()
    load_rir(dd["filename{0}".format(i)],i)
    print(dd)

#Function to load each RIR to the main RIR matrix (GUI function)
def load_rir(rir,n):    
    file = pd.read_excel(io=rir)
    file = np.asarray(file)
    data[n*RIRlen:n*RIRlen + RIRlen, :] = file[0:RIRlen,:]

#Function to load the known positions of the devices (GUI function)
def open_file2():
    kpd_file = filedialog.askopenfilename()
    global KnownPos
    KnownPos = np.asarray(pd.read_excel(io=kpd_file))
    print(KnownPos)

#Function to enable the rest of the functions and to initialize variables (GUI function)
def load():   
    x = int(upd_txt.get())
    lbl_fs.place(x=0, y=470)
    lbl_hz.place(x=142, y=483)
    lbl_kpd_file.place(x=0,y=80)
    btn_kpd_file.place(x=130, y=78)
    fs_txt.place(x=80, y=480)
    dly_checkbox.place(x=500, y=480)
    btn_cal.place(x=600, y=500)
    btn_load['state'] = tk.DISABLED
    upd_txt['state'] = tk.DISABLED
    kpd_txt['state'] = tk.DISABLED
    btn_dlt['state'] = tk.NORMAL
    btn_cal['state'] = tk.NORMAL
    btn_kpd_file['state'] = tk.NORMAL
    fs_txt['state'] = tk.NORMAL
    dly_checkbox['state'] = tk.NORMAL
    btn_ok_dim['state'] = tk.NORMAL
    checkbox_2d['state'] = tk.NORMAL
    r_x_txt['state'] = tk.NORMAL
    r_y_txt['state'] = tk.NORMAL
    r_z_txt['state'] = tk.NORMAL
    
    #Matrix of zeros to fill with RIR's and bounds of room
    global data            #Main matrix composed by RIR's
    global bounds2D_nodel  #Matrix for bounds for the optimization problem in 2-dimensions and without delay estimation
    global bounds2D_del    #Matrix for bounds for the optimization problem in 2-dimensions and with delay estimation
    global bounds3D_nodel  #Matrix for bounds for the optimization problem in 3-dimensions and without delay estimation
    global bounds3D_del    #Matrix for bounds for the optimization problem in 3-dimensions and with delay estimation
    data = np.zeros(shape=(RIRlen*int(upd_txt.get()),int(kpd_txt.get())))
    bounds2D_nodel = np.zeros(shape=(int(upd_txt.get())*2, 2)) 
    bounds2D_del = np.zeros(shape=(int(upd_txt.get())*2 + 1,2))
    bounds3D_nodel = np.zeros(shape=(int(upd_txt.get())*3,2))
    bounds3D_del = np.zeros(shape=(int(upd_txt.get())*3 + 1,2))
    
    for m in range(0, x):
        lbl_rir[m] = tk.Label(frame1, text = "#"+str(m)+" Device RIR")
        lbl_rir[m].place(x=0, y=10+(m*25))
        btn_rir[m] = tk.Button(frame1, text="Open", command=lambda i=m :open_file(i))
        btn_rir[m].place(x=100, y=5+(m*25))

#Function that resets the GUI to the beginning to compute again the estimation positions (GUI function)
def reset():   
    lbl_kpd_file.place_forget()
    btn_kpd_file.place_forget()
    #if 'lbl_delta_cal' in locals():
    lbl_delta_cal.place_forget()
    #canvas_fig.get_tk_widget().place_forget()
    btn_load['state'] = tk.NORMAL
    upd_txt['state'] = tk.NORMAL
    kpd_txt['state'] = tk.NORMAL
    btn_dlt['state'] = tk.DISABLED
    btn_cal['state'] = tk.DISABLED
    btn_kpd_file['state'] = tk.DISABLED
    dly_checkbox['state'] = tk.DISABLED
    fs_txt['state'] = tk.DISABLED
    btn_ok_dim['state'] = tk.DISABLED
    checkbox_2d['state'] = tk.DISABLED
    r_x_txt['state'] = tk.DISABLED
    r_y_txt['state'] = tk.DISABLED
    r_z_txt['state'] = tk.DISABLED
    
    x = int(upd_txt.get())
    for m in range(0, x):
        lbl_rir[m].destroy()
        btn_rir[m].destroy()
        lbl_rir_loc[m].destroy()
        
        
#Function for finding the direct path of the RIR's (Calibration function)
def find_directPath(this_rir, top_peaks=15):
    this_rir = np.abs(this_rir)     #It computes the absolute value of the RIR to avoid that the first peak is negative
    peaks, _ = find_peaks(this_rir)
    nHighest = (this_rir[peaks]).argsort()[::-1][:top_peaks]
    dp = np.sort((peaks[nHighest]))[:1]
    return dp

#Function to compute the distance between two devices through RIR's measurement (Calibration function)
def compute_distance(audio,fs,c,interp_factor = 2, do_interpolation = True):
    distance = np.zeros(shape=(audio.shape[1]))
    interp_factor = interp_factor
    do_interpolation = do_interpolation
    for m in range(0,audio.shape[1]):
        if do_interpolation:
            this_rir = audio[:,m]
            sample_ax = np.arange(0, this_rir.shape[0])
            f = interpolate.interp1d(sample_ax, this_rir, kind='quadratic')
            sample_ax_new = np.arange(0, this_rir.shape[0] - 1, 1/interp_factor)
            dp = find_directPath(f(sample_ax_new))
        else:
            this_rir = abs(audio[:,m])
            dp = find_directPath(this_rir)
        distance[m] = (dp/interp_factor)*(1/fs) * c
    return distance


#### FUNCTIONS OF CALIBRATION ACCORDING TO 2D/3D ####

#Function to estimate the position of the unkown devices in 2D and without delay estimation (Calibration function)
def calibration2D_nodel(audio, fs, PosKnown, c, bnds, nUnknown):
    #Initialization of the vector of initial values for the minimization search
    ini = np.zeros(shape=(nUnknown * 2))
    
    #Function that compute the minimization method
    def fun2D_nodel(x1):
        P = np.zeros(shape=(nUnknown,audio.shape[1]))
        D = np.zeros(shape=(nUnknown,audio.shape[1]))
        distance = np.zeros(shape=(nUnknown,audio.shape[1]))
        
        #Computing the distance with the RIR's measurements and filling the matrices
        counter = 0
        for j in range(0,nUnknown):
            distance[j] = compute_distance(audio[j*RIRlen:j*RIRlen + RIRlen - 1,:], fs, c)
            for i in range(0, audio.shape[1]):
                P[j,i] = (np.sqrt(abs(x1[counter] - PosKnown[i][0])**2 + abs(x1[counter + 1] - PosKnown[i][1])**2))
                D[j,i] = distance[j,i];
            counter = counter + 2

        return sum(sum((P - D )**2));
    
    #Minimization algorithm
    resM = minimize(fun2D_nodel, ini, method='SLSQP', bounds=bnds)
    
    #Printing the results in console log
    counter = 0
    for n in range(0,nUnknown):
            print('Source ',n ,': \n','X: ', resM.x[counter], '[m]', 'Y: ', resM.x[counter + 1], '[m]\n')
            counter = counter + 2
    return resM.x

#Function to estimate the position of the unkown devices in 2D and with delay estimation (Calibration function)
def calibration2D_del(audio, fs, PosKnown, c, bnds,nUnknown):
    #Initialization of the vector of initial values for the minimization search
    ini = np.zeros(shape=(nUnknown * 2 + 1))
    
    #Function that compute the minimization method
    def fun2D_del(x1):
        P = np.zeros(shape=(nUnknown,audio.shape[1]))
        D = np.zeros(shape=(nUnknown,audio.shape[1]))
        T = np.zeros(shape=(nUnknown,audio.shape[1]));
        distance = np.zeros(shape=(nUnknown,audio.shape[1]))
        
        #Computing the distance with the RIR's measurements and filling the matrices
        counter = 0
        for j in range(0,nUnknown):
            distance[j] = compute_distance(audio[j*RIRlen:j*RIRlen + RIRlen - 1,:], fs, c)
            for i in range(0, audio.shape[1]):
                P[j,i] = (np.sqrt(abs(x1[counter] - PosKnown[i][0])**2 + abs(x1[counter + 1] - PosKnown[i][1])**2))
                D[j,i] = distance[j,i];
                T[j,i] = x1[nUnknown*2]*c
            counter = counter + 2

        return sum(sum((P - (D - T)) **2));
    
    #Minimization algorithm
    resM = minimize(fun2D_del, ini, method='SLSQP', bounds=bnds)
    
    #Printing the results in console log
    counter = 0
    for n in range(0,nUnknown):
            print('Source ',n ,': \n','X: ', resM.x[counter], '[m]', 'Y: ', resM.x[counter + 1], '[m]\n')
            counter = counter + 2
    print('Delta :',resM.x[nUnknown *2], '[s]')
    return resM.x

#Function to estimate the position of the unkown devices in 3D and without delay estimation (Calibration function)
def calibration3D_nodel(audio, fs, PosKnown, c, bnds,nUnknown):
    #Initialization of the vector of initial values for the minimization search
    ini = np.zeros(shape=(nUnknown * 3))
    
    #Function that compute the minimization method
    def fun3D_nodel(x1):
        P = np.zeros(shape=(nUnknown,audio.shape[1]))
        D = np.zeros(shape=(nUnknown,audio.shape[1]))
        distance = np.zeros(shape=(nUnknown,audio.shape[1]))
        
        #Computing the distance with the RIR's measurements and filling the matrices
        counter = 0
        for j in range(0,nUnknown):
            distance[j] = compute_distance(audio[j*RIRlen:j*RIRlen + RIRlen - 1,:], fs, c)
            for i in range(0, audio.shape[1]):
                P[j,i] = (np.sqrt(abs(x1[counter] - PosKnown[i][0])**2 + abs(x1[counter + 1] - PosKnown[i][1])**2 + abs(x1[counter + 2] - PosKnown[i][2])**2))
                D[j,i] = distance[j,i];
            counter = counter + 3

        return sum(sum((P - D) **2));
    
    #Minimization algorithm
    resM = minimize(fun3D_nodel, ini, method='SLSQP', bounds=bnds)
    
    #Printing the results in console log
    counter = 0
    for n in range(0,nUnknown):
            print('Source ',n ,': \n','X: ', resM.x[counter], '[m]', 'Y: ', resM.x[counter + 1], '[m]', 'Z: ', resM.x[counter + 2], '[m]\n')
            counter = counter + 3
    return resM.x      

#Function to estimate the position of the unkown devices in 3D and with delay estimation (Calibration function)
def calibration3D_del(audio, fs, PosKnown, c, bnds,nUnknown):
    #Initialization of the vector of initial values for the minimization search
    ini = np.zeros(shape=(nUnknown * 3 + 1))
    
    #Function that compute the minimization method
    def fun3D_del(x1):
        #Initializing the matrix with zeroes
        P = np.zeros(shape=(nUnknown,audio.shape[1]))
        D = np.zeros(shape=(nUnknown,audio.shape[1]))
        T = np.zeros(shape=(nUnknown,audio.shape[1]));
        distance = np.zeros(shape=(nUnknown,audio.shape[1]))
        
        #Computing the distance with the RIR's measurements and filling the matrices
        counter = 0
        for j in range(0,nUnknown):
            distance[j] = compute_distance(audio[j*RIRlen:j*RIRlen + RIRlen - 1,:], fs, c)
            for i in range(0, audio.shape[1]):
                P[j,i] = (np.sqrt(abs(x1[counter] - PosKnown[i][0])**2 + abs(x1[counter + 1] - PosKnown[i][1])**2 + abs(x1[counter + 2] - PosKnown[i][2])**2))
                D[j,i] = distance[j,i];
                T[j,i] = x1[nUnknown*3]*c
            counter = counter + 3
            
        return sum(sum((P - (D - T)) **2));
    
    #Minimization algorithm
    resM = minimize(fun3D_del, ini, method='SLSQP', bounds=bnds)
    
    #Printing the results in console log
    counter = 0
    for n in range(0,nUnknown):
            print('Source ',n ,': \n','X: ', resM.x[counter], '[m]', 'Y: ', resM.x[counter + 1], '[m]', 'Z: ', resM.x[counter + 2], '[m]\n')
            counter = counter + 3
    print('Delta :',resM.x[nUnknown *3], '[s]')
    return resM.x


#Function to compute the estimation position in 2D/3D and with/without estimation delay (GUI function)
def calculate ():
    #Number of unknown positions
    upd = int(upd_txt.get())
    #Arrays of zeroes for the plots
    x = np.zeros(shape=(upd))
    y = np.zeros(shape=(upd))
    z = np.zeros(shape=(upd))
    
    #If we are in a 3D case with estimation delay:
    if (var_dim.get() == 0 and dly_checkbox_fun.get() == 1):
        #Postion estimation
        pos_3Ddel = calibration3D_del(audio = data,fs = int(fs_txt.get()), PosKnown = KnownPos ,c = c,bnds = bounds3D_del,nUnknown = int(upd_txt.get()))
        
        #Setting the text labels that show the estimated positions and the estimated delay
        counter = 0;
        for m in range(0, upd):
            lbl_rir_loc[m] = tk.Label(window, text = "#"+str(m)+" Device Location: "+"     X: "+ str(round(pos_3Ddel[counter],3))+'     Y: '+str(round(pos_3Ddel[counter + 1],3))+'    Z: '+ str(round(pos_3Ddel[counter + 2],3)))
            lbl_rir_loc[m].place(x=195, y=115+(m*25))
            counter = counter + 3
        lbl_delta_cal = tk.Label(window, text="Estimated Delta: " + str(round(pos_3Ddel[upd*3],3)))
        lbl_delta_cal.place(x = 500, y = 475)
        
        #Filling the plot vectors with their correspondent coordinates and plotting the result
        counter1 = 0;
        for n in range(0,upd):
            x[n] = pos_3Ddel[counter1]
            y[n] = pos_3Ddel[counter1 + 1]
            z[n] = pos_3Ddel[counter1 + 2]
            counter1 = counter1 + 3
            
        fig = plt.figure(figsize=(4,4))
        ax = Axes3D(fig)
        ax.scatter(x,y,z, marker = 'o')
        ax.grid()
        ax.legend(['No delay']);
    
    #If we are in a 3D case without estimation delay:
    if (var_dim.get() == 0 and dly_checkbox_fun.get() == 0):
        #Postion estimation
        pos_3Dnodel = calibration3D_nodel(audio = data,fs = int(fs_txt.get()), PosKnown = KnownPos ,c = c,bnds = bounds3D_nodel,nUnknown = int(upd_txt.get()))
        
        #Setting the text labels that show the estimated positions
        counter = 0;
        for m in range(0, upd):
            lbl_rir_loc[m] = tk.Label(window, text = "#"+str(m)+" Device Location: "+"     X: "+ str(round(pos_3Dnodel[counter],3))+'     Y: '+str(round(pos_3Dnodel[counter + 1],3))+'    Z: '+ str(round(pos_3Dnodel[counter + 2],3)))
            lbl_rir_loc[m].place(x=195, y=115+(m*25))
            counter = counter + 3
        lbl_delta_cal = tk.Label(window, text="Estimated Delta: None")
        lbl_delta_cal.place(x = 500, y = 475)
        
        #Filling the plot vectors with their correspondent coordinates and plotting the result
        counter1 = 0;
        for n in range(0,upd):
            x[n] = pos_3Dnodel[counter1]
            y[n] = pos_3Dnodel[counter1 + 1]
            z[n] = pos_3Dnodel[counter1 + 2]
            counter1 = counter1 + 3
            
        fig = plt.figure(figsize=(4,4))
        ax = Axes3D(fig)
        ax.scatter(x,y,z, marker = 'o')
        ax.grid()
        ax.legend(['No delay']);
    
    #If we are in a 2D case with estimation delay:
    if (var_dim.get() == 1 and dly_checkbox_fun.get() == 1):
        #Postion estimation
        pos_2Ddel = calibration2D_del(audio = data,fs = int(fs_txt.get()), PosKnown = KnownPos ,c = c,bnds = bounds2D_del,nUnknown = int(upd_txt.get()))
        
        #Setting the text labels that show the estimated positions and the estimated delay
        counter = 0;
        for m in range(0,upd):
            lbl_rir_loc[m] = tk.Label(window, text = "#"+str(m)+" Device Location: "+"     X: "+ str(round(pos_2Ddel[counter],3))+'     Y: '+str(round(pos_2Ddel[counter + 1],3)))
            lbl_rir_loc[m].place(x=195, y=115+(m*25))
            counter = counter + 2
        lbl_delta_cal = tk.Label(window, text="Estimated Delta: " + str(round(pos_2Ddel[upd*2],3)))
        lbl_delta_cal.place(x = 500, y = 475)
        
        #Filling the plot vectors with their correspondent coordinates and plotting the result
        counter1 = 0;
        for n in range(0,upd):
            x[n] = pos_2Ddel[counter1]
            y[n] = pos_2Ddel[counter1 + 1]
            counter1 = counter1 + 2
            
        fig = plt.figure(figsize=(4,4))
        plt.scatter(x, y, marker = 'o')
        plt.title("Estimated position plane xy")
        plt.grid()
        plt.xlabel('x[m]')
        plt.ylabel('y[m]')
        
    #If we are in a 2D case without estimation delay:   
    if (var_dim.get() == 1 and dly_checkbox_fun.get() == 0):
        #Postion estimation
        pos_2Dnodel = calibration2D_nodel(audio = data,fs = int(fs_txt.get()), PosKnown = KnownPos ,c = c,bnds = bounds2D_nodel,nUnknown = int(upd_txt.get()))
        
        #Setting the text labels that show the estimated positions
        counter = 0;
        for m in range(0,upd):
            lbl_rir_loc[m] = tk.Label(window, text = "#"+str(m)+" Device Location: "+"     X: "+ str(round(pos_2Dnodel[counter],3))+'     Y: '+str(round(pos_2Dnodel[counter + 1],3)))
            lbl_rir_loc[m].place(x=195, y=115+(m*25))
            counter = counter + 2
        lbl_delta_cal = tk.Label(window, text="Estimated Delta: None")
        lbl_delta_cal.place(x = 500, y = 475)
        
        #Filling the plot vectors with their correspondent coordinates and plotting the result
        counter1 = 0;
        for n in range(0,upd):
            x[n] = pos_2Dnodel[counter1]
            y[n] = pos_2Dnodel[counter1 + 1]
            counter1 = counter1 + 2
            
        fig = plt.figure(figsize=(4,4))
        plt.scatter(x, y, marker = 'o')
        plt.title("Estimated position plane xy")
        plt.grid()
        plt.xlabel('x[m]')
        plt.ylabel('y[m]')
        
    #Placing the plot
    canvas_fig = FigureCanvasTkAgg(fig, master=window)
    canvas_fig.get_tk_widget().place_forget()
    canvas_fig.draw()
    canvas_fig.get_tk_widget().place(x=500, y=70)   

#Function to fill the bounds vectors (GUI function)
def set_bounds():
    #Setting the bounds arrays.
    for i in range(0,bounds2D_nodel.shape[0],2):
        bounds2D_nodel[i,1] = int(r_x_txt.get())
        bounds2D_del[i,1] = int(r_x_txt.get())
    for j in range(1,bounds2D_nodel.shape[0],2):
        bounds2D_nodel[j,1] = int(r_y_txt.get())
        bounds2D_del[j,1] = int(r_y_txt.get())
    for m in range(0,bounds3D_nodel.shape[0],2):
        bounds3D_nodel[m,1] = int(r_x_txt.get())
        bounds3D_del[m,1] = int(r_x_txt.get())
    for r in range(1,bounds3D_nodel.shape[0],2):
        bounds3D_nodel[r,1] = int(r_y_txt.get())
        bounds3D_del[r,1] = int(r_y_txt.get())
    if (var_dim.get() == 0):     
        for p in range(2,bounds3D_nodel.shape[0],3):
            bounds3D_nodel[p,1] = int(r_z_txt.get())
            bounds3D_del[p,1] = int(r_z_txt.get())
        bounds3D_del[-1,1] = 0.5   #Delay bounds in 3D case
        
    bounds2D_del[-1,1] = 0.5       #Delay bounds in 2D case

#Buttons declaration & Placement
btn_rir={}
btn_load = tk.Button(window, text="Load", command=load)
btn_dlt = tk.Button(window, text="Reset", command=reset)
btn_cal = tk.Button(window, text="Calculate", command=calculate)
btn_kpd_file = tk.Button(window, text="Open", command=open_file2)
btn_ok_dim = tk.Button(window, text="Ok", command=set_bounds)
btn_ok_dim.place(x=770, y=43)
btn_load.place(x=310, y=23)
btn_dlt.place(x=440, y=23)
btn_cal['state'] = tk.DISABLED   
btn_kpd_file['state'] = tk.DISABLED
btn_dlt['state'] = tk.DISABLED
btn_ok_dim['state'] = tk.DISABLED
btn_cal.place_forget()
window.mainloop()

