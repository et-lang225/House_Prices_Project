import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import root_mean_squared_error
import statsmodels.api as sm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
import xgboost as xgb
from hpsklearn import HyperoptEstimator, xgboost_regression
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from hyperopt.pyll.base import scope

class Testing_Models:
    def __init__(self, X, y):
        self.X_train_1 = X.groupby('zip_code').sample(n=1, random_state=42)
        leftover = X.drop(self.X_train_1.index)
        self.X_train_2, self.X_test = train_test_split(leftover, test_size=0.3, random_state=42)
        self.X_train = pd.concat([self.X_train_1, self.X_train_2], axis=0)
        self.scale_fit = StandardScaler().fit(self.X_train.drop(columns=['zip_code']))
        num_cols = self.X_train.drop(columns=['zip_code']).columns
        X_train_scaled = pd.DataFrame(self.scale_fit.transform(self.X_train[num_cols]), index=self.X_train.index, columns=num_cols)
        self.X_train = pd.concat([X_train_scaled, self.X_train[['zip_code']]], axis=1)
        X_test_scaled = pd.DataFrame(self.scale_fit.transform(self.X_test[num_cols]), index=self.X_test.index, columns=num_cols)
        self.X_test = pd.concat([X_test_scaled, self.X_test[['zip_code']]], axis=1)
        self.y_train = y.loc[self.X_train.index,]
        self.y_test = y.loc[self.X_test.index,]
        self.dtrain = xgb.DMatrix(self.X_train, label=self.y_train)
        self.dtest = xgb.DMatrix(self.X_test, label=self.y_test)
        
    def GLMM(self):
        X_train_fe = sm.add_constant(self.X_train.drop(columns=['zip_code']))
        exog_re = np.ones((len(X_train_fe),1))
        groups = self.X_train['zip_code'].astype(str)
        mod = sm.MixedLM(self.y_train, X_train_fe, groups=groups, exog_re=exog_re)
        result = mod.fit()
        re = pd.DataFrame.from_dict(result.random_effects, orient='index').reset_index()
        re.columns = ['zip_code', 'random_effect']
        re['zip_code'] = re['zip_code'].astype(float)
        re_df = self.X_test[['zip_code']].merge(re, on='zip_code', how='left')
        exog = self.X_test.drop(columns=['zip_code'])
        exog = sm.add_constant(exog)
        y_pred_mixed = result.predict(exog=exog) + re_df['random_effect'].values
        R_squared = 1 - np.sum((self.y_test - y_pred_mixed) ** 2) / np.sum((self.y_test - np.mean(self.y_test)) ** 2)
        rmse = root_mean_squared_error(self.y_test, y_pred_mixed)
        return {'error': rmse, 'variance_explained': R_squared, 'y_pred': np.exp(y_pred_mixed), 'model': result, 'scale_fit': self.scale_fit, 'data': self.X_train}
    
    def XGBoost(self, gamma, learning_rate, colsample_bytree, subsample, max_depth, min_child_weight):
        parms = {
            'objective': 'reg:squarederror',
            'gamma': gamma,
            'learning_rate': learning_rate,
            'colsample_bytree': colsample_bytree,
            'subsample': subsample,
            'max_depth': max_depth,
            'min_child_weight': min_child_weight,
            'tree_method': 'hist'
        }
        xgb_mod = xgb.train(
            params = parms,
            dtrain = self.dtrain,
            num_boost_round=1000
        )
        y_pred = xgb_mod.predict(self.dtest)
        rmse = root_mean_squared_error(self.y_test, y_pred)
        R_squared = 1 - np.sum((self.y_test - y_pred) ** 2) / np.sum((self.y_test - np.mean(self.y_test)) ** 2)
        return {'error': rmse, 'variance_explained': R_squared, 'y_pred': np.exp(y_pred), 'model': xgb_mod, 'scale_fit': self.scale_fit}
    
    def Random_Forest(self, max_depth, min_samples_split):
        RF = RandomForestRegressor(n_estimators=400 , max_depth=max_depth, min_samples_split=min_samples_split, random_state=42, n_jobs=8, max_samples=0.05)
        RF.fit(self.X_train, self.y_train)
        y_pred = RF.predict(self.X_test)
        rmse = root_mean_squared_error(self.y_test, y_pred)
        R_squared = 1 - np.sum((self.y_test - y_pred) ** 2) / np.sum((self.y_test - np.mean(self.y_test)) ** 2)
        return {'error': rmse, 'variance_explained': R_squared, 'y_pred': np.exp(y_pred), 'model': RF, 'scale_fit': self.scale_fit}        