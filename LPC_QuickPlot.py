#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 12:41:41 2021

@author: kalnajs
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timezone
from matplotlib.widgets import Slider, Button


LPCcsv = 'LPC/LPC_Mean.csv'

if len(sys.argv) > 1:
    if sys.argv[1] == 'master':
        LPCcsv = 'LPC/LPC_Master.csv'
        print("Plotting ALL LPC records")
        
LPC = np.genfromtxt(LPCcsv,skip_header=2,delimiter=',')
LPC_time = LPC[:,0]
LPC_diams = np.array([275,300,325,350,375,400,450,500,550,600,650,700,750,800,900,1000,1200,1400,1600,1800,2000,2500,3000,3500,4000,6000,8000,10000,13000,16000,24000])
LPC_conc = LPC[:,15:46]
LPC_Pump1_T = LPC[:,10] 
LPC_Pump2_T = LPC[:,11]
LPC_Inlet_T = LPC[:,14]
LPC_Flow = LPC[:,8]
LPC_Vin = LPC[:,7]

# Define initial parameters
init_szd = len(LPC_Flow)-1

# Create the figure and the line that we will manipulate
fig1, ax1 = plt.subplots()
line, = plt.plot(LPC_diams, LPC_conc[init_szd,:], lw=2)
ax1.set_xlabel('Diameter [nm]')
ax1.set_ylabel('Concentration')
ax1.set_yscale('log')
ax1.set_xscale('log')
ax1.set_xlim(300,24000)
annotation = 'Flow: ' + "{:.2f}".format(LPC_Flow[init_szd]) + '\nT_Pump1: ' + "{:.2f}".format(LPC_Pump1_T[init_szd])+ '\nT_Pump2: ' + "{:.2f}".format(LPC_Pump2_T[init_szd])+ '\nT_Inlet: ' + "{:.2f}".format(LPC_Inlet_T[init_szd])+ '\nV_in: ' + "{:.2f}".format(LPC_Vin[init_szd])
text = ax1.text(0.6,0.7,annotation, transform=ax1.transAxes)
date_time = datetime.fromtimestamp(int(LPC_time[init_szd]),tz=timezone.utc)
d = date_time.strftime("%m/%d/%Y, %H:%M:%S")
ax1.set_title("LPC Size Distribution at: "+d)
axcolor = 'lightgoldenrodyellow'
ax1.margins(x=0)

# adjust the main plot to make room for the sliders
plt.subplots_adjust(bottom=0.25)

# Make a horizontal slider to control which szd we plot.
axszd = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
szd_slider = Slider(
    ax=axszd,
    label='Scan Number',
    valmin=0,
    valmax=len(LPC_Flow),
    valinit=init_szd,
    valfmt="%i"
)

# The function to be called anytime a slider's value changes
def update(val):
    print('Plotting Scan: ' + str(int(szd_slider.val)))
    annotation = 'Flow: ' + "{:.2f}".format(LPC_Flow[int(szd_slider.val)]) + '\nT_Pump1: ' + "{:.2f}".format(LPC_Pump1_T[int(szd_slider.val)])+ '\nT_Pump2: ' + "{:.2f}".format(LPC_Pump2_T[int(szd_slider.val)])+ '\nT_Inlet: ' + "{:.2f}".format(LPC_Inlet_T[int(szd_slider.val)])+ '\nV_in: ' + "{:.2f}".format(LPC_Vin[int(szd_slider.val)])
    text.set_text(annotation)
    date_time = datetime.fromtimestamp(int(LPC_time[int(szd_slider.val)]),tz=timezone.utc)
    d = date_time.strftime("%m/%d/%Y, %H:%M:%S")
    ax1.set_title("LPC Size Distribution at: "+d)
    line.set_ydata(LPC_conc[int(szd_slider.val),:])
    fig1.canvas.draw_idle()


# register the update function with each slider
szd_slider.on_changed(update)
#amp_slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
nextax = plt.axes([0.8, 0.025, 0.1, 0.04])
button_next = Button(nextax, 'Next', color=axcolor, hovercolor='0.975')
prevax = plt.axes([0.68, 0.025, 0.1, 0.04])
button_prev = Button(prevax, 'Prev', color=axcolor, hovercolor='0.975')


def b_next(event):
    szd_slider.set_val(szd_slider.val + 1)
    update(szd_slider.val + 1)
def b_prev(event):
    szd_slider.set_val(szd_slider.val - 1)
    update(szd_slider.val - 1)

button_next.on_clicked(b_next)
button_prev.on_clicked(b_prev)

plt.show()