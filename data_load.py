
import kagglehub
import os
import pandas as pd
from census import Census

class Data:
    def __init__(self):
        self.houses = "ahmedshahriarsakib/usa-real-estate-dataset"
        self.taxes = 'https://www.irs.gov/pub/irs-soi/22zpallagi.csv'
        self.homicides = 'https://data.cdc.gov/api/views/psx4-wq38/rows.csv?accessType=DOWNLOAD'
        self.population = "2ac3fdb294a41d863f6d7e206982fe0b83bdf248"
        self.county_map = "danofer/zipcodes-county-fips-crosswalk"

    def HOMES_FOR_SALE(self):
        path = kagglehub.dataset_download(self.houses)
        for file in os.listdir(path):
            if file.endswith(".csv"):
                csv_path = os.path.join(path, file)
                print("Loading:", csv_path)
                df = pd.read_csv(csv_path)
                break
        return df.to_csv('Houses_Sold.csv')
    
    def INCOME(self):
        irs = pd.read_csv(self.taxes)
        return irs.to_csv('Income_ZipCode.csv')
    
    def HOMICIDES(self):
        HHS = pd.read_csv(self.homicides)
        return HHS.to_csv('HHS_homicides.csv')
    
    def POPULATION(self):
        c = Census(self.population)
        data = c.acs5.get(('B01003_001E', 'NAME'), {'for': 'zip code tabulation area:*'})
        df = pd.DataFrame(data)
        df.rename(columns={'B01003_001E': 'Total_Pop', 'zip code tabulation area': 'zip_code'}, inplace=True)
        return df.to_csv("Zip_Pop.csv", index=False)
    
    def ZIP_COUNTY(self):
        path = kagglehub.dataset_download(self.county_map)
        for file in os.listdir(path):
            if file.endswith(".csv"):
                csv_path = os.path.join(path, file)
                print("Loading:", csv_path)
                df = pd.read_csv(csv_path)
                break
        return df.to_csv('mapping_County.csv')