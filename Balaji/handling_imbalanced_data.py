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

new_df=df.drop("legitimate",axis=1)

Y=df.legitimate
#pearson correlation coeff
cor=new_df.corr()


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

#print((high_corr_features))

high_corr_pearson=['SectionMaxVirtualsize', 'SectionMaxRawsize', 'SizeOfStackCommit', 'MinorImageVersion', 'SectionsMinVirtualsize', 'SizeOfHeapCommit', 'ResourcesMinSize', 'SectionsMinEntropy', 'NumberOfRvaAndSizes', 'ResourcesMaxEntropy', 'ImportsNbDLL', 'ResourcesMaxSize', 'SizeOfHeapReserve']
high_corr_spearman=['SectionsMinRawsize', 'ResourcesMaxEntropy', 'SectionsMinEntropy', 'SectionsMeanVirtualsize', 'SectionMaxVirtualsize', 'SectionAlignment', 'SizeOfHeapCommit', 'ImportsNb', 'MajorSubsystemVersion', 'BaseOfData', 'SectionsMeanRawsize', 'SizeOfImage', 'SectionMaxRawsize', 'MinorSubsystemVersion', 'AddressOfEntryPoint', 'ExportNb', 'ResourcesMaxSize', 'ResourcesMinSize']


#dropped the high correlated values.
new_df=new_df.drop(high_corr_spearman,axis=1)

del new_df['Unnamed: 57']

def covariance(dataset,threshold):
    col_cov=set()
    cov_matrix=dataset.cov()
    for i in range(len(cov_matrix.columns)):
        for j in range(i):
            if(abs(cov_matrix.iloc[i,j]>threshold)):
                col_name=cov_matrix.columns[i]
                col_cov.add(col_name)
    return col_cov


high_cov_val=covariance(new_df,6.888356e+15)

new_df=new_df.drop(high_cov_val,axis=1)

#label_encoding

new_df.Machine=new_df.Machine.apply(lambda x:str(x))

new_df=new_df[~(new_df.Machine==512)&~(new_df.Machine=='450')&
              ~(new_df.Machine=='43620')&~(new_df.Machine=='452')&
              ~(new_df.Machine=='422')&~(new_df.Machine=='3ab1aa9785d0681434766bb0ffc4a13c')&
              ~(new_df.Machine=='512')]


#removing the values with low count from the column
new_df=new_df[(new_df.SizeOfOptionalHeader==224)|(new_df.SizeOfOptionalHeader==240)]




lbl_encode=LabelEncoder()



new_df['Machine_label_encode']=lbl_encode.fit_transform(new_df.Machine)

new_df['SizeOfOptionalHeader_label']=lbl_encode.fit_transform(new_df.SizeOfOptionalHeader)

#one_hot_encoding



del df['Unnamed: 57']

new_df['MajorLinkerVersion']=new_df['MajorLinkerVersion'].fillna(new_df.MajorLinkerVersion.mean())



counts = new_df.ID.value_counts(dropna=False)



new_df=new_df.drop('md5',axis=1)

new_df['legitimate']=Y
#t=TRIED TO PREDICT HOW THE IMBALANCED DATA AFFECTS THE ACCURACY OF THE MODEL
X=np.asarray(new_df.drop('legitimate',axis=1)).astype(np.int64)
Y=np.asarray(new_df.legitimate).astype(np.int64)

x_train,x_test,y_train,y_test=train_test_split(X,Y,train_size=0.7)

from sklearn.ensemble import RandomForestClassifier

random_forest=RandomForestClassifier()
random_forest.fit(x_train,y_train)

y_pred=random_forest.predict(x_test)
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test,y_pred))


##Under sampling
from collections import Counter
from imblearn.under_sampling import NearMiss
ns=NearMiss(0.8)
X_ns,Y_ns=ns.fit_resample(X,Y)

print(Counter(Y_ns))


#over sampling
from collections import Counter
from imblearn.over_sampling import RandomOverSampler

os=RandomOverSampler(0.8)
X_ns_1,Y_ns_new=os.fit_resample(X,Y)

print(Counter(Y_ns_new))



#SMOTETomek
from imblearn.combine import SMOTETomek

smt=SMOTETomek(0.8)
X_ns_smot,Y_ns_smot=ns.fit_resample(X,Y)

print(Counter(Y_ns_smot))


#ensemble techniques
from imblearn.ensemble import EasyEnsembleClassifier

ensemble=EasyEnsembleClassifier()


#handling imbalanced dataset with the help of ANN
import tensorflow
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from sklearn.metrics import roc_auc_score

#n_inputs=len(X.columns)

weights_assigned={0:1,1:2}

model=Sequential()
model.add(Dense(50,input_dim=35,activation='relu',kernel_initializer='he_uniform'))
model.add(Dense(1,activation='sigmoid'))

model.compile(loss='binary_crossentropy',optimizer='adam')
model.fit(x_train,y_train,class_weight=weights_assigned,epochs=10)

y_pred1=model.predict(x_test)

print(roc_auc_score(y_test,y_pred1))