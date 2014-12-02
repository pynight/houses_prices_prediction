from sklearn import metrics
from sklearn import preprocessing
from sklearn.cross_validation import train_test_split, cross_val_score, KFold
from sklearn import cross_validation
from numpy import array
from sklearn.metrics import confusion_matrix

from sklearn import linear_model
from sklearn.metrics import r2_score
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
#will include our points
points=[]

#will include our labels
labels=[]
   
def parseNone(data):
    if data == "None":
        data = '0'
    return data
        

#read the file
f=open('houses.txt')
header = 1

for line in f:
    if header:
        head = line.strip().split('\t')
        header =0
    else:
        toks = line.strip().split('\t')   # split the tokens      
        point=[float(parseNone(toks[3])),\
               float(parseNone(toks[4])),\
               float(parseNone(toks[5])),\
               float(parseNone(toks[28])),\
               float(parseNone(toks[27]))             
              ]
        #add the point to the points list
        points.append(point[:-1])
        
                
        
        #add the label (column) to the ;abels list 
        labels.append(point[-1])
f.close()

print points[1],labels[1]


X = array(points)
y = array(labels)

clf = KNeighborsRegressor(5)

'''
clf.fit(points,labels)
print "Print the coeffient of BayesianRidge regression:\n"
print clf.coef_
print '##################\n'

cv = KFold(X.shape[0], 5, shuffle=True, random_state=0)
print cross_validation.cross_val_score(clf, array(points), array(labels), cv=5)
print '##################\n'
print cross_validation.cross_val_score(clf, points, array(labels), cv = fold,scoring='r2')
'''
#%%
"""
SPLIT_PERC = 0.75
split_size = int(X.shape[0]*SPLIT_PERC)
X_train = X[:split_size]
X_test = X[split_size:]
y_train = y[:split_size]
y_test = y[split_size:]
"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

print metrics.mean_absolute_error(y_test, y_pred)


'''
print '##################\n'
print clf.coef_
'''
print '##################\n'
#print cross_validation.cross_val_score(clf, array(points), array(labels), cv=5)

#print '##################\n'
#print metrics.mean_absolute_error(y_test, y_pred)