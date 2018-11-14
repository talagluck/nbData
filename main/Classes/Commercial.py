from bs4 import BeautifulSoup
import os
import pandas as pd
import datetime
from Classes.Building import Building



class Commercial(Building):
    def __init__(self, driver, swis, tax_ID,municipality):
        self.property_type = "commercial"
        super().__init__(driver, swis, tax_ID,municipality,self.property_type)
        self.main_sections = ['property_info','pnlUtil','pnlInve']
        self.transposed_sections = {'pnlSale':'sales','pnlBuil':'buildings','pnlUses':'site_uses','pnlImpr':'improvements','pnlLand':'land_types','ucSpecialDistricts':'special_districts','pnlExem':'exemptions','pnlTax':'taxes'}
        self.buildings = f'{self.folder_name}/{self.municipality}_buildings.csv'
        self.site_uses = f'{self.folder_name}/{self.municipality}_site_uses.csv'
        self.transposed_csv_names = {'sales':self.sales,'buildings':self.buildings,'site_uses':self.site_uses,'improvements':self.improvements,'land_types':self.land_types,'special_districts':self.special_districts,'exemptions':self.exemptions,'taxes':self.taxes}
        self.check_boxes()
        
