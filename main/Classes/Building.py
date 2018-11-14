from bs4 import BeautifulSoup
import os
import pandas as pd
import datetime
import csv

class Building(object):
    def __init__(self, driver, swis, tax_ID,municipality,property_type):
        self.driver = driver
        # self.url = url
        self.soup = BeautifulSoup(self.driver.page_source,'lxml')
        self.property_type = property_type
        self.sales_dicts = []
        self.improvements_dicts = []
        self.exemptions_dicts = []
        self.swis = swis
        self.tax_ID = tax_ID
        self.time_scraped = datetime.datetime.now()
        self.municipality = municipality
        self.folder_name = self.municipality + '_scraped'
        self.main_csv = f'{self.folder_name}/{self.municipality}_main.csv'
        self.owners_csv = f'{self.folder_name}/{self.municipality}_owners.csv'
        self.sales = f'{self.folder_name}/{self.municipality}_sales.csv'
        self.improvements = f'{self.folder_name}/{self.municipality}_improvements.csv'
        self.land_types = f'{self.folder_name}/{self.municipality}_land_types.csv'
        self.special_districts = f'{self.folder_name}/{self.municipality}_special_districts.csv'
        self.exemptions = f'{self.folder_name}/{self.municipality}_exemptions.csv'
        # self.taxes = f'{self.folder_name}/{self.municipality}_taxes.csv'

        self.buildings = f'{self.folder_name}/{self.municipality}_buildings.csv'
        self.site_uses = f'{self.folder_name}/{self.municipality}_site_uses.csv'

        self.main_sections = ['property_info','pnlArea','pnlStru','pnlUtil','pnlInve']

        self.transposed_sections = {'pnlSale':'sales','pnlBuil':'buildings','pnlUses':'site_uses','pnlImpr':'improvements','pnlLand':'land_types','ucSpecialDistricts':'special_districts','pnlExem':'exemptions'}
        self.transposed_csv_names = {'sales':self.sales,'buildings':self.buildings,'site_uses':self.site_uses,'improvements':self.improvements,'land_types':self.land_types,'special_districts':self.special_districts,'exemptions':self.exemptions}
        #main headers
        self.main_headers = ['Status', 'RollSection', 'Swis', 'tax_ID', 'BasePropClass', 'Site', 'AgDistrict', 'SitePropertyClass', 'ZoningCode',
                            'NeighborhoodCode', 'TotalAcreage', 'SchoolDist', 'LandAssessment', 'TotalAssessment','FullMarketValue', 'EqualizationRate',
                            'LegalPropertyDesc', 'DeedBook', 'DeedPage', 'GridEast', 'GridNorth','CSewerType', 'CWaterSupply', 'CUtilities','RSewerType',
                            'RWaterSupply', 'RUtilities', 'RHeatType', 'RFuelType', 'RCentralAir','LivingArea', 'FirstStoryArea', 'SecondStoryArea',
                            'HalfStoryArea', 'AdditionalStoryArea', '34StoryArea', 'FinishedBasement', 'NumberOfStories', 'FinishedRecRoom', 'FinishedOverGarage',
                            'BuildingStyle', 'Bathrooms', 'Bedrooms', 'Kitchens', 'FirePlaces', 'BasementType', 'PorchType', 'PorchArea', 'BasementGarageCap',
                            'AttachedGarageCap', 'OverallCondition', 'OverallGrade', 'YearBuilt','EffYearBuilt', 'Condition', 'Grade', 'Desirability']

        self.main_headers.extend(['time_scraped', 'property_photo', 'property_type'])

        #owners headers
        self.owners_headers = ['time_scraped', 'property_type','tax_ID','Swis', 'owner','address']

        self.sales_headers = ['time_scraped', 'property_type','tax_ID','Swis','Sale_Date', 'Price', 'Property_Class', 'Sale_Type', 'Prior_Owner', 'Value_Usable', 'Arms_Length', 'Addl._Parcels', 'Deed_Book_and_Page']
        self.buildings_headers = ['time_scraped', 'property_type','tax_ID','Swis','AC%', 'Sprinkler%', 'Alarm%', 'Elevators', 'Basement_Type', 'Year_Built', 'Condition', 'Quality', 'GrossFloor_Area(sqft)', 'Stories']
        self.site_uses_headers = ['time_scraped', 'property_type','tax_ID','Swis','Use', 'Rentable_Area_(sqft)', 'Total_Units']
        self.improvements_headers = ['time_scraped', 'property_type','tax_ID','Swis','Structure', 'Size', 'Grade', 'Condition', 'Year']
        self.land_types_headers = ['time_scraped', 'property_type','tax_ID','Swis','Type', 'Size']
        self.special_districts_headers =['time_scraped', 'property_type','tax_ID','Swis','Description', 'Units', 'Percent', 'Type', 'Value']
        self.exemptions_headers = ['time_scraped', 'property_type','tax_ID','Swis','Year', 'Description', 'Amount', 'Exempt%', 'Start_Yr', 'End_Yr', 'V_Flag', 'H_Code', 'Own%']
        self.transposed_headers = {'sales':self.sales_headers,'buildings':self.buildings_headers,'site_uses':self.site_uses_headers,'improvements':self.improvements_headers,'land_types':self.land_types_headers,'special_districts':self.special_districts_headers,'exemptions':self.exemptions_headers}



        self.check_boxes()


        # initialize dataframes for each csv. Then:
            #if it's the first item in the links csv:
                #make the directory for the municipality
                #output each one to a new csv
            #else:
                #append each dataframe to each csv

    def __repr__(self):
        return self.swis, self.tax_ID

    def click_button(self, button_name):
        button=None
        try:
            button = self.driver.find_element_by_id(button_name)
        except:
            pass
        if button:
            button.click()
            self.driver.implicitly_wait(1)
            return True
        else:
            return False

    def scr_main(self, section_name ):
        section_dict = {'time_scraped':self.time_scraped,'property_type':self.property_type}
        # section_name = self.main_sections[section_index]
        section = self.soup.find_all('div',{'id':section_name})
        if section:
            section = section[0].find_all('td')
            dataClass = False
            for td in section:
                for attr in td.attrs:
                    if attr == 'class' and td.attrs[attr]==['data']:
                        dataClass=True
                    elif attr == 'id' and td.attrs[attr]=='photo_cell':
                        if td.img:
                            section_dict['property_photo']= "http://propertydata.orangecountygov.com/"+ td.img['src']
                        else:
                            section_dict['property_photo']= "N/A"

                if dataClass==True:
                    if len(list(td.descendants))>0 and list(td.descendants)[0]!=u'\xa0':
                        section_dict[td.contents[0]['id'][3:].replace('TaxMapNum','tax_ID')]= td.contents[0].string
                    dataClass=False
        return section_dict

    def scr_all_main(self):
        main_dict = {}
        for section in self.main_sections:
            main_dict.update(self.scr_main(section))
        # df = pd.DataFrame.from_dict([main_dict])
        # return df
        return main_dict

    def scr_owners(self):
        #make sure swis/link information is included in this dictionary
        owners_list = []
        owners = self.soup.find_all('div',{'class':'owner_info'})
        for owner in owners:
            owners_dict = {'Swis':self.swis,'tax_ID':self.tax_ID,'time_scraped':self.time_scraped,'property_type':self.property_type}
            owner_text = owner.get_text(separator=",",strip=True).split(',',1)
            owners_dict['owner'] = owner_text[0]
            owners_dict['address'] = owner_text[1]
            owners_list.append(owners_dict)
            # df = pd.DataFrame.from_dict(owners_list)
        # return df
        return owners_list

    def scr_transposed(self, section_name):
        # section_name = self.transposed_sections[section_index]
        item_list = []
        table = self.soup.find('div',{'id':section_name})
        if table:
            for index,row in enumerate(table.find_all('tr')):
                table_dict = {'Swis':self.swis,'tax_ID':self.tax_ID,'time_scraped':self.time_scraped,'property_type':self.property_type}
                if index==0:
                    title = row.find_all('th')
                else:
                    cur_row = row.find_all('td')
                    for i, column in enumerate(cur_row):
                        if title[i].get_text():
                            key = title[i].get_text(strip=True).replace(u'\xd7','x').replace(u'\xa0','').replace(' ','_')
                            value = cur_row[i].get_text(strip=True).replace(u'\xd7','x').replace(u'\xa0','')
                            table_dict[key] = value
                    item_list.append(table_dict)
        df = pd.DataFrame.from_dict(item_list)
        return {self.transposed_sections[section_name]: item_list}
        #append this to the transposed tables dictionary, then i can output those all in the end
        # self.main_dict[section_name] = item_list

    def scr_all_transposed(self):
        transposed_list = []
        for section in self.transposed_sections:
            transposed_list.append(self.scr_transposed(section))
        return transposed_list #list of dataframes

    def scr_taxes(self):
        pass

    def check_boxes(self):
        checkboxes = self.soup.find_all(attrs={'type':'checkbox'})
            # print(len(checkboxes))
        for checkbox in checkboxes:
            # print(checkbox.attrs)
            if 'checked' not in checkbox.attrs:
                btn = self.driver.find_element_by_id(checkbox.attrs['name'])
                btn.click()

    def create_csv(self,data,csv_filename,headers):
        # data.to_csv(csv_filename,index_label=False,header = self.main_headers)
        with open(csv_filename,'w') as file:
            writer = csv.DictWriter(file, fieldnames = headers)
            writer.writeheader()
            writer.writerow(data)
    def append_csv(self,data,csv_filename,headers):
        # data.to_csv(csv_filename,mode='a',header=False,index_label=False)
        with open(csv_filename,'a') as file:
            writer=csv.DictWriter(file,fieldnames = headers)
            writer.writerow(data)

    def append_multiple_rows_csv(self, data,csv_filename,headers):
        for row in data:
            self.append_csv(row,csv_filename,headers)
    def create_multiple_rows_csv(self, data,csv_filename,headers):
        for idx,row in enumerate(data):
            if idx == 0:
                self.create_csv(row,csv_filename,headers)
            else:
                self.append_csv(row,csv_filename,headers)




    def all_csvs(self):
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)

        if os.path.exists(self.main_csv):
            self.append_csv(self.scr_all_main(),self.main_csv,self.main_headers)
        else:
            self.create_csv(self.scr_all_main(),self.main_csv,self.main_headers)

        if os.path.exists(self.owners_csv):
            self.append_multiple_rows_csv(self.scr_owners(),self.owners_csv,self.owners_headers)
            # self.append_csv(self.scr_owners(),self.owners_csv,self.owners_headers)
        else:
            self.create_multiple_rows_csv(self.scr_owners(),self.owners_csv,self.owners_headers)

            # self.create_csv(self.scr_owners(),self.owners_csv,self.owners_headers)

        transposed_data_to_export = self.scr_all_transposed()
        for transposed_dict in transposed_data_to_export:
            for dict_name,dict in transposed_dict.items():
                cur_filename = self.transposed_csv_names[dict_name]
                cur_header = self.transposed_headers[dict_name]

                if dict:
                    if os.path.exists(cur_filename):
                        self.append_multiple_rows_csv(dict,cur_filename, cur_header)
                    else:
                        self.create_multiple_rows_csv(dict,cur_filename, cur_header)





    # def init_all_csv(self):
    #     if not os.path.exists(self.folder_name):
    #         os.mkdir(self.folder_name)
    #     main_data_to_export = self.scr_all_main()
    #     main_data_to_export.to_csv(self.main_csv)
    #
    #     owners_data_to_export = self.scr_owners()
    #     owners_data_to_export.to_csv(self.owners_csv)
    #
    #     transposed_data_to_export = self.scr_all_transposed()
    #     for transposed_dict in transposed_data_to_export:
    #         for df_name,df in transposed_dict.items():
    #             cur_filename = self.transposed_csv_names[df_name]
    #             df.to_csv(cur_filename)
    #
    # def append_to_all_csvs(self):
    #     main_data_to_export = self.scr_all_main()
    #     if main_data_to_export:
    #         main_data_to_export.to_csv(self.main_csv,mode='a',header=False)
    #
    #     owners_data_to_export = self.scr_owners()
    #     if owners_data_to_export:
    #         owners_data_to_export.to_csv(self.owners_csv, mode ='a',header=False)
    #
    #     transposed_data_to_export = self.scr_all_transposed()
    #     for transposed_dict in transposed_data_to_export:
    #         for df_name,df in transposed_dict.items():
    #             if df:
    #                 df.to_csv(cur_filename,mode='a',header=False)

    # def scr_report(self):
    #     #if button click doesn't work for some reason
    #     self.click_button('btnCReport')
    #     while True:
    #         if not self.click_button('btnCReport'):
    #             break
    #
    #     #check all unchecked checkboxes
    #     self.soup = BeautifulSoup(self.driver.page_source,'lxml')
    #     checkboxes = self.soup.find_all(attrs={'type':'checkbox'})
    #     # print(len(checkboxes))
    #     for checkbox in checkboxes:
    #         # print(checkbox.attrs)
    #         if 'checked' not in checkbox.attrs:
    #             btn = self.driver.find_element_by_id(checkbox.attrs['name'])
    #             btn.click()
    #
    #     #reset soup after checking boxes and adding fields
    #     self.soup = BeautifulSoup(self.driver.page_source,'lxml')
    #
    #     #scrape top section
    #     for idx, section in enumerate(self.main_sections):
    #         self.scr_main(idx)
    #
    #     for idx, section in enumerate(self.transposed_sections):
    #         self.scr_transposed(idx)
    #
    #     self.main_dict["owners"] = self.scr_owners()









    # def scr_property_info(self):
    #     tdList = self.soup.find_all('td','dataTD')
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
    #         self.main_dict[key] = value

    # def scr_owner_sales_info(self):
    #     btnCOwner = self.driver.find_element_by_id('btnCOwner')
    #     btnCOwner.click()
    #
    #     self.driver.implicitly_wait(1)
    #     self.soup = BeautifulSoup(self.driver.page_source,'lxml')
    #
    #
    #     ownerTable = self.soup.find(id='tblOwnerShip')
    #     ownerRows = ownerTable.find_all('tr')
    #     owners=[]
    #     for i,row in enumerate(ownerRows):
    #         if i > 0:
    #             owner={}
    #             cols = row.find_all('td')
    #
    #             address = cols[1].contents
    #             address = [line.string for line in address if line.name!='br' ]
    #
    #             # for i in address:
    #             #     print(i, type(i))
    #             numberKey = 'Owner Number'
    #             nameKey = 'Name'
    #             nameValue=cols[0].string
    #             address1Key = 'Address-Line1'
    #             address2Key = 'Address-Line2'
    #             address1Value = address[0]
    #             address2Value = address[1]
    #             owner[numberKey] = i
    #             owner[nameKey] = nameValue
    #             owner[address1Key] = address1Value
    #             owner[address2Key] = address2Value
    #             owners.append(owner)
    #     # print (json.dumps(owners, indent=1))
    #     self.main_dict['owner_info'] = owners


            # else:
            #     break

    # def scr_inventory(self):
    #     btnCInventory = self.driver.find_element_by_id('btnCInventory')
    #     btnCInventory.click()
    #
    #     self.driver.implicitly_wait(1)
    #     self.soup = BeautifulSoup(self.driver.page_source,'lxml')
    #
    #     table_panel = self.soup.find_all('div','pnlCInventory')
    #     tables = tablepanel.find_all('table')
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
    #         self.main_dict[key] = value
