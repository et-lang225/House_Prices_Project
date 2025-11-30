import pandas as pd
import numpy as np
import itertools
import statsmodels.api as sm
from statsmodels.regression.mixed_linear_model import MixedLMResults, MixedLMResultsWrapper

class Client_Opt:
    def __init__(self, df, model, scale_fit):
        self.zips = list(df['zip_code'].unique())
        self.pred_df = pd.DataFrame()
        for z in self.zips:
            self.Household_AGI = df.loc[df['zip_code'] == z, 'Household_AGI'].unique()
            self.Total_Pop = df.loc[df['zip_code'] == z, 'Total_Pop'].unique()
            self.Homicides = df.loc[df['zip_code'] == z, 'Homicides'].unique()
            all_permutations = list(itertools.product(self.Household_AGI, self.Total_Pop, self.Homicides, [z]))
            temp_df = pd.DataFrame(all_permutations, columns=['Household_AGI', 'Total_Pop', 'Homicides', 'zip_code'])
            self.pred_df = pd.concat([self.pred_df, temp_df], ignore_index=True)
        self.pred_df = self.pred_df.drop_duplicates().reset_index(drop=True)
        self.mod = model
        self.scale = scale_fit
        
    
    def Client_prediction(self, beds=input("bedrooms you would like:"), baths=input("bathrooms you would like:"),
                    sqft=input("square footage you would like:"), acre_lot=input("acreage you would like (acre=sqft/43,560):")):
        print(f"Chosen Bedrooms: {beds}")
        print(f"Chosen Bathrooms: {baths}")
        print(f"Chosen Square Footage: {sqft}")
        print(f"Chosen Square Footage: {acre_lot}")
        self.pred_df['bed'] = float(beds)
        self.pred_df['bath'] = float(baths)
        self.pred_df['house_size'] = float(sqft)
        self.pred_df['acre_lot'] = float(acre_lot)
        self.pred_df['bed_bath_ratio'] = self.pred_df['bed'] / (self.pred_df['bath'] + 0.5)  # Optimal ratio ~1.5-2
        self.pred_df['economic_health'] = self.pred_df['Household_AGI'] / (self.pred_df['Total_Pop'] + 1) * 1000
        self.pred_df['lot_to_house_ratio'] = self.pred_df['acre_lot'] / (self.pred_df['house_size'] / 43560)  # Convert sqft to acres
        self.pred_df['zip_code'] = self.pred_df['zip_code'].astype(float)
        self.pred_df = self.pred_df[['bed', 'bath', 'house_size', 'acre_lot', 'zip_code', 'Household_AGI', 'Total_Pop', 'Homicides', 'bed_bath_ratio', 'economic_health', 'lot_to_house_ratio']]
        num_cols = self.pred_df.drop(columns=['zip_code']).columns
        num_df_scaled = pd.DataFrame(self.scale.transform(self.pred_df[num_cols]), index=self.pred_df.index, columns=num_cols)
        fit_df = pd.concat([num_df_scaled, self.pred_df[['zip_code']]], axis=1)        
        if hasattr(self.mod, "random_effects"):
            re = pd.DataFrame(self.mod.random_effects).T.reset_index()
            re.columns = ['zip_code', 'random_effect']
            re['zip_code'] = re['zip_code'].astype(float)
            re_df = fit_df[['zip_code']].merge(re, on='zip_code', how='left')
            exog = fit_df.drop(columns=['zip_code'])
            exog = sm.add_constant(exog, has_constant='add')
            exog = exog[self.mod.model.exog_names]
            self.pred_df['Predicted_Price'] = np.exp(self.mod.predict(exog=exog) + re_df['random_effect'].values)
        else:
            self.pred_df['Predicted_Price'] = np.exp(self.mod.predict(fit_df))
        self.pred_df['Homicide_Rate'] = self.pred_df['Homicides'] / self.pred_df['Total_Pop'] * 100000
        self.pred_df = self.pred_df.loc[self.pred_df['Predicted_Price'].notna(),].sort_values(by=['Homicide_Rate','Predicted_Price']).reset_index(drop=True)
        return self.pred_df