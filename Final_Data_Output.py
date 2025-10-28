import pandas as pd

class Final_Data:
    def __init__(self):
        self.house_path = 'Houses_Sold.csv'
        self.income_path = 'Income_ZipCode.csv'
        self.population_path = 'Zip_Pop.csv'
        self.homicides_path = 'HHS_homicides.csv'
        self.county_map = 'mapping_County.csv'
    
    def House_filter(self, sold=True, for_sale=True, min_price=None, max_price=None, min_bed=None, max_bed=None, min_bath=None, max_bath = None, min_sqft = None, max_sqft = None):
        houses = pd.read_csv(self.house_path)
        houses.dropna(axis=0, inplace=True)
        if sold != True:
            houses = houses.loc[houses['status']!='sold',]
        if for_sale != True:
            houses = houses.loc[houses['status']!='for_sale',]
        if min_price is not None:
            houses = houses.loc[houses['price'] >= min_price,]
        if max_price is not None:
            houses = houses.loc[houses['price'] <= max_price,]
        if min_bed is not None:
            houses = houses.loc[houses['bed'] >= min_bed,]
        if max_bed is not None:
            houses = houses.loc[houses['bed'] <= max_bed,]
        if min_bath is not None:
            houses = houses.loc[houses['bath'] >= min_bath,]
        if max_bath is not None:
            houses = houses.loc[houses['bath'] <= max_bath,]
        if min_sqft is not None:
            houses = houses.loc[houses['house_size'] >= min_sqft,]
        if max_sqft is not None:
            houses = houses.loc[houses['house_size'] <= max_sqft,]
        return houses
    
    def Income_clean_merge(self):
        Income = pd.read_csv(self.income_path)
        Income = Income.loc[Income['zipcode'] > 0, :]
        Income = Income[['zipcode', 'N1', 'A00100']]
        Income = Income.groupby('zipcode').sum()
        Income['Household_AGI'] = Income['A00100'] / Income['N1']
        return Income
    
    def Population_import(self):
        zip_pop = pd.read_csv(self.population_path)
        zip_pop = zip_pop[['zip_code','Total_Pop']]
        return zip_pop
    
    def Homicides_import(self):
        homicides = pd.read_csv(self.homicides_path)
        homicides = homicides.loc[(homicides['Intent']== 'All_Homicide') & (homicides['Period']=='2023'), ]
        homicides.loc[homicides['Count']=='1-9','Count']= '5'
        homicides.loc[homicides['Count']=='10-50','Count']= '30'
        homicides.loc[ :,'Count'] = homicides.loc[:,'Count'].apply(lambda x: pd.to_numeric(x))
        homicides = homicides[['GEOID', 'NAME', 'ST_NAME', 'Period', 'Count', 'Rate']]
        return homicides
    
    def Merge_all(self, sold=True, for_sale=True, min_price=None, max_price=None, min_bed=None, max_bed=None, min_bath=None, max_bath = None, min_sqft = None, max_sqft = None):
        houses = self.House_filter(sold, for_sale, min_price, max_price, min_bed, max_bed, min_bath, max_bath, min_sqft, max_sqft)
        income = self.Income_clean_merge()
        zip_pop = self.Population_import()
        homicides = self.Homicides_import()
        county_map= pd.read_csv(self.county_map)
        county_map = county_map.rename(columns={'ZIP': 'zip_code'})
        House_Income = houses.merge(income, how='left', left_on='zip_code', right_on='zipcode')
        House_Income_Pop = House_Income.merge(zip_pop, how='left', on='zip_code')
        House_Income_Pop = House_Income_Pop.merge(county_map, how='left', on='zip_code')
        House_Income_Pop_Hom = House_Income_Pop.merge(homicides, how='left', left_on='COUNTYNAME', right_on='NAME')
        return House_Income_Pop_Hom