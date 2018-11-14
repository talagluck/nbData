from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import json
import pickle
from Classes.Residential import Residential
from Classes.Commercial import Commercial
from Classes.Building import Building
import datetime
from tkinter import messagebox
#figure out new category (the first property in tuxedo?)
#instead of creating csvs for scraped and error, try updating the csv, or else keep track of what i'm up to
#add section for taxes
#merge residential and commercial?



#iterate over each link row
#scrape the link for each one, using the swis and tax_id for each csv file
#if successfully scraped, append to a new csv of successfully scraped links
#if not, append to a new csv of unsuccessfully scraped links

#add Taxes
#add date/time scraped

def load_link_csv(csv_filename):
    data = pd.read_csv(csv_filename)
    return data

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    return driver

def through_public_access(url):
    driver.get(url)

    btnPublicAccess=None
    btnC = None
    btnR = None

    btnPublicAccess = driver.find_elements_by_id('btnPublicAccess')
    # print(type(btnPublicAccess),btnPublicAccess)

    if btnPublicAccess:
        btnPublicAccess[0].click()
        driver.implicitly_wait(1)



def try_button(button_list):
    if button_list:
        button_list[0].click()
        driver.implicitly_wait(1)
        return True
    else:
        return False


def res_or_com(driver):
    soup = BeautifulSoup(driver.page_source,'lxml')
    # com = driver.find_elements_by_id('pnlComButtons')
    # res = driver.find_elements_by_id('pnlResButtons')
    btnCom = driver.find_elements_by_id('btnCReport')
    # print(btnCom)
    # if not try_button(btnCom):
    #     print("not commercial")
    if try_button(btnCom):
        return "Commercial"

    btnRes = driver.find_elements_by_id('btnReport')
    # print(btnRes)
    # if not try_button(btnRes):
    #     print("not residential")
    if try_button(btnRes):
        return "Residential"

    return False

def property_track(good_or_bad,municipality,swis,tax_ID):
    data = {"swis":swis,"tax_ID":tax_ID,"time_attempted":datetime.datetime.now()}
    data = pd.DataFrame([data])
    folder_name = municipality+'_scraped'
    if good_or_bad == "good":
        file_name = folder_name+'/successfully_scraped.csv'
        print("Success")
    elif good_or_bad == "bad":
        file_name = folder_name+'/error_scraped.csv'
        print("Error")
    else:
        print("Error")
        return "Error"

    if not os.path.exists(folder_name):
       os.mkdir(folder_name)

    if os.path.exists(file_name):
       data.to_csv(file_name,mode='a',header=False,index_label=False)
    else:
       data.to_csv(file_name,index_label=False)

def iterate_link_table(pd_link_table,start,finish,driver):
    count=start
    for row in link_table[start:finish].itertuples():
        url = row.link
        driver.get(url)

        swis = row.swis_x
        tax_ID = row.tax_ID

        prop_type = res_or_com(driver)

        if prop_type:
            print(f'{count}/{finish}',tax_ID, prop_type, swis)
            try:
                entry = Building(driver,swis,tax_ID,municipality,prop_type)
                entry.all_csvs()
                property_track("good", municipality, swis, tax_ID)
            except:
                property_track("bad", municipality, swis, tax_ID)
        else:
            property_track("bad", municipality, swis, tax_ID)
        count+=1


municipality = "newburgh"
# csv_filename = municipality + "_links.csv"
csv_filename = "error_links.csv"
# url = "http://propertydata.orangecountygov.com/propdetail.aspx?swis=331100&printkey=00100000020010000000"


link_table = load_link_csv(csv_filename)
driver = setup_driver()
through_public_access(link_table.iloc[0].link)
iterate_link_table(link_table,0,len(link_table),driver)
driver.quit()
print('Done')
# messagebox.showinfo("Done", "Done!")

# try: #if commercial
#     # com = driver.find_element_by_id('pnlComButtons'):
#     btnC = driver.find_element_by_id('btnCReport')
#     btnC.click()
#     driver.implicitly_wait(1)
# except:
#     pass
#
# try: #if residential
#     # res = driver.find_element_by_id('pnlResButtons'):
#     btnR = driver.find_element_by_id('btnReport')
#     btnR.click()
#     driver.implicitly_wait(1)
#
# except: #otherwise
#     pass
#             #record the link/property information
#
# if btnR:
#     entry = Residential(url, SWIS, driver)
#
# if btnC:
#     entry = Commercial(url, SWIS, driver)
#
# if entry:
#     entry.scr_report()


# btnCReport=None
# try:
#     btnCReport = driver.find_element_by_id('btnReport')
# except:
#     pass
#
# if btnCReport:
#     btnCReport.click()
#     driver.implicitly_wait(1)
#

# def scr_property_info(driver, main_dict):
#     soup = BeautifulSoup(driver.page_source,'lxml')
#     tdList = soup.find_all('td','dataTD')
#
#     landTypes = ["Type","Size"]
#     count=0
#     for td in tdList:
#         if td.contents[0].name=='span':
#             child = td.contents[0]
#             key = child['id'][3:]
#             value = child.string
#         else:
#             key = landTypes[count]
#             value = td.string
#             count+=1
#         main_dict[key] = value



#
# entry = Place(url, driver)

# print(entry.property_dict)



#clear blank lines
#clear 'legal description not given'
#parse out assessment year and price
#parse out size
#convert stuff to integers



# idTable = soup.find(id='pnlLabel')
# datalist = []
# for td in idTable.find_all('td'):
#     print(td.string)
