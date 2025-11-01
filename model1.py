import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

class DataPipeline:
    def __init__(self, data_path='HousingData/realtor-data.zip.csv.zip'):
        self.data_path = data_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.stats = None
        
    def load_data(self, use_sample=False):
        self.df = pd.read_csv(self.data_path, compression='zip')
        print("Data Shape:", self.df.shape)
        print("Column Names:", list(self.df.columns))
        print("\nData Types\n:", self.df.dtypes)
        print("\nFirst few rows:")
        display(self.df.head())
        if use_sample:
            self.df = self.df.sample(5000)
            print("\nSample df Shape:", self.df.shape)
        return self.df
    
    def prepare_data(self, target='price'):
        df = self.df.dropna()
        X = df.drop(columns=target).copy()
        y = df[target].copy()
        numerical_cols = X.select_dtypes(include='number').columns.to_list()
        categorical_cols = X.select_dtypes(exclude='number').columns.to_list()
        # Scale numerical
        if numerical_cols:
            scaler = StandardScaler()
            X[numerical_cols] = scaler.fit_transform(X[numerical_cols])
        # OHE categorical
        if categorical_cols:
            X = pd.get_dummies(X, columns=categorical_cols)
        return X, y
    
    def split_data(self, X, y, split=0.8, random_state=1):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, train_size=split, random_state=random_state)
        print("Split Training:", split)
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def save_data(self):
        self.X_train.to_csv("processed_data_X_train.csv", index=False)
        self.X_test.to_csv("processed_data_X_test.csv", index=False)
        self.y_train.to_csv("processed_data_y_train.csv", index=False, header=['price'])
        self.y_test.to_csv("processed_data_y_test.csv", index=False, header=['price'])
        print("Processed data saved")
        
    def log_stats(self):
        self.stats = pd.DataFrame({
            'metric': ['original_rows', 'original_cols', 'train_size', 'test_size', 
                       'num_features', 'target_mean', 'target_std'],
            'value': [self.df.shape[0], self.df.shape[1], len(self.X_train), len(self.X_test), 
                      self.X_train.shape[1], self.y_train.mean(), self.y_train.std()]})
        display(self.stats)
        return self.stats
    
    def fit_model(self, model_type='gradient_boost'):
        if model_type == 'random_forest':
            model = RandomForestRegressor().fit(self.X_train, self.y_train)
        elif model_type == 'gradient_boost':
            model = GradientBoostingRegressor().fit(self.X_train, self.y_train)
        else:
            model = LinearRegression().fit(self.X_train, self.y_train)
            
        y_pred = model.predict(self.X_test)
        mse = mean_squared_error(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)
        r2 = r2_score(self.y_test, y_pred)
        print("MSE:", mse, "\nMAE:", mae)
        print("R2:", r2)
        return y_pred
    
    def run_pipeline(self, use_sample=False, model_type='random_forest', save_output=False):
        self.load_data(use_sample=use_sample)
        X, y = self.prepare_data()
        self.split_data(X, y)
        self.log_stats()
        if save_output:
            self.save_data()
        
        predictions = self.fit_model(model_type=model_type)
        return self.stats, self.X_train, self.X_test, self.y_train, self.y_test


if __name__ == "__main__":
    pipeline = DataPipeline()
    stats, X_train, X_test, y_train, y_test = pipeline.run_pipeline(use_sample=True,  model_type='random_forest', save_output=False)
    
    