#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 09:40:57 2019

@author: kalnajs
"""

#Python code to illustrate parsing of XML files 
# importing the required modules 
import csv 
import xml.etree.ElementTree as ET 
import struct
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import gzip
from datetime import datetime
from datetime import timezone


def readTMfile(TMfile,lines):
    with open(TMfile, 'rb') as TM_file:
        header = [next(TM_file).decode() for x in range(lines)]
        TM_file.readline()
        data = TM_file.readlines()

    return ''.join(header), b''.join(data)
          
def parseXML(xmlstring): 
  
    # create element tree object 
    root = ET.fromstring(xmlstring) 
    
    #create a dictionary to store the tags
    
    XMLdict = dict()
  
    for child in root:
        value = root.find(child.tag).text
        XMLdict[child.tag] = value
      
    # return the dict
    return XMLdict
         
def parseLCPdatatoCSV(InputFile,OutputFile):
    ''' This function parses the input binary file to a human readable csv file of the same name with a
    .csv extension'''    
    
    #OutputFile =  os.path.splitext( InputFile)[0] + '.csv'
    #print('parseLPC Output File:')
    #print(OutputFile)
    with gzip.open(InputFile, "rb") as binary_file:
        bindata = binary_file.read()  # Read the whole file at once
    
    start = bindata.find(b'START') + 5  # Find the 'START' string that mark the start of the binary section
    end = bindata.find(b'END') #Find the end of the binary section
    #print('START found at: ' + str(start))
    #print('END found at: ' + str(end))
    data = bindata[start:end] #Pull the binary section from the XML packet
    
    #LPC bins - each number is the left end of the bins in nm.   The first bin has minimal sensitivity
    diams = [275,300,325,350,375,400,450,500,550,600,650,700,750,800,900,1000,1200,1400,1600,1800,2000,2500,3000,3500,4000,6000,8000,10000,13000,16000,24000,24000]
    bin_header = list(map(str,diams))
    
    with open(OutputFile, mode='w') as out_file:
        StartTime = struct.unpack_from('>I',data,0)[0] #get the first number which is the start time
        date_time = datetime.fromtimestamp(int(StartTime),tz=timezone.utc)
        d = date_time.strftime("%m/%d/%Y, %H:%M:%S")
        print("Processing Measurement from: " + d + "To File: " + OutputFile)
        
        file_writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        header1 = ['Instrument: ', 'LPC-0002', 'Measurerment End Time: ', d, 'LASP Optical Particle Counter on Strateole 2 Super Pressure Balloons']
        file_writer.writerow(header1)
        
        header2 = ['Time', 'Pump1_I','Pump2_I','Heater_I','PHA_I', 'PHA_12V','PHA_3V3',
                   'Input_V', 'Flow', 'Motor_V', 'Pump1_T', 'Pump2_T',
                  'Laser_T', 'DC-DC_T', 'Inlet_T'] + bin_header
        file_writer.writerow(header2)
        
        header3 = ['[Unix Time]', '[mA]','[mA]','[mA]','[mA]', '[V]','[V]',
                   '[V]', '[SLPM]', '[V]', '[C]', '[C]',
                  '[C]', '[C]', '[C]'] + ['[diam >nm]']*len(bin_header)
        file_writer.writerow(header3)
        
        
        for y in range(int(len(data)/96 -1)):
            HGBins = []
            LGBins = []
            HKRaw = []
            HKData = [0]*15
            indx = 36 + (y+1)*96
        
            for x in range(16):
                HGBins.append(struct.unpack_from('>H',data,indx + x*2)[0])    
                LGBins.append(struct.unpack_from('>H',data,indx + x*2 + 32)[0])
                HKRaw.append(struct.unpack_from('>H',data,indx + x*2 + 64)[0])

            HKData[0] = HKRaw[0] + HKRaw[1]*65535  # 16 LSB of time_t
            HKData[1] = HKRaw[2]  # Pump1 Current in mA
            HKData[2] = HKRaw[3]  # Pump2 Current in mA
            HKData[3] = HKRaw[4]  # Heater1 Current in mA
            HKData[4] = HKRaw[5]  # Detector Current in mA
            HKData[5] = HKRaw[6] / 1000.0 # Detector voltage in V
            HKData[6] = HKRaw[7] / 1000.0 # Input Voltage
            HKData[7] = HKRaw[8] / 1000.0 #Input V
            HKData[8] = HKRaw[9] / 1000.0 # Flow in SLPM
            HKData[9] = HKRaw[10] / 1000.0 # Motor voltage in V
            HKData[10] = HKRaw[11] / 100.0 - 273.15 # Pump1 T in C
            HKData[11] = HKRaw[12] / 100.0 - 273.15 # Pump2 T in C
            HKData[12] = HKRaw[13] / 100.0 - 273.15 # Laser T in C
            HKData[13] = HKRaw[14] / 100.0 - 273.15 # DC-DC T in C
            HKData[14] = HKRaw[15] / 100.0 - 273.15 # Inlet T in C
            
            file_writer.writerow(HKData + HGBins + LGBins)
    
    return OutputFile              

def plotLPC(filename):
    ''' This function takes the 'human readable' csv file and generates quick look plots '''
    
    mpl.use('Agg')
    
    path = os.path.dirname(filename)
    
    figFile_size = path + '/plots/' + os.path.splitext(os.path.basename(filename))[0] + '_sizes.png'
    figFile_hk = path + '/plots/' + os.path.splitext(os.path.basename(filename))[0] + '_HK.png'
    
    locs = [0.3,0.5,1.0,2.0,4.0,8.0,16.0]
    HGBins = np.array([250,275,300,325,350,375,400,450,500,550,600,650,700,750,800,900,1000])
    LGBins = np.array([1000,1200,1400,1600,1800,2000,2500,3000,3500,4000,6000,8000,10000,13000,16000,24000,24000])
    diams = np.array([275,300,325,350,375,400,450,500,550,600,650,700,750,800,900,1000,1200,1400,1600,1800,2000,2500,3000,3500,4000,6000,8000,10000,13000,16000,24000,24000])
    
    LPCdata = np.genfromtxt(filename, skip_header = 7, delimiter = ',')
    row = 14
    dt = LPCdata[row+1,0]- LPCdata[row,0]
    time = LPCdata[:,0] - LPCdata[0,0]
    Ipump1 = LPCdata[:,1]
    Ipump2 = LPCdata[:,2]
    Pump1_T = LPCdata[:,10]
    Pump2_T = LPCdata[:,11]
    LaserT = LPCdata[:,12]
    DCDC_T = LPCdata[:,13]
    Inlet_T = LPCdata[:,14]
    flow = LPCdata[:,8]
    
    raw_counts = LPCdata[:,15:]
    cc_per_sample = flow * 1000*  dt/60
    counts = raw_counts/cc_per_sample[:,None]
    dr = np.diff(diams)
    dr = np.append(dr, dr[-1])
    dndr = counts/dr
    title = os.path.basename(filename)
    
    fig, ax1 = plt.subplots(figsize = (9,9))
    ax1.plot(diams/1000, np.mean(dndr,0),'r-')
    ax1.plot(diams/1000, np.mean(dndr,0) + np.std(dndr,0),'r.')
    ax1.plot(diams/1000, np.mean(dndr,0) - np.std(dndr,0),'r.')
    ax1.set_xlabel('Diameter [um]')
    ax1.set_ylabel('dN/dr [#/cc]')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim([0.3,24])
    ax1.set_ylim([1e-8,1])
    ax1.xaxis.set_minor_locator(ticker.FixedLocator(locs))
    ax1.xaxis.set_major_locator(ticker.NullLocator())
    ax1.xaxis.set_minor_formatter(ticker.ScalarFormatter())
    ax1.set_title(title)
    plt.savefig(figFile_size)
    
    fig, ax2 = plt.subplots()
    ax2.hist(diams[1:], diams[1:], weights=np.mean(dndr[:,1:],0),histtype='step')
    ax2.set_xscale('log')
    ax2.set_yscale('log')

    plt.figure(3,figsize=(9,9))
    plt.tight_layout()
    plt.suptitle(title)
    ax3 = plt.subplot2grid((2,2), (0, 0))
    ax3.plot(time,Ipump1, 'r-', label = 'Pump1')
    ax3.plot(time,Ipump2, 'b-', label = 'Pump2')
    ax3.set_ylim(0,1000)
    ax3.legend(loc='upper left')
    ax3.set_ylabel('Current [mA]')
    ax3.set_xlabel('Elapsed Time [s]')
    
    ax4 = plt.subplot2grid((2,2), (0, 1))
    ax4.plot(time,Pump1_T, 'r-', label = 'Pump1')
    ax4.plot(time,Pump2_T, 'b-', label = 'Pump2')
    ax4.legend(loc='upper left')
    ax4.set_ylabel('Temperature [C]')
    ax4.set_xlabel('Elapsed Time [s]')
    
    ax5 = plt.subplot2grid((2,2), (1, 0))
    ax5.plot(time,LaserT, 'g-', label = 'Laser')
    ax5.plot(time,DCDC_T, 'm-', label = 'DCDC Conv.')
    ax5.plot(time,Inlet_T, 'c-', label = 'Inlet')
    ax5.legend(loc='upper left')
    ax5.set_ylabel('Temperature [C]')
    ax5.set_xlabel('Elapsed Time [s]')
    
    ax6 = plt.subplot2grid((2,2), (1, 1))
    ax6.plot(time,flow, 'k-')
    ax6.set_ylabel('Flow [SLPM]')
    ax6.set_xlabel('Elapsed Time [s]')
    plt.savefig(figFile_hk)
    
    plt.close('all')
        

def main():
    file = '/Users/kalnajs/Documents/Strateole/LPC/LPC-0003/TM_03-Dec-20_14-58-02.LPC.dat'
    #csvFile = parseLCPdatatoCSV(file, file+'.csv')
    
    # for file in os.listdir('raw'):
    #     if file.endswith(".dat"):
    print('Processing: ' + file)
    csvFile = parseLCPdatatoCSV(file,os.path.splitext(file)[0] + '.csv')
    plotLPC(csvFile)  
            
if __name__ == "__main__": 
  
    # calling main function 
    main() 