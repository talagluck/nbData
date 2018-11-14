# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
# import re
import pandas as pd
import os
import datetime
import csv

class Taxes(object):
    def __init__(self, driver, swis, tax_ID,municipality,property_type,url):
        self.driver = driver
        self.swis = swis
        self.tax_ID = tax_ID
        self.municipality = municipality
        self.property_type = property_type
        # self.time_scraped = datetime.datetime.now()
        self.original_url = url
        self.current_url = ''
        self.soup = ''
        self.folder_name = self.municipality + '_taxes_scraped'

        self.summary_header = ['Swis','tax_ID','property_type', 'time_scraped', 'Tax_Year', 'Tax_Type', 'Original_Bill',
                            'Total_Assessed_Value', 'Full_Market_Value',
                            'Uniform_%', 'Roll_Section']
        self.exemptions_header = ['Swis','tax_ID','property_type', 'time_scraped', 'Tax_Year','Code_Description','Amount','Exempt','Start_Year','End_Year','Vflag','Hcode','Own']
        self.taxable_values_header = ['Swis','tax_ID','property_type', 'time_scraped', 'year', 'taxable_type', 'taxable_amount','exemption_amount']
        self.detailed_header = ['Description','Rate','Value','Amount_Due','Swis','tax_ID','property_type', 'time_scraped', 'year','tax_level']
        self.basic_headers = ['Swis','tax_ID','property_type','time_scraped']
        self.exemptions = None
        self.years = []
        self.taxable_values = None
        self.historical_tax = None
        self.detailed_tax = None
        self.detailed_dataframe_list = []
        self.detailed_error_dataframe = pd.DataFrame(columns = self.basic_headers.append('year') )
        self.all_errors = pd.DataFrame(columns = self.basic_headers.append('error_type'))
        self.exemptions_csv = f'{self.folder_name}/{self.municipality}_tax_exemptions.csv'
        self.values_csv = f'{self.folder_name}/{self.municipality}_tax_values.csv'
        self.historical_csv = f'{self.folder_name}/{self.municipality}_tax_historical.csv'
        self.detailed_csv = f'{self.folder_name}/{self.municipality}_tax_detailed.csv'

        try:
            self.exemptions = self.scr_exemptions()
            # print(self.exemptions)
        except:
            self.basic_error_notate('exemptions')

        try:
            self.taxable_values = self.scr_taxable_values()
            # print(self.taxable_values)

        except:
            self.basic_error_notate('taxable_values')

        try:
            self.historical_tax = self.scr_historical_tax_table()
            self.years = self.historical_tax['Tax Year'].unique().tolist()
            # print(self.historical_tax)

        except:
            self.basic_error_notate('historical_tax')

        try:
            self.detailed_tax = self.scr_all_detailed()

        except:
            self.basic_error_notate('detailed')

        self.check_all_for_errors()
        print(self.all_errors)

        self.csv_header = {self.exemptions_csv:self.exemptions_header,self.values_csv:self.taxable_values_header,
                            self.historical_csv:self.summary_header,self.detailed_csv:self.detailed_header}
        self.csv_dataframe = {self.exemptions_csv:self.exemptions,self.values_csv:self.taxable_values,
                            self.historical_csv:self.historical_tax,self.detailed_csv:self.detailed_tax,'error':self.all_errors}

    def basic_error_notate(self,error_type):
        df = pd.DataFrame(columns=['error_type'])
        df = df.append([{'error_type':error_type}])
        self.add_id_columns(df)
        self.all_errors = self.all_errors.append(df)
        print(error_type,"error")

    def add_error_df(self,class_attr_to_check,error_type):
        if class_attr_to_check is None:
            self.basic_error_notate(error_type)

    def check_all_for_errors(self):
        # self.add_error_df(self.exemptions,'exemptions')
        self.add_error_df(self.taxable_values,'taxable_values')
        self.add_error_df(self.historical_tax,'historical_tax')
        if self.detailed_tax is not None:
            if self.detailed_tax.empty:
                df = pd.DataFrame(columns='error_type')
                df = df.append([{'error_type':'detailed'}])
                self.add_id_columns(df)
                self.all_errors = self.all_errors.append(df)


    def add_id_columns(self, df):
        df['Swis'] = self.swis
        df['tax_ID'] = self.tax_ID
        df['property_type'] = self.property_type
        df['time_scraped'] = datetime.datetime.now()

    def get_basic_tax_link(self, url):
        new_url = url.replace('propdetail.aspx?swis','TaxInfo.aspx?SwisCode')
        return new_url

    def get_historical_tax_link(self, url):
        new_url = url.replace('propdetail.aspx?swis','TaxInfo.aspx?SwisCode')+"&Hist=True"
        return new_url

    def get_detailed_tax_link(self,url,year):
        new_url = url.replace('propdetail','taxbill').replace('printkey','sbl') + f'&taxYear={year}'
        return new_url

    def go_to_link(self,url):
        self.driver.get(url)
        self.driver.implicitly_wait(1)
        self.soup = BeautifulSoup(self.driver.page_source, "lxml")

    def scr_exemptions(self):
        to_url = self.get_basic_tax_link(self.original_url)
        if self.current_url != to_url:
            self.go_to_link(to_url)
            self.current_url = to_url
        section = self.soup.find_all('table',{'id':'tblExemptionsCurr'})
        if section:
            table = pd.read_html(str(section[0]),header=0)
            df = pd.DataFrame(table[0])
            self.add_id_columns(df)
            return df
        return None

    def scr_taxable_values(self):
        to_url = self.get_basic_tax_link(self.original_url)
        if self.current_url != to_url:
            self.go_to_link(to_url)
            self.current_url = to_url
        dict = {}
        df = pd.DataFrame(columns = self.taxable_values_header)
        section = self.soup.find_all('table',{'id':'tblTaxableValues'})
        if section:
            rows = section[0].find_all('tr')
            for idx,row in enumerate(rows):
                tds = row.find_all('td')
                if idx==0:
                    dict['year'] = tds[0].get_text()
                else:
                    dict['taxable_type'] = tds[0].get_text().split(" Taxable")[0]
                    dict['taxable_amount'] = tds[1].get_text()
                    dict['exemption_amount'] = tds[3].get_text()
                    self.add_id_columns(dict)
                    df = df.append([dict])
            # self.add_id_columns(df)
            return df
        return None

    def scr_historical_tax_table(self):
        to_url = self.get_historical_tax_link(self.original_url)
        if self.current_url != to_url:
            self.go_to_link(to_url)
            self.current_url = to_url
        section = self.soup.find('table',{'id':'tblSummary'})
        if section:
            table = pd.read_html(str(section),header=0)
            df = pd.DataFrame(table[0])

        section = self.soup.find('table',{'id':'tblHistoricalSummary'})
        if section:
            table = pd.read_html(str(section),header=0)
            data = pd.DataFrame(table[0])
            df = df.append(data)

            df = df[df['Tax Year'].str.contains('Display Details')==False]
            self.add_id_columns(df)
            return df
        return None

    def scr_detailed_tax_info(self,year):
        to_url = self.get_detailed_tax_link(self.original_url, year)
        if self.current_url != to_url:
            self.go_to_link(to_url)
            self.current_url = to_url

        section = self.soup.find('div',{'id':'pnlTaxes'})
        if section:
            df = pd.DataFrame(columns = self.detailed_header)
            main_table = self.soup.find('div',{'id':'pnlTaxes'})

            tables = main_table.find_all('table')
            nonempty_tables = []
            for i in tables:
                if i.find_all('tbody'):
                    if i.find_all('thead'):
                        nonempty_tables.append(i)
            for i in nonempty_tables:
                dict = {}
                header_line1 = i.find('thead')
                body = i.find('tbody')
                head_split = header_line1.find('p').get_text().split(' ')
                dict['year'] = head_split[0]
                dict['tax_level'] = head_split[1]
                for row in body.find_all('tr'):
                    for idx,col in enumerate(row.find_all('td')):
                        if idx<4:
                            dict[self.detailed_header[idx]] = col.get_text()
                    self.add_id_columns(dict)
                    df = df.append([dict])
            self.add_id_columns(df)
            return df
        return None

    def scr_all_detailed(self):
        for year in self.years:
            try:
                self.detailed_dataframe_list.append(self.scr_detailed_tax_info(year))
            # print(self.detailed_dataframe_list)
            except:
                df = pd.DataFrame(columns=['year'])
                df['year'] = year
                self.add_id_columns(df)
                self.detailed_error_dataframe.append(df)
        return pd.concat(self.detailed_dataframe_list,sort=False)

    def create_csv(self,data,csv_filename,headers):
        # data.to_csv(csv_filename,index_label=False,header = self.main_headers)
        with open(csv_filename,'w') as file:
            writer = csv.DictWriter(file, fieldnames = headers)
            writer.writeheader()
            print('header is', headers,'\n')
            print('csv headers',data.columns)
            writer.writerows(data)
    def append_csv(self,data,csv_filename,headers):
        # data.to_csv(csv_filename,mode='a',header=False,index_label=False)
        with open(csv_filename,'a') as file:
            writer=csv.DictWriter(file,fieldnames = headers)
            writer.writerows(data)

    def append_multiple_rows_csv(self, data,csv_filename,headers):
        for row in data:
            self.append_csv(row,csv_filename,headers)
    def create_multiple_rows_csv(self, data,csv_filename,headers):
        print('create multiple rows',data)
        for idx,row in data.iterrows():
            print(row)
            if idx == 0:
                self.create_csv(row,csv_filename,headers)
            else:
                self.append_csv(row,csv_filename,headers)


    def all_csvs(self):
        print('start')

        # self.go_to_detail_tax('2016')
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)
            print('made directory')

        for csv_name, dataframe in self.csv_dataframe.items():
            if csv_name in self.csv_header.keys():
                print(csv_name,dataframe)
                if dataframe is not None:
                    print('not none',csv_name)
                    if os.path.exists(csv_name):
                        # print('exists appending',csv_name)
                        # self.append_multiple_rows_csv(dataframe,csv_name,self.csv_header[csv_name])
                        # print('header',self.csv_header[csv_name])
                        self.append_csv(dataframe,csv_name, self.csv_header[csv_name])
                    else:
                        # print('creating',csv_name)
                        # print(dataframe)
                        # self.create_multiple_rows_csv(dataframe,csv_name,self.csv_header[csv_name])
                        self.create_csv(dataframe,csv_name,self.csv_header[csv_name])


    # if os.path.exists(self.main_csv):
    #     self.append_csv(self.scr_all_main(),self.main_csv,self.main_headers)
    # else:
    #     self.create_csv(self.scr_all_main(),self.main_csv,self.main_headers)
    #
    # if os.path.exists(self.owners_csv):
    #     self.append_multiple_rows_csv(self.scr_owners(),self.owners_csv,self.owners_headers)
    #     # self.append_csv(self.scr_owners(),self.owners_csv,self.owners_headers)
    # else:
    #     self.create_multiple_rows_csv(self.scr_owners(),self.owners_csv,self.owners_headers)
    #
    #     # self.create_csv(self.scr_owners(),self.owners_csv,self.owners_headers)
    #
    # transposed_data_to_export = self.scr_all_transposed()
    # for transposed_dict in transposed_data_to_export:
    #     for dict_name,dict in transposed_dict.items():
    #         cur_filename = self.transposed_csv_names[dict_name]
    #         cur_header = self.transposed_headers[dict_name]
    #
    #         if dict:
    #             if os.path.exists(cur_filename):
    #                 self.append_multiple_rows_csv(dict,cur_filename, cur_header)
    #             else:
    #                 self.create_multiple_rows_csv(dict,cur_filename, cur_header)
