import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
from hpsklearn import HyperoptEstimator, xgboost_regression
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from hyperopt.pyll.base import scope

class Testing_Models:
    def __init__(self, X, y):
        self.zip = X['zip_code']
        self.Xscaled = pd.concat([pd.DataFrame(StandardScaler().fit_transform(X.drop(columns=['zip_code'])), columns=X.drop(columns=['zip_code']).columns, index=X.index), X[['zip_code']]], axis=1)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.Xscaled, y, test_size=0.3, random_state=42)
        self.dtrain = xgb.DMatrix(self.X_train, label=self.y_train)
        self.dtest = xgb.DMatrix(self.X_test, label=self.y_test)
        
    def GLMM_CV(self):
        X_train_fe = sm.add_constant(self.X_train.drop(columns=['zip_code']))
        exog_re = np.ones((len(X_train_fe),1))
        groups = self.X_train['zip_code'].astype(str)
        mod = sm.MixedLM(self.y_train, X_train_fe, groups=groups, exog_re=exog_re)
        result = mod.fit()
        re = pd.DataFrame.from_dict(result.random_effects, orient='index').reset_index()
        re.columns = ['zip_code', 'random_effect']
        re_df = self.X_test[['zip_code']].merge(re, on='zip_code', how='left')
        exog = self.X_test.drop(columns=['zip_code'])
        y_pred_mixed = result.predict(exog=exog)+ re_df['random_effect'].values
        R_squared = 1 - np.sum((self.y_test - y_pred_mixed) ** 2) / np.sum((self.y_test - np.mean(self.y_test)) ** 2)
        return print(f'Proportion of Variance Explained: {R_squared:.4f}')
    
    def XGBoost_CV(self):
        space = {
            'objective': 'reg:squarederror',
            'gamma': hp.uniform('gamma', 0, 1.0),
            'learning_rate': hp.loguniform('learning_rate', np.log(0.03), np.log(0.3)),
            'colsample_bytree': hp.uniform('colsample_bytree', 0.5, 1.0),
            'subsample': hp.uniform('subsample', 0.5, 1.0),
            'max_depth': scope.int(hp.quniform('max_depth', 3, 10, 1)),
            'min_child_weight': scope.int(hp.quniform('min_child_weight', 1, 5, 1)),
            'tree_method': 'hist'
        }
        def objective(params):
            params['max_depth'] = int(params['max_depth'])
            params['min_child_weight'] = int(params['min_child_weight'])
            cv_results = xgb.cv(
                params,
                self.dtrain,
                num_boost_round=1000,
                metrics = 'rmse',
                nfold=3,
                early_stopping_rounds=20,
                seed=42,
                verbose_eval=False
            )
            best_loss = cv_results['test-rmse-mean'].min()
            return {'loss': best_loss, 'status': STATUS_OK}
        
        trials = Trials()
        best_params = fmin(
            fn=objective,
            space=space,
            algo=tpe.suggest,
            max_evals=50,
            trials=trials
        )
        # This function should take about an hour
        # Michael this will get faster if you have a fast GPU, I will have to adjust the code though to use that GPU
        print(f"\nOptimization finished. Best parameters found:\n{best_params}")
        print(f"Minimum RMSE: {trials.best_trial['result']['loss']:.4f}")