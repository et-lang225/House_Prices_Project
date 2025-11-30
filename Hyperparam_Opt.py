import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
import xgboost as xgb
from hpsklearn import HyperoptEstimator, xgboost_regression
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from hyperopt.pyll.base import scope

class Hyper_Opt:
    def __init__(self, X, y):
        self.zip = X['zip_code']
        self.Xscaled = pd.concat([pd.DataFrame(StandardScaler().fit_transform(X.drop(columns=['zip_code'])), columns=X.drop(columns=['zip_code']).columns, index=X.index), X[['zip_code']]], axis=1)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.Xscaled, y, test_size=0.3, random_state=42)
        self.dtrain = xgb.DMatrix(self.X_train, label=self.y_train)
        self.dtest = xgb.DMatrix(self.X_test, label=self.y_test)
    
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
        print(f"\nOptimization finished. Best parameters found:\n{best_params}")
        print(f"Minimum RMSE: {trials.best_trial['result']['loss']:.4f}")
        {'Best Parameters': best_params, 'Min RMSE': trials.best_trial['result']['loss']}
    
    def Random_Forest_CV(self):
        # 
        param_grid = {
        # 'n_estimators': [25, 50, 100, 200, 400, 500, 600, 700],
        'max_depth': [30,40, 50],
        'min_samples_split': [2, 4, 6]
        }
        RF = RandomForestRegressor(n_estimators=400 , random_state=42, n_jobs=8, max_samples=0.05)
        RF_grid_search = RandomizedSearchCV(RF, param_distributions=param_grid, n_iter=8, scoring='neg_root_mean_squared_error', n_jobs=6, cv=3, verbose=2)
        RF_grid_search.fit(self.X_train, self.y_train)
        best_rf_model = RF_grid_search.best_estimator_
        return {'best': best_rf_model, 'model': RF_grid_search}