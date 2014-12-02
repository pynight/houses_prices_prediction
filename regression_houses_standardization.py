from sklearn import metrics, preprocessing
from sklearn.cross_validation import train_test_split
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
import csv
import re
import matplotlib.pyplot as plt

# convert string back into numbers
def str2num(text):
    if re.search('[a-z/]+', text.lower()) and text != "None":  # if it is a string return itself
        return text    
    if text == "None":
        return None
    else:
        if '.' in text:
            return float(text)
        else:
            return int(text)

   
def remove_sparse(X, ratio):
    "if the ratio of missing values is bigger than 'ratio=0.5', discard that feature"
    dim_r, dim_c = X.shape
    none_matrix = np.matrix([[None]*dim_c]*dim_r)
    is_none = X == none_matrix
    missing = is_none.sum(axis=0)
    mask = missing < ratio*dim_r
    mask = np.array(mask)[-1].tolist()
    return  mask


def parse_X( X, header, ratio=0.5 ):
    
    # features that we will keep    
    keep = [0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1]
    
    mask = remove_sparse( X, ratio ) # features whose ratio of missing values is smaller than ratio=0.5
    
    parsed_mask = np.array(mask)*np.array(keep)*np.arange(X.shape[1])
    # features that are categorical
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0]
    #categorical = [ 'catego' in x.lower() for x in header[: -1]]
    #parsed_categorical =  parsed_mask*categorical
    
    parsed_mask = [x for x in parsed_mask if x>0]
    # [4, 5, 16, 17, 20, 23, 27, 29, 30, 32]
    
    parsed_X = X[ : , parsed_mask]    

    parsed_header = np.array(header)[parsed_mask]
    return parsed_header, parsed_X
    
############################################################
points=[] # features
labels=[] 

# read all the data for machine learning
with open('extractItems/houses.txt', 'rb') as f:
    reader = csv.reader(f, delimiter='\t')
    header = next(reader)
    for row in reader:
        row = [str2num(item) for item in row]
        points.append(row[:-1])
        labels.append(row[-1])

'''header of features
['Address(String)', 'Elevator(Numerical)', 'AddedToSite(Date)', 'AmenitiesCommunity(Numerical)', 
'Appliances(Numerical)', 'Beds(Numerical)', 'BedsOnMain(Numerical)', 'BedsOnUpper(Numerical)', 
'Baths(Numerical)', 'Basement(Numerical)', 'Brokeredby(String)', 'Builder(String)', 
'StoriesNum(Numerical)', 'CondoCoop(String)', 'CondoCoopFee(Numerical)', 'Garage(Numerical)',
'ElectCooling(Categorical)', 'CentralAC(Categorical)', 'ParkingInPrice(Categorical)', 'HOAFee(Numerical)', 
'HouseSize(Numerical)', 'Lastrefreshed(Numerical)', 'ListingAgent(String)', 'LotSize(Numerical)', 
'MLSID(Categorical)', 'PoolSpa(Categorical)', 'PostalCode(Categorical)', 'PriceSqFt(Numerical)', 
'PropertyStatus(Categorical)', 'PropertyType(Categorical)', 'Status(Categorical)', 'Style(String)', 
'YearBuilt(Numerical)',]'''

X = np.matrix(points)
y = np.array(labels)

# remove sparse features
parsed_header, parsed_X = parse_X( X, header, ratio=0.5 )

categorical = [ 'catego' in x.lower() for x in parsed_header]
categorical_pos = [i for i in range(len(categorical)) if categorical[i] is True]

# convert python None into numpy.nan
parsed_X = np.matrix(parsed_X, dtype=float)

# complete missing values
imp = preprocessing.Imputer(missing_values = 'NaN', strategy = 'median', axis = 0) # 'mean', 'median', and 'most_frequent'
imp.fit(parsed_X)
parsed_X = imp.transform(parsed_X)

# encode categorical features
encoder = preprocessing.OneHotEncoder(categorical_features = categorical_pos)
encoder.fit(parsed_X)
transformed_X=encoder.transform(parsed_X).toarray()

# Standardization of features
scaler = preprocessing.StandardScaler().fit(transformed_X)
standardized_X = scaler.transform(transformed_X)

###########################################################3
# K-NN regression
KNN = KNeighborsRegressor(5)

legend = ['transformed_X', 'standardized_X']
absoulte_error = dict.fromkeys(legend)


data = [transformed_X, standardized_X]

for i in range(len(data)):

    X_train, X_test, y_train, y_test = train_test_split(data[i], y, test_size=0.25, random_state=15)
    
    KNN.fit(X_train, y_train)
    
    y_pred = KNN.predict(X_test)
    
    absoulte_error[legend[i]] = metrics.mean_absolute_error(y_test, y_pred)

##################################################
# bar plot of absoulte error vs. standardization
x_pos = np.arange(len(data)+1)
y_data = absoulte_error.values()
y_data.append(y.mean())
fig, ax = plt.subplots()
rects = ax.bar(x_pos, y_data, yerr= [0, 0, y.std()], color= 'r', align='center', alpha=0.2)
ax.set_xticks(x_pos)
ax.set_xticklabels(legend+['mean'])
ax.set_ylabel('absoulte error')
ax.set_title('Error vs. Standardization')

def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height), ha='center', va='bottom')
                
autolabel(rects)
plt.show()

#########################################################################
# plot y, it demonstrates that the houses are listed by ascended prices.
fig, ax2 = plt.subplots()
ax2.plot(y, 'ro')
# however, that the prices are random after train_test_split
ax2.plot(np.concatenate([y_train,y_test]), 'g*')
plt.show()