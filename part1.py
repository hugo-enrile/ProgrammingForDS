import csv
import time
import pandas as pd 
import re
from calendar import monthrange
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


webdriver_options = Options()
webdriver_options.add_argument('--no-sandbox')
webdriver_options.add_argument('--disable-dev-shm-usage')

##### FIRST PART #####

assets = ['funds/amundi-msci-wrld-ae-c','etfs/ishares-global-corporate-bond-$','etfs/db-x-trackers-ii-global-sovereign-5','etfs/spdr-gold-trust','indices/usdollar']

def fillNA(df, dates):
    for i in dates:
        if i not in df.Date.values:
            row = {'Date': i, 'Price': -1, 'Change%': -1}
            df = df.append(row, ignore_index=True)
            
    df = df.iloc[::-1]
    df.reset_index(inplace = True, drop = True)
    df.Date = pd.to_datetime(df.Date, format='%b-%d-%Y')
    df = df.sort_values(by="Date")
    df.Date = df.Date.dt.strftime("%b-%d-%Y")
    df.reset_index(inplace=True, drop=True)

    for index, row in df.iterrows():
        if index == 0:
            df.at[index, 'Price'] = df.Price[index+1]
            df.at[index, 'Change%'] = "0%"
        elif row.Price == -1:
            df.at[index, 'Price'] = df.Price[index-1]
            df.at[index, 'Change%'] = "0%"
    return df

with webdriver.Chrome(ChromeDriverManager().install(), options=webdriver_options) as driver:
    for asset in assets:
        driver.get("https://www.investing.com/" + asset)
        if asset == assets[0]:
            button_accept = wait(driver, 60).until(EC.element_to_be_clickable((By.ID,"onetrust-accept-btn-handler")))
            button_accept.click()
        asset = asset.split('/')[1]
        name = driver.find_element_by_class_name("float_lang_base_1").text
        print('-------')
        print(name)
        button_historical = driver.find_element_by_link_text('Historical Data')
        button_historical = button_historical.get_attribute('href')
        print('-------')
        print('Accessing ' + str(button_historical) + '...\n')
        driver.get(button_historical)
        # date_button = wait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[5]/section/div[8]/div[3]/div/div[2]/span")))
        # date_button.click()
        date_button = driver.find_element_by_xpath("/html/body/div[5]/section/div[8]/div[3]/div/div[2]/span")
        driver.execute_script("arguments[0].click();", date_button)
        print('Successful Access!')
        print('Configuring the dates SAM is interested in...')

        #Configuring the dates SAM is interested in
        time.sleep(6)
        input_startDate = driver.find_element_by_id('startDate')
        input_startDate.clear()
        input_startDate.send_keys("01/01/2020")
        input_endDate=driver.find_element_by_id('endDate')
        input_endDate.clear()
        input_endDate.send_keys("12/31/2020")

        apply_button = wait(driver, 20).until(EC.element_to_be_clickable((By.ID, "applyBtn")))
        apply_button.click()
        time.sleep(4)
        print('Dates have been set. Retrieving data from that range...')

        #Retrieving data from the table
        table = driver.find_element_by_id('curr_table')
        rows = table.find_elements_by_tag_name('tr')
        row_text = []

        print('Creating the ' + str(asset) + '.csv file...\n')
        for row in rows:
            tmp = row.text
            tmp = tmp.replace(', ', '-')
            tmp = tmp.replace(' %', '%')
            tmp = tmp.replace(r'([A-z][a-z][a-z] )',r'([A-z][a-z][a-z]-)')
            if row is not rows[0]:
                tmp = re.compile(" ").sub("-", tmp, count=1)
            tmp = tmp.replace(' ', ',') 
            row_text.append(tmp)

        df = pd.DataFrame([row.split(",") for row in row_text])
        df.columns = df.iloc[0] 
        df = df.drop([0],axis=0)  
        df = df.drop(['Open','High','Low'], axis=1)
        d1 = datetime.date(2020, 1, 1)
        d2 = datetime.date(2020, 12, 31)
        delta = d2 - d1
        dates = []

        for i in range(delta.days + 1):
            date = d1 + datetime.timedelta(days=i)
            date = date.strftime("%b-%d-%Y")
            dates.append(date)

        df = fillNA(df, dates)

        df.to_csv('' + str(asset)+ '.csv', header = True, index = False)
        print(str(asset) + '.csv file created. You can locate it in the same directory.\n\n\n')
                



        