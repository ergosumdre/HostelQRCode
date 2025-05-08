import paramiko
import pandas as pd
from datetime import datetime
import os
import datetime
import re
from datetime import datetime, timedelta
import csv



# Linux Path
guest_list_path = "/home/ubuntu/qrCode/v2/data/cleaned_guest_list.csv"
guestExcel_list_path = "/home/ubuntu/qrCode/v2/data/raw.xlsx"
door_codes_path = "/home/ubuntu/qrCode/data/doorCodes.csv"
qrCode_path = "/home/ubuntu/qrCode/v2/data/qrCode.png"
checkin_html_path = "/home/ubuntu/qrCode/v2/data/checkin_details.html"
activity_logs_path = "/home/ubuntu/qrCode/v2/data/activity_logs.txt"


def list_files_sftp(hostname, port, username, password, directory):
    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    file_paths = []
    try:
        # Connect to the sFTP server
        client.connect(hostname, port, username, password)
        # Create an sFTP client
        sftp = client.open_sftp()
        # Change to the specified directory
        sftp.chdir(directory)
        # List all files in the directory
        files = sftp.listdir()
        # Add the directory path to the file names
        file_paths = [sftp.normalize(os.path.join(directory, file)) for file in files]
        # Sort the file paths by the newest date
        file_paths = sorted(file_paths, key=lambda x: datetime.strptime(os.path.basename(x).split('Guests in house ')[-1].split(' - ')[0], '%m-%d-%Y %I-%M-%S %p'), reverse=False)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close the connections
        sftp.close()
        client.close()
    return file_paths


def download_file_sftp(hostname, port, username, password, remote_filepath, local_filepath):
    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the sFTP server
        client.connect(hostname, port, username, password)
        # Create an sFTP client
        sftp = client.open_sftp()
        # Download the file
        sftp.get(remote_filepath, local_filepath)
        print(f"File downloaded successfully: {local_filepath}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close the connections
        sftp.close()
        client.close()



current_files = list_files_sftp("XXXXX", 
                                22, 
                                "XXXXX", 
                                "XXXXXX", 
                                "XXXXXX")
lastest_file = current_files[len(current_files)-1]

download_file_sftp("XXXXX",
                    22, "XXXXX",
                    "XXXXX",
                    lastest_file,
                    guestExcel_list_path)


def convert_to_csv(file_path):
    df = pd.read_excel(file_path, sheet_name=1)
    df = df.rename(columns={'Unnamed: 0': 'Bed Number'})
    fixed_rows = []
    current_bed = None
    current_customer = None
    companions = None
    products = None
    email = None
    preauths = None
    balance = None
    check_in_date = None
    check_out_date = None
    for i, row in df.iterrows():
        if isinstance(row['Bed Number'], str):
            if current_bed is not None:
                fixed_rows.append([current_bed, current_customer, companions, products, email, preauths, balance, check_in_date, check_out_date])
            current_bed = row['Bed Number']
            current_customer = row['Customer']
            companions = row['Companions']
            products = row['Products']
            check_in_date = datetime.strptime(row['Companions'].split()[2] + ' 11:00:00', '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            check_out_date = datetime.strptime(row['Companions'].split()[4] + ' 10:00:00', '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            email = None
            preauths = None
            balance = None
        elif isinstance(row['Email'], str):
            email = row['Email']
            preauths = row['Preauthorizations']
            balance = row['Balance including preauthorizations']
    fixed_rows.append([current_bed, current_customer, companions, products, email, preauths, balance, check_in_date, check_out_date])
    fixed_df = pd.DataFrame(fixed_rows, columns=['Bed Number', 'Customer', 'Companions', 'Products', 'Email', 'Preauthorizations', 'Balance including preauthorizations', 'check_in_date', 'check_out_date'])
    fixed_df = fixed_df.rename(columns={'Bed Number': 'room_number', 'Email':'email'})
    return fixed_df


dat = convert_to_csv(guestExcel_list_path)
dat.to_csv(guest_list_path, index=False)
