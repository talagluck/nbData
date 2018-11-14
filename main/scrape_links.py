from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os

import csv

from Classes.Grab_Links import Grab_Links

url = "http://propertydata.orangecountygov.com/viewlist.aspx?sort=printkey&swis=3350&page=1"
options = webdriver.ChromeOptions()
# options.add_argument('headless')

driver = webdriver.Chrome(chrome_options=options)
driver.get(url)

btnPublicAccess=None
btnC = None
btnR = None
try:
    btnPublicAccess = driver.find_element_by_id('btnPublicAccess')
except:
    pass

if btnPublicAccess:
    btnPublicAccess.click()
    driver.implicitly_wait(1)

def get_all_links(url, driver, csv_filename):
    link_grabber = Grab_Links(url,driver,csv_filename)
    while link_grabber.next:
        link_grabber.grab_property_links()
        link_grabber.next_page()
    link_grabber.remove_dupes()

get_all_links(url, driver, "tuxedo_links2.csv")

driver.quit()
# print (json.dumps(entry.main_dict, indent=1))

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
