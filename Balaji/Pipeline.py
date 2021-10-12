import json
import pandas as pd
import numpy as np
import missingno as msno
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn.compose import make_column_transformer
from sklearn.impute import SimpleImputer

df=pd.read_csv('Malware_Classification.csv')
del df['md5']
del df['Unnamed: 57']
df=df[~(df.Machine=='3ab1aa9785d0681434766bb0ffc4a13c')]
df['MajorLinkerVersion'] = df['MajorLinkerVersion'].fillna(df.MajorLinkerVersion.mean())


X=df.drop('legitimate',axis=1)
Y=df.legitimate


X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.3)



pipeline_lr=Pipeline([
                     ('pca1',PCA(n_components=2)),
                      ('scalar1',StandardScaler()),
                     ('lr_classifier',LogisticRegression())])

pipeline_dt=Pipeline([
                      ('pca2',PCA(n_components=2)),
                      ('scalar2',StandardScaler()),

                     ('dt_classifier',DecisionTreeClassifier())])

pipeline_rf=Pipeline([('pca3',PCA(n_components=2)),
                      ('scalar3',StandardScaler()),
                     ('rf_classifier',RandomForestClassifier())])


pipelines=[pipeline_lr,pipeline_dt,pipeline_rf]

best_accuracy=0.0
best_classifier=0
best_pipeline=""

pipe_dict={0:"Logistic Regression",1:"Decison tree",2:"Random Forest"}

for pipe in pipelines:
    pipe.fit(X_train,Y_train)


for i,model in enumerate(pipelines):
    print(pipe_dict[i],model.score(X_test,Y_test))


