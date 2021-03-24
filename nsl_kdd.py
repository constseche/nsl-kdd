import numpy as np
import pandas as pd
from sklearn import cluster
from sklearn.preprocessing import LabelEncoder,OneHotEncoder, StandardScaler, MaxAbsScaler, MinMaxScaler
from sklearn.metrics import silhouette_score, confusion_matrix, homogeneity_completeness_v_measure, silhouette_samples
from sklearn import metrics, mixture
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import matplotlib.cm as cm
    
    
# =============================================================================
# kmeans result/evaluation
# fit in train set and predict for test set
# count how many 'attack' and 'normal' are includes in each labels_ from kmeans
# for example: 
# kmean predicted label 0 contains:  attack    6060
#                                    normal    9580
# kmean predicted label 1 contains:  attack    6773
#                                    normal    131
# So,  normal results in label 0 are greater that the attack, so we assume that 
# label 0 is the "normal" label of y_test set
# and the attack results in label 1 are much greater that the normal so we assume that 
# label 1 is the "attack" label of y_test
# Then we measure: accuracy = how many correct predictions/all_prediction(shape[0])
# =============================================================================  
    

def results(X_test, y_test, clf = None):
    if clf is None:
        clf = cluster.KMeans(n_clusters=4,init='random').fit(X_test)
        
    preds = clf.predict(X_test)
    ans = pd.DataFrame({'label':y_test.values, 'kmean':preds})
    print(preds)
    print( "y_test:   ", y_test)
        
    ans = ans.groupby(['kmean', 'label']).size()
    print(ans)

    correct = sum([anom if anom > norm else norm for anom, norm in zip(ans[::2],ans[1::2])])
    
    print(correct)
    print(sum(ans))
    print("Total accuracy: {0:.1%}".format(correct/sum(ans)))
    
    y_test = y_test.tolist()
    
    for x in range(len(y_test)): 
        if (y_test[x] == "attack"):
            y_test[x] = 1
        else: 
            y_test[x] = 0
            


    print(homogeneity_completeness_v_measure(y_test, preds))
    print("ac ", metrics.accuracy_score(y_test, preds))
    print(confusion_matrix(y_test, preds))
    
    return clf

# =============================================================================
# silhouette average score for max_clusters different values of number pf clusters
# =============================================================================     
def num_clusters(X, max_clusters):
    s = np.zeros(max_clusters+1)
    s[0] = 0;
    s[1] = 0;
    
    for k in range(2,max_clusters+1):
        kmeans = cluster.KMeans(init = 'k-means++', n_clusters = k)
        kmeans.fit_predict(X)
        s[k] = silhouette_score(X,kmeans.labels_,metric = 'euclidean')
    
    plt.plot(range(2,len(s)),s[2:])
    
    plt.xlabel('Number of clusters')
    plt.ylabel('Average Silhouette Score')
    plt.show()


# =============================================================================
# Mean Silhouette Coefficient for all samples
# silhouette average score for 2 number of clusters using kmeans alg
# =============================================================================    
def sil(X):
    clf = cluster.KMeans(n_clusters = 2, init='random')
    clf.fit_predict(X)
    
    print(silhouette_score(X,clf.labels_))
    

