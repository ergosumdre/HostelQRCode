from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import re
import gradio as gr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import re
import qrcode
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from PIL import Image
from gradio.inputs import Image as PyPNGImage
from PIL import Image
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ftplib
from io import BytesIO
import random
import string
import datetime
import subprocess
from requests.utils import quote
from selenium.webdriver.chrome.options import Options
import os
import datetime
import re
from datetime import datetime, timedelta
import csv



dir_path = "/home/dre/Downloads/"
pattern = r"^Guests in house"

for filename in os.listdir(dir_path):
    if re.match(pattern, filename):
        os.remove(os.path.join(dir_path, filename))




#chrome_options = Options()
#chrome_options.add_argument('--headless')
#driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver = webdriver.Chrome(ChromeDriverManager().install())
#driver = webdriver.Chrome("/bin/google-chrome")
def getReport():
  driver.get("https://app.mews.com")
  # Wait for the page to load
  sleep(5)
  # Find the email input box and enter the username
  username = "XXXXX@gmail.com"
  username_box = driver.find_element(By.ID, "nameOrEmail")
  username_box.send_keys(username)
  username_box.send_keys(Keys.RETURN)
  # Wait for the page to load
  sleep(2)
  # Find the password input box and enter the password
  pwd = "XXXXX"
  password_box = driver.find_element(By.ID, "password")
  password_box.send_keys(pwd)
  password_box.send_keys(Keys.RETURN)
  # Wait for the page to load
  sleep(5)
  now = datetime.now()
  yesterday = now - timedelta(days=1)
  start_date_string = yesterday.strftime("%-m %d %Y")
  start_date_string = quote(start_date_string, safe='')
  tomorrow = now + timedelta(days=1)
  end_date_string = tomorrow.strftime("%-m %d %Y")
  end_date_string = quote(end_date_string, safe='')
  # Navigate to the URL with the data of interest
  url = f'https://app.mews.com/Commander/GuestInHouseReport/Index?EnterpriseId=XXXXXXXXXX&Custom=True&Service.Id=XXXXXXXXXXX&Start.Date={start_date_string}&Start.Time=10%3A15+AM&End.Date={end_date_string}&End.Time=11%3A45+PM&&States.CheckedIn=true&States.CheckedOut=false&States.Confirmed=true&States.Optional=false&DisplayOptions.AllProducts=true&DisplayOptions.Balance=true&DisplayOptions.CarRegistrationNumber=false&DisplayOptions.CustomerNotes=false&DisplayOptions.ProductsConsumedInInterval=false&DisplayOptions.ReservationNotes=false&Ordering=Space'
  driver.get(url)
  
  sleep(10)
  driver.find_element(By.CSS_SELECTOR, "div.cf1lHZ.cf2MAH").click() # privacy modal
  sleep(10)
  balance_keys = "Balance"
  #driver.find_element(By.XPATH, "//*[@id='DisplayOptions']").click() #add balance to report 

  #driver.find_element(By.XPATH, "//*[@id='DisplayOptions']").send_keys(balance_keys)
  #driver.find_element(By.XPATH, "//*[@id='DisplayOptions']").send_keys(Keys.RETURN)
  #driver.find_element(By.XPATH, "//*[@id='DisplayOptions']").send_keys(Keys.TAB)



  driver.find_element(By.CSS_SELECTOR, "div.style__ContentElement-sc-mz2hb5-0.hbVrSL").click() # export icon/button


  sleep(5)
  driver.find_element(By.CSS_SELECTOR, 'span.style__LeftContentElement-sc-uc9cl7-3.fdUlu').click()
  sleep(10)
  driver.get("https://app.mews.com/Commander/Export/Index")
  # get the current date
  now = datetime.now()
  # format the date as M-DD-YYYY
  date_string = now.strftime("%-m-%-d-%Y")
  sleep(5)
  driver.find_element(By.PARTIAL_LINK_TEXT,f'Guests in house {yesterday.strftime("%-m-%-d-%Y")} 10-15-00 AM - {tomorrow.strftime("%-m-%-d-%Y")}').click()
  sleep(10)

getReport()


def clean_report():
    # Format date in mdy format
    date_str = datetime.now().strftime("%m-%-d-%Y")
    # Remove leading 0
    date_str = date_str.lstrip('0')

    # Search for files in specified directory with filename matching pattern
    dir_path = "/home/dre/Downloads/"
    file_pattern = f'Guests in house'
    matching_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and file_pattern in f]
    dat = matching_files



    df = pd.read_excel(dat[0], sheet_name=1)
    df = df.rename(columns={'Unnamed: 0': 'Bed Number'})
    # initialize empty lists to hold the fixed rows
    fixed_rows = []
    current_bed = None
    current_customer = None
    companions = None
    products = None
    email = None
    preauths = None
    balance = None

    # iterate over the rows in the DataFrame
    for i, row in df.iterrows():
        # if this row is a bed row, save the current fixed row (if there is one)
        # and start building a new one
        if isinstance(row['Bed Number'], str):
            if current_bed is not None:
                fixed_rows.append([current_bed, current_customer, companions, products, email, preauths, balance])
            current_bed = row['Bed Number']
            current_customer = row['Customer']
            companions = row['Companions']
            products = row['Products']
            email = None
            preauths = None
            balance = None
        # if this row is an email row, save the email address
        elif isinstance(row['Email'], str):
            email = row['Email']
            preauths = row['Preauthorizations']
            balance = row['Balance including preauthorizations']

    # append the last fixed row
    fixed_rows.append([current_bed, current_customer, companions, products, email, preauths, balance])

    # create a new DataFrame from the fixed rows
    fixed_df = pd.DataFrame(fixed_rows, columns=['Bed Number', 'Customer', 'Companions', 'Products', 'Email', 'Preauthorizations', 'Balance including preauthorizations'])
    fixed_df = fixed_df.rename(columns={'Bed Number': 'room_number', 'Email':'email'})
    return fixed_df


guests_in_house = clean_report()


file_path = "/data/cleaned_guest_list.csv"
if os.path.exists(file_path):
    os.remove(file_path)
    print("File deleted successfully")
else:
    print("The file does not exist")

guests_in_house.to_csv(file_path, index = False)


def add_dates_to_csv(csv_file):
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        header.extend(['check_in_date', 'check_out_date'])
        rows = [header]
        for row in reader:
            companions = row[2].split()
            check_in_date = datetime.strptime(companions[2] + ' 11:00:00', '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            check_out_date = datetime.strptime(companions[4]+ ' 10:00:00', '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            row.extend([check_in_date, check_out_date])
            rows.append(row)
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


add_dates_to_csv(file_path)


