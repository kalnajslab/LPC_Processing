#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 11:41:32 2020
Reads all the individual LPC files and creates a master file that contains
an average of all the contents of the individual files
@author: kalnajs
"""


import os
import glob
import numpy as np
import csv

def read_lpc_csv(filename, meanoutfile, masteroutfile):
    """ 
    This function reads the individual csv files generates from each LPC TM,
    then sorts through the data and pulls out any records where the flow is 
    greater than 1 SLPM, averages the values for those records, and saves them 
    to the mean csv file.
    """
    #read the source csv file and ditch the header and first 3 measurements    
    data = np.genfromtxt(filename, delimiter = ',', skip_header = 6)  
    
    #save all the data to the master file
    f = open(masteroutfile,'ab')
    np.savetxt(f,data, delimiter=",")
    f.close
    
    #only save the mean data with flow above 0.5 slpm to the mean file
    data[data < -273.0] = np.nan
    number_of_nans = np.count_nonzero(np.isnan(data))
    flow = data[:,8]
    to_delete = np.where(flow < 0.5)
    data = np.delete(data,to_delete[0],0)   
    print(str(len(flow) - len(to_delete[0])) + " Good records in file: " + filename )  
    
    if (len(flow) - len(to_delete[0])) > 3:
        mean_data = np.nanmean(data,axis = 0)
        mean_data[0] = mean_data[0] + 25200 #adjust from MST to UTC
        mean_data_nans = np.append(mean_data,number_of_nans)
        
        with open(meanoutfile, 'a', newline = '') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(mean_data_nans)
       



def master_csv(csv_dir,mean_file_name,master_file_name):
    """
    This function reads all the individual TM file names in the 'csv_dir'
    directory, creates new mean and master csv files, then processes 
    all the individual files into these mean and master files
    """ 
    #read all the file names in the csv dir
    filenames = glob.glob(csv_dir)
    filenames.sort() #sort the list based on filename
    print("Mean File Name: " + mean_file_name)
    #read the header from one of the csv files
    with open(filenames[1], 'r', newline = '') as csvfile:
       first = csvfile.readline()
       second = csvfile.readline()
       third = csvfile.readline()
    
    #copy the 2nd two lines of the header to the mean file
    with open(mean_file_name, 'w', newline = '') as outfile:
        outfile.write(second)
        outfile.write(third)
    
    #copy the 2nd two lines of the header to the master file
    with open(master_file_name, 'w', newline = '') as outfile:
        outfile.write(second)
        outfile.write(third)
    
    #loop over all the rest of the csv files
    for filename in filenames:
        if os.stat(filename).st_size > 0:  #only if it is not zero bytes
            #print(filename)
            read_lpc_csv(filename, mean_file_name,master_file_name)

def main():
    csv_dir = 'Processed/csv/*.csv'
    ave_output_file = 'LPC_Mean_flow.csv'
    master_output_file = 'LPC_Master.csv'
    master_csv(csv_dir,ave_output_file,master_output_file)
            
if __name__ == "__main__": 
    # calling main function 
    main()         
