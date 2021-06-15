import tkinter as tk
from tkinter import filedialog
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

#Main Window
window = tk.Tk()
window.title("Reverb Calibration")
window.geometry('700x820')

#Frames Declaration & Placement
frame1 = tk.Frame(window, height = 405, width = 250, bg = "WHITE", borderwidth=2)
frame1.place(x=0, y=100)
frame2 = tk.Frame(window, height = 200, width = 700, bg= "WHITE", borderwidth=2)
frame2.place(x=0, y=600)

#Labels, Entry's & checkboxes Declaration & Placement
lbl_kpd = tk.Label(window, text="Known Position Devices:")
lbl_upd = tk.Label(window, text="Unknown Position Devices:")
lbl_kpd_file = tk.Label(window, text="Known Devices File")
lbl_fs = tk.Label(window, text="Sampling Frequency:", wraplength=100, justify="left")
lbl_hz = tk.Label(window, text="Hz")
lbl_delta_cal=tk.Label(frame2, text="Estimated Delta:")
lbl_rir={}
lbl_rir_loc={}
kpd_txt = tk.Entry(window,width=5)
upd_txt = tk.Entry(window,width=5)
fs_txt = tk.Entry(window, width=6)
dly_checkbox_fun = tk.IntVar()
dly_checkbox= tk.Checkbutton(frame2, text = "Activate Delay", 
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
lbl_delta_cal.place_forget()
fs_txt.place_forget()


def open_file(i):
    dd = {}
    dd["filename{0}".format(i)] = filedialog.askopenfilename()
    print(dd)

def open_file2():
    kpd_file = filedialog.askopenfilename()
    print(kpd_file)

def load():
       
    x = int(upd_txt.get())
    lbl_fs.place(x=0, y=540)
    lbl_hz.place(x=142, y=553)
    lbl_kpd_file.place(x=0,y=80)
    btn_kpd_file.place(x=130, y=78)
    fs_txt.place(x=80, y=550)
    dly_checkbox.place(x=580, y=100)
    btn_cal.place(x=580, y=170)
    btn_load['state'] = tk.DISABLED
    upd_txt['state'] = tk.DISABLED
    kpd_txt['state'] = tk.DISABLED
    btn_dlt['state'] = tk.NORMAL
    btn_cal['state'] = tk.NORMAL
    btn_kpd_file['state'] = tk.NORMAL
    fs_txt['state'] = tk.NORMAL
    dly_checkbox['state'] = tk.NORMAL




    for m in range(1, x+1):
        lbl_rir[m] = tk.Label(frame1, text = "#"+str(m)+" Device RIR")
        lbl_rir[m].place(x=0, y=1+(m*25))
        btn_rir[m] = tk.Button(frame1, text="Open", command=lambda i=m :open_file(i))
        btn_rir[m].place(x=100, y=0+(m*25))
    
def reset():
    
    lbl_kpd_file.place_forget()
    btn_kpd_file.place_forget()
    lbl_delta_cal.place_forget()
    canvas_fig.get_tk_widget().place_forget()
    btn_load['state'] = tk.NORMAL
    upd_txt['state'] = tk.NORMAL
    kpd_txt['state'] = tk.NORMAL
    btn_dlt['state'] = tk.DISABLED
    btn_cal['state'] = tk.DISABLED
    btn_kpd_file['state'] = tk.DISABLED
    dly_checkbox['state'] = tk.DISABLED
    fs_txt['state'] = tk.DISABLED

    x = int(upd_txt.get())
    for m in range(1, x+1):
        lbl_rir[m].destroy()
        btn_rir[m].destroy()
        lbl_rir_loc[m].destroy()


def calculate ():
    
    lbl_delta_cal.place(x=500, y=25)
    canvas_fig.get_tk_widget().place(x=220, y=70)

    #Labels with position
    x = int(upd_txt.get())
    for m in range(1, x+1):
        lbl_rir_loc[m] = tk.Label(frame2, text = "#"+str(m)+" Device Location: "+"x:    y:    z:")
        lbl_rir_loc[m].place(x=0, y=1+(m*25))

#Function for new window where you set up the room limits
def roomlim():
      
    window_r = tk.Toplevel(window)
    window_r.title("Room Bounds")
    window_r.geometry("400x250")
    
    #Declaration of Labels, Entry's & Placement
    lbl_room_x = tk.Label(window_r, text="X:       meters")
    lbl_room_y = tk.Label(window_r, text="Y:        meters")
    lbl_room_z = tk.Label(window_r, text="Z:        meters")
    r_x_txt = tk.Entry(window_r,width=2)
    r_y_txt = tk.Entry(window_r,width=2)
    r_z_txt = tk.Entry(window_r,width=2)

    lbl_room_x.place(x=10,y=100)
    lbl_room_y.place(x=150,y=100)
    lbl_room_z.place(x=290,y=100)
    r_x_txt.place(x=25,y=98)
    r_y_txt.place(x=165,y=98)
    r_z_txt.place(x=305,y=98)

    #Hide or unhide Z parameter for 3D or 2D Room
    def dimension():
        print(var_dim.get())
        if var_dim.get() == 1:
            r_z_txt['state'] = tk.DISABLED
            lbl_room_z.place_forget()
            r_z_txt.place_forget()
        else:
            r_z_txt['state'] = tk.NORMAL
            lbl_room_z.place(x=290,y=100)
            r_z_txt.place(x=305,y=98)

    var_dim = tk.IntVar()
    checkbox_2d= tk.Checkbutton(window_r, text = "Select 2D Room Bounds", 
                      command = dimension,
                      variable = var_dim,
                      onvalue = 1,
                      offvalue = 0,
                      height = 2,
                      width = 20)
    checkbox_2d.place(x=100, y=30)
    btn_load = tk.Button(window_r, text="Ok", command=window_r.destroy)
    btn_load.place(x=170, y=170)



#Plot Example
fig = plt.figure(figsize=(5, 5))
x_del = [0.2523,0.2555,0.2383,0.5366,0.5385,0.5228,0.827,0.8372,0.8205]
y_del = [0.125,0.4357,0.7495,0.1349,0.4451,0.75,0.1224,0.4400,0.7613]
x_nodel = [0.3265,0.3387,0.3095,0.6019,0.6116,0.5902,0.8926,0.907,0.887]
y_nodel = [0.1,0.4323,0.7829,0.1064,0.4434,0.7752,0.1,0.4383,0.7812]
x_gt = [0.3311,0.3531,0.3238,0.6102,0.6231,0.5982,0.9004,0.9148,0.8916]
y_gt = [0.0863,0.4320,0.7822,0.1052,0.4419,0.7787,0.0975,0.4391,0.7835]
plt.scatter(x_del,y_del, marker = 'o')
plt.scatter(x_nodel,y_nodel, marker = 'x')
plt.scatter(x_gt,y_gt,marker = '^');
plt.title('Estimated positions')
plt.grid()
leg = plt.legend(['Delay','No delay','Ground Truth'],loc='upper center',bbox_to_anchor=(0.5, -0.05),fancybox=True, shadow=True, ncol=3);

#Canvas for figure
canvas_fig = FigureCanvasTkAgg(fig, master=window)
canvas_fig.get_tk_widget().place_forget()
#canvas_fig.draw()

#Buttons declaration & Placement
btn_rir={}
btn_load = tk.Button(window, text="Load", command=load)
btn_dlt = tk.Button(window, text="Reset", command=reset)
btn_cal = tk.Button(frame2, text="Calculate", command=calculate)
btn_room = tk.Button(window, text="Room Bounds", command=roomlim)
btn_kpd_file = tk.Button(window, text="Open", command=open_file2)
btn_load.place(x=310, y=23)
btn_dlt.place(x=440, y=23)
btn_room.place(x=560, y=23)
btn_cal['state'] = tk.DISABLED    
btn_kpd_file['state'] = tk.DISABLED
btn_dlt['state'] = tk.DISABLED
btn_cal.place_forget()
window.mainloop()


#tex= "KPD: " + kpd_txt.get() + "   UPD: " + upd_txt.get()
    #lbl_dev.configure(text=tex)