from bs4 import BeautifulSoup
import os
import pandas as pd
import datetime
from Classes.Building import Building


class Residential(Building):
    def __init__(self, driver, swis, tax_ID,municipality):
        self.property_type = "residential"
        super().__init__(driver, swis, tax_ID,municipality,self.property_type)
        self.main_sections = ['property_info','pnlArea','pnlStru','pnlUtil']
        self.transposed_sections = {'pnlSale':'sales','pnlImpr':'improvements','pnlLand':'land_types','ucSpecialDistricts':'special_districts','pnlExem':'exemptions','pnlTax':'taxes'}
        self.transposed_csv_names = {'sales':self.sales,'improvements':self.improvements,'land_types':self.land_types,'special_districts':self.special_districts,'exemptions':self.exemptions,'taxes':self.taxes}
        self.check_boxes()
        # initialize dataframes for each csv. Then:
            #if it's the first item in the links csv:
                #make the directory for the municipality
                #output each one to a new csv
            #else:
                #append each dataframe to each csv
