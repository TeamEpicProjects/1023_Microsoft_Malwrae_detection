import json
import pandas as pd
import numpy as np
import missingno as msno
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report

df=pd.read_csv('Malware_Classification.csv')
del df['md5']
del df['Unnamed: 57']
new_df=df.drop('legitimate',axis=1)

new_df=new_df[~(new_df.Machine=='3ab1aa9785d0681434766bb0ffc4a13c')]
df=df[~(df.Machine=='3ab1aa9785d0681434766bb0ffc4a13c')]
new_df['MajorLinkerVersion'] = new_df['MajorLinkerVersion'].fillna(new_df.MajorLinkerVersion.mean())



def correlation(dataset,threshold):
    col_corr=set()
    corr_matrix=dataset.corr(method='spearman')
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if(abs(corr_matrix.iloc[i,j]>threshold)):
                col_name=corr_matrix.columns[i]
                col_corr.add(col_name)
    return col_corr

high_corr_features=correlation(new_df,0.7)



new_df=new_df.drop(high_corr_features,axis=1)

X=new_df.iloc[:,:-1]
Y=df.legitimate

from imblearn.over_sampling import RandomOverSampler
from collections import Counter

os=RandomOverSampler(0.8)
x_os,y_os=os.fit_resample(X,Y)

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2


#ordered_rank_feat=SelectKBest(score_func=chi2,k=36)
#ordered_features=ordered_rank_feat.fit(X,Y)


#dfscores=pd.DataFrame(ordered_features.scores_,columns=['Scores'])
#dfcolumns=pd.DataFrame(X.columns)

#feature_rank=pd.concat([dfcolumns,dfscores],axis=1)

#feature_rank.columns=['features','score']

new_df=x_os[['ImageBase','CheckSum','SizeOfStackCommit','SizeOfStackReserve','SizeOfUninitializedData',
          'LoadConfigurationSize','SizeOfInitializedData','SizeOfHeapReserve','LoaderFlags','ResourcesMeanSize']]


from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.model_selection import  train_test_split
from sklearn.metrics import classification_report,accuracy_score,confusion_matrix
from sklearn.ensemble import  RandomForestClassifier


norm=StandardScaler().fit(new_df)
norm_X=norm.transform(new_df)

X_train,X_test,Y_train,Y_test=train_test_split(norm_X,y_os,test_size=0.2,stratify=y_os)

from sklearn.linear_model import LogisticRegression

log_reg=LogisticRegression()
forest=RandomForestClassifier()

forest.fit(X_train,Y_train)
log_reg.fit(X_train,Y_train)

y_pred_forest=forest.predict(X_test)
y_pred_log=log_reg.predict(X_test)

print(classification_report(Y_test,y_pred_forest))
print(confusion_matrix(Y_test,y_pred_forest))

######################################################

with stratified datasplit and balanced dataset using logistic regression
           precision    recall  f1-score   support

           0       0.57      0.99      0.72     28170
           1       0.87      0.06      0.11     22536
 
[[27976   194]
 [21274  1262]]
######################################################
without stratified datasplit ,using logistic regression

                precision    recall  f1-score   support

           0       0.57      0.99      0.72     28143
           1       0.87      0.06      0.11     22563
 

[[27943   200]
 [21263  1300]]

#########################################################

but after applying random forest on unbalanced data
     precision    recall  f1-score   support

0       0.98      0.98      0.98     28272
1       0.96      0.97      0.97     14999

#confusion matrix
[[27735   537]
 [  479 14520]]
###########################################################

random forest on balanced dataset

precision    recall  f1-score   support

    0       0.99      0.98      0.98     28170
    1       0.97      0.99      0.98     22536

 [[27588   582]
 [  312 22224]]

###########################################################


