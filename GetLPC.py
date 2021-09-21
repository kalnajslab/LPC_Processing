#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LPC download and processing script

This is based on Albert's automatic download script, customized for LPC.
The script uses sftp to mirror the LPC directories on the CCMz.  If there is a
a new LPC TM file, it processes that file using the readLPCXML module which generates
a csv file of that TM.   It then adds that data to two global CSV files, one 
containing every measurement from each TM file, the other containing a single 
average measurement from each TM file.  It also reads the state messages from 
XML portion of the TM file and appends those to the LPC_State_Log text file.  

This interface uses Python 3.x, pysftp, gzip, csv and readLPCXML modules.

"""

import sys
import os
import glob
import pysftp
import gzip
from readLPCXML import *
from LPC_Make_Master_CSVs import *

if len(sys.argv) > 1:
    if sys.argv[1] == 'reprocess':
        reprocess = True
        print("Reprocessing CSV files")
    if sys.argv[1] == 'download':
        download = True
        print("Downloading without processing")

#Uncomment this line to ONLY reprocess existing csv files
#reprocess = True
#Uncomment this line to ONLY download new files without processing
#download = True
#https://pysftp.readthedocs.io/en/latest/pysftp.html


###### Update these values for your user name, flight of interest and local directory structure #########
default_local_target_dir="LPC_Test" # directory where to store mirrored data on your local machine
LPC_csv_dir = "LPC/csv/" # dir where to put processesed csv files 
LPC_log_file = "LPC/LPC_Log.txt" #file to save log of XML messages
mean_file_name = "LPC/LPC_Mean.csv"
master_file_name = "LPC/LPC_Master.csv"
ccmz_user="XXXXXX" # Your login on the CCMz
ccmz_pass="XXXXXX" # Your password on the CCMz
my_flights=['ST2_C0_03_TTL3','ST2_C0_05_TTL2'] # Adapt according to your needs
########################################################################################################


ccmz_url="sshstr2.ipsl.polytechnique.fr" # CCMz URL from where to download data
my_instruments=['LPC'] # Adapt according to your needs
flight_or_test='Flight'
tm_or_tc='TM'
raw_or_processed='Processed'


def mirror_ccmz_folder(instrument, ccmz_folder, local_target_dir=default_local_target_dir, show_individual_file=True):
   """
   Mirror one CCMz folder.
   Files are stored locally in local_target_dir/ccmz_path/to/ccmz_folder/
   Files already downloaded are not downloaded again.
   local_target_dir prescribes where CCMz files will be downloaded locally.
   show_individual_file controls whether the name of each downloaded file is displayed or not.
   """

   print('---------------------------------')
   print('Trying to mirror CCMz folder: \033[1m'+ccmz_folder+'\033[0m')
   
   downloaded_files = []

   # Create (if needed) the appropriate local directory
   local_folder=os.path.join(local_target_dir,ccmz_folder)
   if not os.path.exists(local_folder):
      os.makedirs(local_folder)

   # Connect to CCMz
   try:
       with pysftp.Connection(host=ccmz_url, username=ccmz_user, password=ccmz_pass) as sftp:
          print("\033[1mConnection to CCMz succesfully established\033[0m...")

          # Switch to the remote directory
          try:
              sftp.cwd(ccmz_folder)
          except IOError:
              print('\033[1m\033[91mNo such directory on CCMz: '+ccmz_folder+'\033[0m')
              return

          # Get file list in current directory, i.e. those that have been already downloaded from CCMz
          local_files=glob.glob(os.path.join(local_folder,'*')) # filenames with relative path
          local_filenames=[os.path.basename(f) for f in local_files] # filenames without

          # Get file list from the CCMz directory with file attributes
          ccmz_file_list = sftp.listdir_attr()

          # check wether CCMz files need to be downloaded
          n_downloads=0

          for ccmz_file in ccmz_file_list:
              # Get rid of directories in CCMZ folder (if any)
              if ccmz_file.longname[0] == '-':
                 ccmz_filename=ccmz_file.filename
                 # Check whether the file has already been downloaded (so as to not download it again)
                 if not ccmz_filename in local_filenames:
                    # file has to be downloaded
                    if show_individual_file == True:
                       print('Downloading \033[92m'+ccmz_filename+'\033[0m...') # display file name
                       downloaded_files.append(os.path.join(local_folder,ccmz_filename))
                    sftp.get(ccmz_filename,os.path.join(local_folder,ccmz_filename),preserve_mtime=True)
                    #print(ccmz_filename)
                    n_downloads=n_downloads+1
            # Create a ZipFile Object and load sample.zip in it
                    print (os.path.join(local_folder,ccmz_filename))

            
          # and print some statistics
          if n_downloads == 0:
              print('\nYour local repository \033[92m'+local_folder+'\033[0m looks\033[1m up do date\033[0m')
          else:
              print('\n\033[1m'+str(n_downloads)+ '\033[0m file(s) downloaded in \033[92m'+local_folder+'\033[0m')
              print('List of downloaded Files')
              return downloaded_files
              

   except:
          print('\033[1m\033[91mConnection to CCMz failed\033[0m: check your login/password')
          return

def loop_over_flights_and_instruments():
    """
    Get all data from CCMz for the input list of flights/instruments
    """
    for flight in my_flights:
        for instrument in my_instruments:
            ccmz_folder=os.path.join(flight,instrument,flight_or_test,tm_or_tc,raw_or_processed)
            #mirror_ccmz_folder(ccmz_folder)
            new_files = mirror_ccmz_folder(instrument,ccmz_folder, show_individual_file=True)
            if new_files != None and download != True:
                for file in new_files:
                    if file.endswith('.gz'):
                        path = os.path.dirname(file)
                        filename = os.path.basename(file)
                    
                    if 'LPC' == instrument:
                        InputFile = path + '/' + filename
                        #print('Input Filename: ' + InputFile)
                        try:
                            readHeader(InputFile,LPC_log_file)
                        except:
                            print("Unable to read header from: " + os.path.basename(file))
                        try:
                            OutputFile = LPC_csv_dir + os.path.splitext(os.path.basename(file))[0]
                            OutputFile = os.path.splitext(OutputFile)[0] + '.csv'
                            #print('Processing to: ' + OutputFile)
                            csvFile = parseLCPdatatoCSV(InputFile,OutputFile)
                            #plotLPC(csvFile)
                        except:
                            print('Unable to Process Data From: ' + os.path.basename(file) )
                
                
                master_csv(LPC_csv_dir + "*.csv",mean_file_name,master_file_name)
                        

def readHeader(InputFile,logFile):    
    
    with gzip.open(InputFile, "rb") as binary_file:
        data = binary_file.read()
    start = data.find(b'<StateMess1>')
    end = data.find(b'</StateMess1>')
    XMLMsg = data[start+12:end].decode()
    start = data.find(b'<Msg>')
    end = data.find(b'</Msg>')
    MsgID = data[start+5:end].decode()
    
    if os.path.basename(InputFile).startswith('ST2'):
        #print(os.path.basename(InputFile))
        #print(MsgID + ' ' + XMLMsg)
        
        with open(logFile, "a") as log:
            log.write(os.path.basename(InputFile) + ': ' + MsgID + ' ' + XMLMsg + '\n')                        

if __name__ == '__main__':
    if reprocess:
        master_csv(LPC_csv_dir + "*.csv",mean_file_name,master_file_name)
    else:
        loop_over_flights_and_instruments()
