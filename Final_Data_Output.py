import pandas as pd
import numpy as np

class Final_Data:
    def __init__(self):
        self.house_path = 'Houses_Sold.csv'
        self.income_path = 'Income_ZipCode.csv'
        self.population_path = 'Zip_Pop.csv'
        self.homicides_path = 'HHS_homicides.csv'
        self.county_map = 'mapping_County.csv'
    
    def House_filter(self, sold=True, for_sale=True, min_price=None, max_price=None, min_bed=None, max_bed=None, min_bath=None, max_bath = None, min_sqft = None, max_sqft = None, min_acre = None, max_acre = None):
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
        if min_acre is not None:
            houses = houses.loc[houses['acre_lot'] >= min_acre]
        if max_acre is not None:
            houses = houses.loc[houses['acre_lot'] <= max_acre]
        return houses
    
    def Income_clean_merge(self):
        Income = pd.read_csv(self.income_path)
        Income = Income.loc[Income['zipcode'] > 0, :]
        Income = Income[['zipcode', 'N1', 'A00100']]
        Income = Income.groupby('zipcode').sum()
        Income['Household_AGI'] = Income['A00100'] / Income['N1']
        Income.rename(columns={'N1': 'Households', 'A00100': 'Total_AGI'}, inplace=True)
        Income = Income[['Households', 'Total_AGI', 'Household_AGI']]
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
        homicides['Count'] = homicides['Count'].astype(float)
        homicides = homicides[['GEOID', 'NAME', 'ST_NAME', 'Period', 'Count', 'Rate']]
        homicides.rename(columns={'NAME': 'County_Name', 'ST_NAME': 'State', 'Count': 'Homicides'}, inplace=True)
        return homicides

    def County_import(self):
        county_map= pd.read_csv(self.county_map)
        county_map = county_map.loc[county_map['tot_ratio'] >= 0.5,]
        county_map = county_map.loc[county_map['res_ratio'] >= 0.5,]
        county_map.rename(columns={'zip': 'zip_code', 'geoid': 'GEOID'}, inplace=True)
        return county_map
    
    def feature_engineering(self, df):
        """Add engineered features optimized for house recommender system"""
        
        # LIVABILITY SCORES (Important for family recommendations)
        df['bed_bath_ratio'] = df['bed'] / (df['bath'] + 0.5)  # Optimal ratio ~1.5-2
        
        # ECONOMIC ENVIRONMENT (Area prosperity indicators)
        df['economic_health'] = df['Household_AGI'] / (df['Total_Pop'] + 1) * 1000  # Income per capita scaled
        
        # INVESTMENT POTENTIAL INDICATORS
        df['lot_to_house_ratio'] = df['acre_lot'] / (df['house_size'] / 43560)  # Convert sqft to acres
        
        # LOG TRANSFORMATIONS
        df['log_price'] = np.log1p(df['price'])
        df['log_income'] = np.log1p(df['Household_AGI'])
        df['log_house_size'] = np.log1p(df['house_size'])
        
        return df
    
    def Merge_all(self, sold=True, for_sale=True, min_price=None, max_price=None, min_bed=None, max_bed=None, min_bath=None, max_bath = None, min_sqft = None, max_sqft = None, min_acre = None, max_acre = None):
        houses = self.House_filter(sold, for_sale, min_price, max_price, min_bed, max_bed, min_bath, max_bath, min_sqft, max_sqft, min_acre, max_acre)
        income = self.Income_clean_merge()
        zip_pop = self.Population_import()
        homicides = self.Homicides_import()
        county_map= self.County_import()
        
        House_Income = houses.merge(income, how='left', left_on='zip_code', right_on='zipcode')
        House_Income_Pop = House_Income.merge(zip_pop, how='left', on='zip_code')
        House_Income_Pop = House_Income_Pop.merge(county_map, how='left', on='zip_code')
        House_Income_Pop_Hom = House_Income_Pop.merge(homicides, how='left', on='GEOID')

        # return House_Income_Pop_Hom        
        # Apply feature engineering
        eng_df = self.feature_engineering(House_Income_Pop_Hom)

        analysis_columns = ['bed', 'bath', 'house_size', 'acre_lot', 'zip_code', 'Household_AGI', 'Total_Pop', 'Homicides', 'bed_bath_ratio', 'economic_health', 'lot_to_house_ratio', 'log_price']
        df = eng_df[analysis_columns]
        df = df.dropna()

        Q1 = np.quantile(df, 0.25, axis=0)
        Q3 = np.quantile(df, 0.75, axis=0)
        IQR =  Q3 - Q1
        lower = Q1 - 3 * IQR
        upper = Q3 + 3 * IQR

        i = 0
        for col in analysis_columns:
            df = df[(df[col] >= lower[i]) & (df[col] <= upper[i])]
            i += 1
        
        clean_df = df.reset_index(drop=True)
        
        return clean_df