def silhouette_analysis(X, y, range_n_clusters):
    for n_clusters in range_n_clusters:
   
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)

        ax1.set_xlim([-0.1, 1])
        ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

        clusterer = cluster.KMeans(init = 'k-means++', n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(X)

        silhouette_avg = silhouette_score(X, cluster_labels)
        print("For n_clusters =", n_clusters,
              "The average silhouette_score is :", silhouette_avg)

        sample_silhouette_values =silhouette_samples(X, cluster_labels)
    
        y_lower = 10
        for i in range(n_clusters):
            ith_cluster_silhouette_values = \
                sample_silhouette_values[cluster_labels == i]
    
            ith_cluster_silhouette_values.sort()
    
            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i
    
            color = cm.nipy_spectral(float(i) / n_clusters)
            ax1.fill_betweenx(np.arange(y_lower, y_upper),
                              0, ith_cluster_silhouette_values,
                              facecolor=color, edgecolor=color, alpha=0.7)
    

            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
            y_lower = y_upper + 10
    
        ax1.set_title("The silhouette plot for the various clusters.")
        ax1.set_xlabel("The silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

    plt.show()

# =============================================================================
#                        PREPROCESSING
# =============================================================================     

# Load the dataset, train and test set
X_train = pd.read_csv('NSL-KDDTrain.csv')
X_test = pd.read_csv('NSL-KDDTest.csv')

# target: labels of test dataset
y_test = X_test['target']
X_test = X_test.drop(columns = ['target'])

print(X_test.shape)
print(X_train.shape)


# =============================================================================
#                       Handle Categorical columns
# Handling categorical-nominal data(colums = 'protocol_type', 'service', 'flag')
# 1) just dropping them.
# 2) LabelEncoder + OneHotEncoder
# =============================================================================    


categorical_columns=['protocol_type', 'service', 'flag']

# drop the colums that contains non-numeric data
#X_train = X_train.select_dtypes(include = [np.number])
#X_test = X_test.select_dtypes(include = [np.number])

# OR 

# train_data = X_train.drop(columns = categorical_columns)
# test_data = X_test.drop(columns = categorical_columns)

# print(train_data.shape)
# print(test_data.shape)


# =============================================================================
#                       Train set
# =============================================================================    
#
# 'protocol_type' has 3 categories
# 'service' has 70 categories
# 'flag' has 11 categories
# + 84 columns after labelencoding and onehotencoding

# columns 'protocol_type', 'service', 'flag' of X_train
categorical_values = X_train[categorical_columns]


# for col in X_train.columns:
#     if X_train[col].dtypes == 'object' :
#         unique_cat = len(X_train[col].unique())
#         print("'{col_name}' has {unique_cat}".format(col_name = col, unique_cat = unique_cat))

# a = X_train['service'].value_counts().sort_values(ascending=False)
# print(a)

# ------------protocol column-----------
# find unique values of 'protocol' column/feature and sort them 
# create unique_protocol_str
# it contains "protocol_+{nameof each category}" values and represent the new created columns
# --------------------------------------
# 
protocol_un = sorted(X_train.protocol_type.unique())
string1 = 'protocol'
unique_protocol_str = [string1 + x for x in protocol_un]


# ----------------service---------------
# service_+{nameof each category}
unique_service_train=sorted(X_train.service.unique())
string2 = 'service_'
unique_service2_train=[string2 + x for x in unique_service_train]


# -----------------flag-----------------
# flag_+{nameof each category}
unique_flag=sorted(X_train.flag.unique())
string3 = 'flag_'
unique_flag2=[string3 + x for x in unique_flag]


# merge these new lists which will be the new columns (dummmy columns)
dumcols = unique_protocol_str + unique_service2_train + unique_flag2

# Label Encoder
# before OneHotEncoder, the data should be label encoded before one hot encoded.
df_categorical_values_enc = categorical_values.apply(LabelEncoder().fit_transform)

# One Hot Encoder
enc = OneHotEncoder(categories = 'auto')
df_categorical_values_encenc = enc.fit_transform(df_categorical_values_enc)
df_cat_data = pd.DataFrame(df_categorical_values_encenc.toarray(),columns = dumcols)


# =============================================================================
#                        test set
# ============================================================================= 
# Feature 'protocol_type' has 3 categories
# Feature 'service' has 64 categories
# Feature 'flag' has 11 categories
# the same procedure as train test


# # count how many discrete nomial values
# for col_name in X_test.columns:
#     if X_test[col_name].dtypes == 'object' :
#         unique_cat_test = len(X_test[col_name].unique())
#         print("Feature '{col_name}' has {unique_cat} categories".format(col_name = col_name, unique_cat = unique_cat_test))

cat = X_test['service'].value_counts().sort_values(ascending = False)
print(cat)

# protocol column
unique_protocol_test = sorted(X_test.protocol_type.unique())
string1 = 'Protocol_type_'
unique_protocol2_test = [string1 + x for x in unique_protocol_test]


# service column
unique_service_test = sorted(X_test.service.unique())
string2 = 'service_'
unique_service2_test = [string2 + x for x in unique_service_test]


# flag column
unique_flag_test = sorted(X_test.flag.unique())
string3 = 'flag_'
unique_flag2_test=[string3 + x for x in unique_flag_test]



# Merge new columns created from protocol, service and flag columns
dumcols_test=unique_protocol2_test + unique_service2_test + unique_flag2_test


categorical_columns=['protocol_type', 'service', 'flag']
categorical_values_test = X_test[categorical_columns]

# Label Encoder
# before OneHotEncoder, the data should be label encoded before one hot encoded.
df_categorical_values_enc_test = categorical_values_test.apply(LabelEncoder().fit_transform)

# One Hot Encoder
enc = OneHotEncoder(categories='auto')
df_categorical_values_encenc_test = enc.fit_transform(df_categorical_values_enc_test)
df_cat_data_test = pd.DataFrame(df_categorical_values_encenc_test.toarray(),columns = dumcols_test)

# =============================================================================
#              Differences categories between train and test set
# [service_urh_i', 'service_aol', 'service_http_2784', 'service_http_8001', 'service_red_i', 'service_harvest']
# ============================================================================= 


train_service = X_train['service'].tolist()
test_service = X_test['service'].tolist()

difference = list(set(train_service) - set(test_service))

string = 'service_'
difference = [string + x for x in difference]

print("differences of service categories between test and train set:", difference)

for col in difference:
    df_cat_data_test[col] = 0


# =============================================================================
#               Final train and test sets
# drop 'protocol_type', 'service', 'flag from test and train set
# ============================================================================= 

train_data = X_train.join(df_cat_data)


train_data.drop('flag', axis = 1, inplace = True)
train_data.drop('protocol_type', axis = 1, inplace = True)
train_data.drop('service', axis = 1, inplace = True)
print("Train data dimension: ", train_data.shape)


test_data = X_test.join(df_cat_data_test)

test_data.drop('flag', axis = 1, inplace = True)
test_data.drop('protocol_type', axis = 1, inplace = True)
test_data.drop('service', axis = 1, inplace = True)
print("Test data dimension: ", test_data.shape)

# =============================================================================
#                Standard scaler for train and test data
# ============================================================================= 

scaler1 = StandardScaler().fit(train_data)
train_data=scaler1.transform(train_data) 


scaler2 = StandardScaler().fit(test_data)
test_data = scaler2.transform(test_data) 

# =============================================================================
#                        Clustering 
# =============================================================================
 
# ---------------Silhouette Analysis--------------

# silhouette analysis for max number o cluster = 5
# silhouette_analysis(train_data, y_test, range_n_clusters = [2, 3, 4])
#num_clusters(train_data, 5)
# #sil(train_data)


# --------------Clustering Algorithms-------------

# KMEANS
#cl = cluster.KMeans(n_clusters = 2, n_init = 100).fit(train_data)

# DBSCAN 
#cl  = cluster.DBSCAN(eps = 0.8, min_samples = 600).fit(train_data)


# SPECTRAL CLUSTERING
#cl  = cluster.SpectralClustering(n_clusters = 2).fit(train_data)

# MINIBATCHKMEANS
#cl = cluster.MiniBatchKMeans(n_clusters = 2, batch_size = 100).fit(train_data)

# BIRCH
#cl = cluster.Birch(n_clusters = 2, threshold = 1).fit(train_data)

# GaussianMixture
cl = mixture.GaussianMixture(n_components = 2, covariance_type = "spherical", random_state = 0).fit(train_data)

results(test_data, y_test, cl)


# # =============================================================================
# #                Classification using kNN, SVC, RandomForest after clustering
# # =============================================================================
# cl.predict(train_data)
# clusters = cl.labels_

# y_test = y_test.tolist()

# # Assume that class attack is label 1
# for x in range(len(y_test)): 
#     if (y_test[x] == "attack"):
#         y_test[x] = 1
#     else: 
#         y_test[x] = 0
        
# clf = KNeighborsClassifier(n_neighbors = 10, n_jobs = -1)
# # # clf = SVC(kernel = 'rbf', C = 1, random_state = 0)
# # # clf = RandomForestClassifier(n_estimator = 10, n_jobs = -1)


# clf.fit(train_data, clusters)
# y_pred = clf.predict(test_data)


# print('Classifier Accuracy Score: %.3f'  %metrics.accuracy_score(y_test, y_pred))
# print('Recall Score: %.3f'    %metrics.recall_score(y_test, y_pred, average = 'macro'))
# print('Precision Score: %.3f' %metrics.precision_score(y_test, y_pred, average = 'macro'))
# print('f1 Score: %.3f \n'     %metrics.f1_score(y_test, y_pred, average = 'macro'))



