# House_Prices_Project
Class project for Computational Data Analysis

## Data Setup

Download required datasets:
1. Real estate: [Kaggle - USA Real Estate Dataset](https://www.kaggle.com/datasets/ahmedshahriarsakib/usa-real-estate-dataset)
2. Crime data: [FBI Data](https://www.icpsr.umich.edu/web/NACJD/studies/39062)
3. Agency data: [US Bureau of Justice](https://www.icpsr.umich.edu/web/ICPSR/studies/35158#)

Data files in `Data/` folder (ignored by git).


## Instructions
Download Data Directly into your Working Directory Using data_load.py:    
  from data_load import Data # importing the contents from the data_load.py    
  load = Data() # Assigining a variable to the Data class    
  load.HOMES_FOR_SALE() # Houses dataset from Kaggle    
  load.INCOME() # Income Data by zip code from IRS    
  load.HOMICIDES() # Homicides data by county from HHS    
  load.POPULATION() # Census data by zip code     
  load.ZIP_COUNTY() # df that relates zip code to county    

Clean data can be accssed through Final_Data_Output.py:    
  from Final_Data_Output import Final_Data as FD    
  FD = FD()    
  clean_df = FD.Merge_all()    
  clean_df.info()    

  clean_df = clean_df.dropna()     
  clean_df = sm.add_constant(clean_df)    
  clean_df.shape    
