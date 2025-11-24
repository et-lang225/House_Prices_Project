# House_Prices_Project
Class project for Computational Data Analysis

## Data Setup

Download required datasets:
1. Real estate: [Kaggle - USA Real Estate Dataset](https://www.kaggle.com/datasets/ahmedshahriarsakib/usa-real-estate-dataset)
2. Population data: [Census Dataset](https://data.census.gov/table/ACSDP5Y2023.DP05?t=Populations+and+People&g=010XX00US$8600000&y=2023)
3. Homicide data: [HHS Data](https://healthdata.gov/CDC/Mapping-Injury-Overdose-and-Violence-County/5k3d-tfmx/about_data)
4. Income data: [IRS Dataset](https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-2022-zip-code-data-soi)

Data files in `Data/` folder (ignored by git).


## Instructions
If Full_Model.ipynb is run through every cell then price predictions will be made with user preferences from a generalized linear mixed model. However, the first cell has to be run the first time (as it downloads the data). The data download code is commented out right now so be sure to uncomment and run before running the rest of the code for the first time.     

The resulting dataframe is sorted by homicides and predicted price (lowest to highest).    

Once Full_Model.ipynb is completed and all cells have been executed properly, there should be a zip_scores.js file generated and Map.html should be operable. The Map.html should only require a double-click to operate.
