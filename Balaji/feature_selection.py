import json
import pandas as pd
import numpy as np
import missingno as msno
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2


df=pd.read_csv('Malware_Classification.csv')
del df['md5']
del df['Unnamed: 57']
df=df[~(df.Machine=='3ab1aa9785d0681434766bb0ffc4a13c')]

df['MajorLinkerVersion'] = df['MajorLinkerVersion'].fillna(df.MajorLinkerVersion.mean())

X=(df.iloc[:,:-1])
Y=(df.legitimate)


#select Kbest features
ordered_rank_feat=SelectKBest(score_func=chi2,k=55)
ordered_features=ordered_rank_feat.fit(X,Y)

dfscores=pd.DataFrame(ordered_features.scores_,columns=['Scores'])
dfcolumns=pd.DataFrame(X.columns)

feature_rank=pd.concat([dfcolumns,dfscores],axis=1)

feature_rank.columns=['features','score']
print(feature_rank.nlargest(10,'score'))

##feature importance
from sklearn.ensemble import ExtraTreesClassifier
import matplotlib.pyplot as plt

model=ExtraTreesClassifier()
#model.fit(X,Y)

ranked_features=pd.Series(model.feature_importances_,index=X.columns)
ranked_features.nlargest(10).plot(kind='barh')
#

#forward and backward feature selection
new_df=df[['ImageBase','CheckSum','SizeOfStackCommit','SizeOfStackReserve','SizeOfUninitializedData',
          'LoadConfigurationSize','SizeOfInitializedData','ResourcesMaxSize','SizeOfHeapReserve','LoaderFlags','legitimate']]

x=(new_df.iloc[:,:-1])
y=(new_df.legitimate)


from mlxtend.feature_selection import SequentialFeatureSelector as sfs
from sklearn.linear_model import LogisticRegression

log_reg=LogisticRegression()
sfs1=sfs(log_reg,k_features=4,forward=False,verbose=2,scoring='neg_mean_squared_error')

sfs1=sfs1.fit(x,y)

feat_names=list(sfs1.k_feature_names_)

print(feat_names)


#boruta feature selection

from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier

forest=RandomForestClassifier(n_jobs=-1,class_weight='balanced',max_depth=5)

feat_sel=BorutaPy(forest,n_estimators='auto',verbose=2,random_state=1)

feat_sel.fit(x,y)

print(feat_sel.support_)

#recursive feature elimination with cross-validation

from sklearn.feature_selection import RFECV
from sklearn.model_selection import StratifiedKFold


rfecv=RFECV(estimator=log_reg,step=1,cv=StratifiedKFold(55),scoring='accuracy')
rfecv=rfecv.fit(x,y)

print(X.columns[rfecv.support_])

#PCA(PRINCIPLE COMPONENT ANALYSIS)

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix

#standard scalar is used to convert all the data to standard normal distrubution
scaler=StandardScaler()
scaler.fit(new_df)

scaled_data=scaler.transform(new_df)

pca=PCA(n_components=2)
pca.fit(scaled_data)

x_pca=pca.transform(scaled_data)

plt.figure(figsize=(8,6))
plt.scatter(x_pca[:,0],x_pca[:,1],c=df['legitimate'])
plt.xlabel("first principle component")
plt.ylabel("secong principle component")

x_train,x_test,y_train,y_test=train_test_split(x_pca,df.legitimate,train_size=0.7)

log_reg.fit(x_train,y_train)
y_pred=log_reg.predict(x_test)

print(confusion_matrix(y_test,y_pred))
print(accuracy_score(y_test,y_pred))