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
import pickle
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
from sklearn.model_selection import KFold,ShuffleSplit
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV,GridSearchCV
from sklearn.svm import SVC
from hyperopt import hp,fmin,STATUS_OK,Trials,tpe
import xgboost
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

norm=StandardScaler().fit(new_df)
norm_X=norm.transform(new_df)

X_train,X_test,Y_train,Y_test=train_test_split(norm_X,y_os,test_size=0.2)

params = {
    "learning_rate": [0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
    "max_depth": [3, 4, 5, 6, 8, 10, 12, 15],
    "min_child_weight": [1, 3, 5, 7],
    "gamma": [0.0, 0.1, 0.2, 0.3, 0.4],
    "colsample_bytree": [0.3, 0.4, 0.5, 0.7]

}
#BOOSTING
XGBoost=xgboost.XGBClassifier(min_child_weight=1, max_depth=15, learning_rate=0.2, gamma=0.0, colsample_bytree=0.7)

#BAGGING
bagging=BaggingClassifier()
#randomsearch=RandomizedSearchCV(XGBoost,param_distributions=params,n_iter=5,scoring='roc_auc',n_jobs=-1,verbose=3)

#randomsearch.fit(X_train,Y_train)

#print(randomsearch.best_params_)

#results=cross_val_score(bagging,X_train,Y_train,cv=KFold(10))
#print(results)
#print(np.mean(results))

#STACKING

def Stacking(model,train,y,test,n_fold):
   folds=KFold(n_splits=n_fold,random_state=1,shuffle=True)
   test_pred=np.empty((test.shape[0],1),float)
   train_pred=np.empty((0,1),float)
   for train_indices,val_indices in folds.split(train,y.values):
      x_train,x_val=train.iloc[train_indices],train.iloc[val_indices]
      y_train,y_val=y.iloc[train_indices],y.iloc[val_indices]
      model.fit(X=x_train,y=y_train)
      train_pred=np.append(train_pred,model.predict(x_val))
      test_pred=np.append(test_pred,model.predict(test))

      return (test_pred.reshape(-1,1),train_pred)


model1=DecisionTreeClassifier()

test_pred1,train_pred1=Stacking(model=model1,train=X_train,y=Y_train,test=X_test,n_fold=10)

train_pred1=pd.DataFrame(train_pred1)
test_pred1=pd.DataFrame(test_pred1)




