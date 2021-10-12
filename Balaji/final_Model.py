import evalml
import pandas as pd
from sklearn.model_selection import train_test_split
from evalml.automl import AutoMLSearch
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
from xgboost import XGBClassifier
import pickle
'''

X_train,X_test,Y_train,Y_test=evalml.preprocessing.split_data(X,Y,problem_type='binary')
automl=AutoMLSearch(X_train=X_train,y_train=Y_train,problem_type='binary')
automl.search()


print(automl.describe_pipeline(automl.rankings.iloc[0]["id"]))'''


df=pd.read_csv('Malware_Classification.csv')

del df['md5']
del df['Unnamed: 57']

df=df[~(df.Machine=='3ab1aa9785d0681434766bb0ffc4a13c')]
df=df[~(df.Machine=='3ab1aa9785d0681434766bb0ffc4a13c')]
df['MajorLinkerVersion'] = df['MajorLinkerVersion'].fillna(df.MajorLinkerVersion.mean())



def correlation(dataset,threshold):
    col_corr=set()
    corr_matrix=dataset.corr(method='spearman')
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if(abs(corr_matrix.iloc[i,j]>threshold)):
                col_name=corr_matrix.columns[i]
                col_corr.add(col_name)
    return col_corr

high_corr_features=correlation(df,0.7)



new_df=df.drop(high_corr_features,axis=1)

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


norm=StandardScaler().fit(new_df)
norm_X=norm.transform(new_df)

X_train,X_test,Y_train,Y_test=train_test_split(norm_X,y_os,test_size=0.3)

XGBoost=XGBClassifier(min_child_weight=1, max_depth=6,n_estimators=100,n_jobs=-1,eval_metrics='logloss')

XGBoost.fit(X_train,Y_train)

Y_pred=XGBoost.predict(X_test)

print(classification_report(Y_test,Y_pred))
print(confusion_matrix(Y_test,Y_pred))
print(accuracy_score(Y_test,Y_pred))

with open('final_model_pickle','wb') as f:
    pickle.dump(XGBoost,f)

with open('final_model_pickle','rb') as f:
    xgb=pickle.load(f)











