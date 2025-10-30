import pandas as pd
import numpy as np

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

    def County_import(self):
        county_map= pd.read_csv(self.county_map)
        county_map = county_map.loc[county_map['tot_ratio'] >= 0.5,]
        county_map = county_map.loc[county_map['res_ratio'] >= 0.5,]
        county_map.rename(columns={'zip': 'zip_code', 'geoid': 'GEOID'}, inplace=True)
        return county_map
    
    def feature_engineering(self, df):
        """Add engineered features optimized for house recommender system"""
        
        # 1. AFFORDABILITY METRICS (Critical for recommendations)
        df['price_to_income_ratio'] = df['price'] / (df['Household_AGI'] + 1)  # Avoid division by zero
        df['affordability_score'] = np.where(df['price_to_income_ratio'] <= 3, 'Affordable',
                                   np.where(df['price_to_income_ratio'] <= 5, 'Moderate', 'Expensive'))
        
        # 2. VALUE METRICS (Key for investment decisions)
        df['price_per_sqft'] = df['price'] / (df['house_size'] + 1)
        df['value_tier'] = pd.qcut(df['price_per_sqft'], q=5, labels=['Budget', 'Economy', 'Mid-Range', 'Premium', 'Luxury'])
        
        # 3. LIVABILITY SCORES (Important for family recommendations)
        df['total_rooms'] = df['bed'] + df['bath']
        df['bed_bath_ratio'] = df['bed'] / (df['bath'] + 0.5)  # Optimal ratio ~1.5-2
        df['space_per_room'] = df['house_size'] / (df['total_rooms'] + 1)
        df['family_suitability'] = np.where((df['bed'] >= 3) & (df['bath'] >= 2) & (df['house_size'] >= 1500), 
                                           'Family-Friendly', 'Compact')
        
        # 4. ECONOMIC ENVIRONMENT (Area prosperity indicators)
        df['economic_health'] = df['Household_AGI'] / (df['Total_Pop'] + 1) * 1000  # Income per capita scaled
        df['area_prosperity'] = pd.qcut(df['economic_health'], q=4, 
                                      labels=['Emerging', 'Developing', 'Established', 'Affluent'])
        
        # 5. SAFETY & LOCATION QUALITY
        # Handle missing homicide data
        df['Count'] = df['Count'].fillna(0)
        df['safety_score'] = np.where(df['Count'] <= 5, 'Very Safe',
                            np.where(df['Count'] <= 15, 'Safe',
                            np.where(df['Count'] <= 30, 'Moderate', 'Caution')))
        
        # Population density (lifestyle indicator)
        df['population_density'] = df['Total_Pop'] / (df['acre_lot'] + 0.1)
        df['lifestyle_type'] = np.where(df['population_density'] < 50, 'Rural',
                              np.where(df['population_density'] < 200, 'Suburban', 'Urban'))
        
        # 6. INVESTMENT POTENTIAL INDICATORS
        df['lot_to_house_ratio'] = df['acre_lot'] / (df['house_size'] / 43560)  # Convert sqft to acres
        df['expansion_potential'] = np.where(df['lot_to_house_ratio'] > 2, 'High', 
                                   np.where(df['lot_to_house_ratio'] > 1, 'Medium', 'Low'))
        
        # 7. REGIONAL MARKET SEGMENTS
        df['zip_region'] = df['zip_code'].astype(str).str[0]  # First digit of zip code
        df['state_market'] = df['ST_NAME']
        
        # 8. COMPOSITE SCORES FOR RECOMMENDATIONS
        # Normalize key metrics for scoring (0-100 scale)
        df['affordability_numeric'] = 100 - np.clip((df['price_to_income_ratio'] - 2) * 25, 0, 100)
        df['value_numeric'] = 100 - pd.qcut(df['price_per_sqft'], q=100, labels=False)
        df['safety_numeric'] = 100 - np.clip(df['Count'] * 3, 0, 100)
        
        # Overall recommendation score
        df['recommendation_score'] = (df['affordability_numeric'] * 0.4 + 
                                    df['value_numeric'] * 0.3 + 
                                    df['safety_numeric'] * 0.3)
        
        # 9. USER PREFERENCE SEGMENTS
        df['buyer_profile'] = np.where((df['bed'] <= 2) & (df['bath'] <= 2) & (df['price'] < df['price'].quantile(0.4)), 'First-Time Buyer',
                             np.where((df['bed'] >= 4) & (df['bath'] >= 3) & (df['house_size'] >= 2500), 'Family Buyer',
                             np.where(df['price'] >= df['price'].quantile(0.8), 'Luxury Buyer', 'Move-Up Buyer')))
        
        # 10. LOG TRANSFORMATIONS
        df['log_price'] = np.log1p(df['price'])
        df['log_income'] = np.log1p(df['Household_AGI'])
        df['log_house_size'] = np.log1p(df['house_size'])
        
        return df
    
    def Merge_all(self, sold=True, for_sale=True, min_price=None, max_price=None, min_bed=None, max_bed=None, min_bath=None, max_bath = None, min_sqft = None, max_sqft = None):
        houses = self.House_filter(sold, for_sale, min_price, max_price, min_bed, max_bed, min_bath, max_bath, min_sqft, max_sqft)
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
        final_df = self.feature_engineering(House_Income_Pop_Hom)
        
        return final_df