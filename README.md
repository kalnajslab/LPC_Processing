# LPC_Processing
Python code for downloading and processing LPC data from CCMz

These scripts will automatically download LPC TMs (Telemetry Messages) from the CCMz sftp site, process each individual binary TM file into a correspoding csv file, then create two summary csv files: the LPC_Average.csv file that contains a single line of data that represents the average of all 'good' data from each TM file and the LPC_Master.csv file that contains every record from every TM file. 

**Dependencies**
The code is written for Python 3.X and requires the following (possibly non standard) modules in addition to those included here: NumPy, Matplotlib, pysftp, gzip, csv

**Usage**
The code can be exectuded from either the command line or from an IDE like Spyder.  Before running the following variables in GetLPC need to be updated for the user, file structure and flight/instrument of interest:
  default_local_target_dir="LPC_Test" # directory where to store mirrored data on your local machine
  LPC_csv_dir = "LPC/csv/" # dir where to put processesed csv files 
  LPC_log_file = "LPC/LPC_Log.txt" #file to save log of XML messages
  mean_file_name = "LPC/LPC_Mean.csv"
  master_file_name = "LPC/LPC_Master.csv"
  ccmz_user="XXXXXXXX" # Your login on the CCMz
  ccmz_pass="XXXXXXXX" # Your password on the CCMz
  my_flights=['ST2_C0_03_TTL3','ST2_C0_05_TTL2'] # Adapt according to your needs
  
Once these values are updated, either run the script or type "python3 GetLPC.py" at the command line.

The first time the script is run it will mirror the CCMz directory structure in the local target directory and donwload all the LPC data from chosen flights.  Once this is complete (it may take some time) it will process all the TMs containing valid data into corresponding csv files in the LPC_csv_dir.  Finally it will create the master and average csv files. 

On susequent calls, the scipt will only download new TM files that don't exist in the local TM directory.  It will process these new files into csv files and then regenerate the master and average files with the new files included.

To just reprocess the csv files to the master and average files, add the argument 'reprocess' to call: "python3 GetLPC.py reprocess" or uncomment the reprocess Tre line.

**Visualizing the Data**
LPC_QuickPlot will provide a quick interactive way of visualizing the LPC data. Update the following lines to reflect the path to your 'average' and 'master' csv files:
#17 LPCcsv = 'LPC/LPC_Mean.csv'
#24     LPCcsv = 'LPC/LPC_Master.csv'

Calling this from either the command line "python3 LPC_QuickPlot.py" or from the IDE will open an mpl window with the most recent particle size distribution (PSD) and house keeping data from the averaged data.   You can step through the PSD and house keeping data using the buttons or sliders at the bottom, you can zoom or save individual plots using the control bar at the top.   To exit the application, close the plot window.


  
