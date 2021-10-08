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


norm=StandardScaler().fit(new_df)
norm_X=norm.transform(new_df)

X_train,X_test,Y_train,Y_test=train_test_split(norm_X,y_os,test_size=0.2)




log_reg=LogisticRegression()
SVM=SVC()


#k-fold validation approach
#KFold=KFold(10)
#results=cross_val_score(log_reg,x_os,y_os,cv=KFold)
#print(np.mean(results))

#Randomizedcvsearch
n_estimators=[int(x) for x in np.linspace(start=200,stop=2000,num=10)]
max_features=['auto','sqrt','log2']
max_depth=[int(x) for x in np.linspace(10,1000,10)]
min_samples_split=[1,3,4,5,7,9]
min_samples_leaf=[1,2,4,6,8]


random_grid={'n_estimators':n_estimators,
             'max_features':max_features,
             'max_depth':max_depth,
             'min_samples_split':min_samples_split,
             'min_samples_leaf':min_samples_leaf,
             'criterion':['entropy','gini']}

#gridsearchcv
grid={
    'criterion':['entropy'],
     'max_depth':[340],
    'max_features':['log2'],
    'min_samples_leaf':[1,3,5],
    'min_samples_split':[0,3,4,5],
    'n_estimators':[1000,2000,3000,4000,5000]}

#bayesion optimization
space = {'criterion': hp.choice('criterion', ['entropy', 'gini']),
        'max_depth': hp.quniform('max_depth', 10, 1200, 10),
        'max_features': hp.choice('max_features', ['auto', 'sqrt','log2', None]),
        'min_samples_leaf': hp.uniform('min_samples_leaf', 0, 0.5),
        'min_samples_split' : hp.uniform ('min_samples_split', 0, 1),
        'n_estimators' : hp.choice('n_estimators', [10, 50, 300, 750, 1200,1300,1500])
    }


def objective(space):
    model = RandomForestClassifier(criterion=space['criterion'], max_depth=space['max_depth'],
                                   max_features=space['max_features'],
                                   min_samples_leaf=space['min_samples_leaf'],
                                   min_samples_split=space['min_samples_split'],
                                   n_estimators=space['n_estimators'],
                                   )

    accuracy = cross_val_score(model, X_train, Y_train, cv=KFold(5)).mean()


    return {'loss': -accuracy, 'status': STATUS_OK}

trials = Trials()
#best = fmin(fn= objective,space= space,algo= tpe.suggest,max_evals = 5,trials= trials)


#{'criterion': 1, 'max_depth': 490.0, 'max_features': 1, 'min_samples_leaf': 0.2310387401540508, 'min_samples_split': 0.07110067389732533, 'n_estimators': 1}


forest=RandomForestClassifier(criterion='gini', max_depth=490, max_features='sqrt', min_samples_leaf=0.2310387401540508, min_samples_split=0.07110067389732533, n_estimators=1)
#rfRandomcv=RandomizedSearchCV(estimator=forest,param_distributions=random_grid,n_iter=1000,cv=KFold(1000),random_state=100,
#                              verbose=2,n_jobs=-1)

#Gridsearch=GridSearchCV(estimator=forest,param_grid=grid,cv=KFold(1000),n_jobs=-1,verbose=2)
#Gridsearch.fit(X_train,Y_train)

#print(Gridsearch.best_estimator_)

#criterion=entropy, max_depth=340, max_features=log2, min_samples_leaf=1, min_samples_split=1, n_estimators=1000; total time=   1.5s

#Svclass=SVC(kernel='linear')

#Svclass.fit(X_train,Y_train)
#repeated random test-train split

forest.fit(X_train,Y_train)
#log_reg.fit(X_train,Y_train)
#SVM.fit(X_train,Y_train)

y_pred_forest=forest.predict(X_test)
#y_pred_log=log_reg.predict(X_test)
#y_pred_SVM=Svclass.predict(X_test)

print(classification_report(Y_test,y_pred_forest))
print(confusion_matrix(Y_test,y_pred_forest))

#with open('model_pickle','wb') as f:
#    pickle.dump(f)


#with open('model_pickle','rb') as f:
    #model=pickle.load(f)


#pred=model.predict(X_test)

#print(classification_report(Y_test,pred))


