library(dplyr)
buildings <- read.csv('Houses_Sold.csv')
buildings <- na.omit(buildings)
summary <- buildings %>% group_by(bed, bath) %>% summarise(count = n())
summary <- summary[summary$bath < summary$bed,]
max_bed <- min(summary[summary$count==1,]$bed)
print(paste('The maximum bedrooms we will alow in this analysis is', max_bed))

houses <- buildings[buildings$bed <= max_bed & buildings$bed > buildings$bath & buildings$house_size <= 5000 & buildings$price > 1000,]
sapply(houses,class)
X <- houses[,c('price', 'bed', 'bath', 'acre_lot', 'zip_code', 'house_size')]
pc_object <- prcomp(X,center=TRUE, scale.=TRUE)
summary(pc_object)
PCs <- as.data.frame(pc_object$x)

library(ggplot2)
scree_data <- data.frame(
  Component = 1:length(pc_object$sdev),
  Variance = pc_object$sdev^2 / sum(pc_object$sdev^2)
)
ggplot(scree_data, aes(x = Component, y = Variance))+
geom_bar(stat = "identity", fill = "steelblue")+
geom_line()+
geom_point()+
xlab("Principal Components")+
ylab("Proportion of Variance Explained")+
theme_bw()

ggplot()+
geom_point(aes(x=PCs$PC1, y = PCs$PC2))+
labs(x='Principal Component 1', y= 'Principal Component 2')+
theme_bw()+
theme(axis.text = element_text(size = 20),
axis.title = element_text(size = 25))

library(mgcv)
gam_mod <- gam(price ~ s(bed, k = 3, bs = "tp") + s(bath, k = 3, bs = "tp") + s(acre_lot, bs='tp')+s(house_size, bs='tp')+s(zip_code, bs='tp'), data=houses, method="REML", family = Gamma(link = "log"))

