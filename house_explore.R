library(dplyr)
buildings <- read.csv('Houses_Sold.csv')
buildings <- na.omit(buildings)
summary <- buildings %>% group_by(bed, bath) %>% summarise(count = n())
summary <- summary[summary$bath < summary$bed,]
max_bed <- min(summary[summary$count==1,]$bed)
print(paste('The maximum bedrooms we will alow in this analysis is', max_bed))

houses <- buildings[buildings$bed <= max_bed & buildings$bed > buildings$bath & buildings$house_size <= 5000 & buildings$price > 1000,]
apply(houses, 2,class)
houses[,c('price', 'bed', 'bath', 'acre_lot', 'zip_code', 'house_size')] <- apply(houses[,c('price', 'bed', 'bath', 'acre_lot', 'zip_code', 'house_size')], 2, as.numeric)
apply(houses, 2,class)
houses$price <- as.numeric(houses$price)
# prcomp(,center=TRUE, scale.=TRUE)
