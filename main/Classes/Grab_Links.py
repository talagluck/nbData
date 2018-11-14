from bs4 import BeautifulSoup
import csv
import selenium
import pandas as pd
import os

class Grab_Links(object):
    def __init__(self,starting_url,driver,municipality):
        self.driver = driver
        self.url = starting_url
        self.soup = BeautifulSoup(self.driver.page_source,'lxml')
        self.list_of_links = {}
        self.next = self.url
        self.headers = ["swis","tax_ID","owner","link", "street_name"]
        self.municipality = municipality
        self.csv_filename = municipality + "_links.csv"
        self.init_csv()

    def init_csv(self):
        with open(self.csv_filename,"w") as file:
            csv_writer = csv.DictWriter(file,fieldnames=self.headers)
            csv_writer.writeheader()

    def grab_property_links(self):
        table = self.soup.find('table',{'id':'tblList'})
        rows = table.find_all('tr')

        all_page_links ={}
        for row in rows:
            new_line = {}
            link = "http://propertydata.orangecountygov.com/"
            columns = row.find_all('td')
            if columns[0].get('id') == 'cellSwis':
                title_row = row.find_all('td')
            else:
                for idx, cell in enumerate(columns):
                    value = cell.get_text()
                    if idx == 0: #get just the swis number and remove city name
                        value = value.split(' ')[0]
                    if idx == 1: #get rid of the extra space at the end of the tax id
                        value = value.strip()
                        link += cell.find('a').get('href')
                    if idx == 3: #get the link
                        value = link
                    new_line[self.headers[idx]]=value
                all_page_links[link] = new_line

        with open(self.csv_filename,"a") as file:
            csv_writer = csv.DictWriter(file, fieldnames=self.headers)
            for key,value in all_page_links.items():
                csv_writer.writerow(value)
        print("Page", self.driver.current_url.split('page=')[1],"scraped")

    def next_page(self):
        try:
            self.next = self.driver.find_element_by_id('lnkNextPage')
        except:
            self.next=None
        if self.next:
            self.next.click()
            self.driver.implicitly_wait(1)
            self.soup = BeautifulSoup(self.driver.page_source,'lxml')
            return True
        else:
            return False

    def remove_dupes(self):
        data = pd.read_csv(self.csv_filename)
        data = data.drop_duplicates(subset='tax_ID')
        data.to_csv(self.csv_filename, index_label=False)
        print("Duplicates removed")
