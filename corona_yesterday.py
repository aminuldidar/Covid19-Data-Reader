#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
import pandas as pd
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys
from os import path


chrome_options = Options()  
#chrome_options.add_argument('--window-size=1050,660')
#chrome_options.add_argument("--headless")


class Coronavirus():
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=r"./driver/chromedriver.exe",options=chrome_options)

try:
	print("Reading html page from the source..")
	
	bot = Coronavirus()
	bot.driver.get('https://www.worldometers.info/coronavirus/')
	
except Exception as e:
	print(e)
	sys.exit()
	
try:
	print("Clicking on yesterday button..")
	
	button=bot.driver.find_element_by_id("nav-yesterday-tab")
	button.click()
	
except Exception as e:
	print(e)
	sys.exit()

try:
    #id="main_table_countries_yesterday"
    print("Reading data from html file..")
    tables=bot.driver.find_elements_by_id("main_table_countries_yesterday")
except Exception as e:
    print(e)
    sys.exit()

table=tables[0]

trs=table.find_elements_by_tag_name("tr")

## Take the table data into a list
data_list = []
for tr in trs:
    tds= tr.find_elements_by_tag_name('td')
    row = []
    for td in tds:
        row.append(td.text)
    if(len(row)>0):
        #print(row)
        data_list.append(row)

## Get the column names

cols=[]
tr=trs[0]

tds= tr.find_elements_by_tag_name('th')
for td in tds:
    cols.append(td.text)
if(len(cols)>0):
    print(cols)
        

df=pd.DataFrame(data=data_list,columns=cols)

bot.driver.quit()


def ClosedCase(TotalCase,ActiveCase):
    try:
        TotalCase=TotalCase.replace(',',"")
        TotalCase = int(TotalCase)
        ActiveCase=ActiveCase.replace(',',"")
        ActiveCase = int(ActiveCase)
    except Exception as e:
        print(e)
        return None
    return TotalCase - ActiveCase


df['Closed Case'] = df.apply(lambda x: ClosedCase(x['Total\nCases'],x['Active\nCases']),axis=1)


def TotalDeath(TotalDeath, ClosedCase):
    #print(TotalDeath)
    DeathRate = None
    if(len(TotalDeath)>0):
        TotalDeath=TotalDeath.replace(',',"")
        TotalDeath = int(TotalDeath)
        DeathRate = (TotalDeath/ClosedCase)*100
        DeathRate = round(DeathRate,2)
    return DeathRate


df['Death Rate\n(%)'] = df.apply(lambda x: TotalDeath(x['Total\nDeaths'],x['Closed Case']),axis=1)

dtime = datetime.datetime.now().timestamp()

fileName="./data/ByDate/"+str(dtime).split('.')[0]+'.csv'

df.to_csv(fileName,index=False)

CountryList=df['Country,\nOther'].to_list()
CountryList=CountryList[0:-1]

for country in CountryList:
    df_country = df[df['Country,\nOther']==country]
    #df_country.to_csv(fileName,index=False)
    df_country=df_country.rename(columns={'Country,\nOther':'Date Time'})
    df_country['Date Time'] = dtime
    
    fileName = "./data/ByCountry/"+country+".csv"
    isExist = path.exists(fileName)
    #print(val)
    if(isExist==False):
        df_country.to_csv(fileName,index=False)
    else:
        df_there=pd.read_csv(fileName)
        df_update = pd.concat([df_there,df_country])
        df_update.to_csv(fileName,index=False)
