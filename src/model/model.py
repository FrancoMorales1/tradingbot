import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from joblib import dump
from ..utils.utils import adjust_values

data_frame = pd.read_csv('data_for_model/btc_price_data.csv')
col = ['open_time','open','high','low','close']
open_X_array = []
high_X_array = []
low_X_array = []
close_X_array = []

open_y_array = []
high_y_array = []
low_y_array = []
close_y_array = []

j=0
for i in range(0,data_frame.shape[0]-4):
    open_X_array.append(np.asarray(data_frame.iloc[i:i+3,1]))
    high_X_array.append(np.asarray(data_frame.iloc[i:i+3,2]))
    low_X_array.append(np.asarray(data_frame.iloc[i:i+3,3]))
    close_X_array.append(np.asarray(data_frame.iloc[i:i+3,4]))

    open_X_array[j][np.isnan(open_X_array[j])]=0
    high_X_array[j][np.isnan(high_X_array[j])]=0
    low_X_array[j][np.isnan(low_X_array[j])]=0
    close_X_array[j][np.isnan(close_X_array[j])]=0

    maxValue_open = max(open_X_array[j])
    maxValue_high = max(high_X_array[j])
    maxValue_low = max(low_X_array[j])
    maxValue_close = max(close_X_array[j])
    
    open_y_array.append('Comprar' if maxValue_open < data_frame.iloc[i+4,1] else ('Vender' if maxValue_open > data_frame.iloc[i+4,1] else 'Nada'))
    high_y_array.append('Comprar' if maxValue_high < data_frame.iloc[i+4,2] else ('Vender' if maxValue_high > data_frame.iloc[i+4,2] else 'Nada'))
    low_y_array.append('Comprar' if maxValue_low < data_frame.iloc[i+4,3] else ('Vender' if maxValue_low > data_frame.iloc[i+4,3] else 'Nada'))
    close_y_array.append('Comprar' if maxValue_close < data_frame.iloc[i+4,4] else ('Vender' if maxValue_close > data_frame.iloc[i+4,4] else 'Nada'))

    j=j+1

X_open = adjust_values(open_X_array)
X_high = adjust_values(high_X_array)
X_low = adjust_values(low_X_array)
X_close = adjust_values(close_X_array)

y_open = open_y_array
y_high = high_y_array
y_low = low_y_array
y_close = close_y_array

X_train_open, X_test_open, y_train_open, y_test_open = train_test_split(X_open, y_open, test_size=0.3)
X_train_high, X_test_high, y_train_high, y_test_high = train_test_split(X_high, y_high, test_size=0.3)
X_train_low, X_test_low, y_train_low, y_test_low = train_test_split(X_low, y_low, test_size=0.3)
X_train_close, X_test_close, y_train_close, y_test_close = train_test_split(X_close, y_close, test_size=0.3)

knn_open = KNeighborsClassifier(n_neighbors=100)
knn_high = KNeighborsClassifier(n_neighbors=100)
knn_low = KNeighborsClassifier(n_neighbors=100)
knn_close = KNeighborsClassifier(n_neighbors=100)

knn_open.fit(X_train_open,y_train_open)
knn_high.fit(X_train_high,y_train_high)
knn_low.fit(X_train_low,y_train_low)
knn_close.fit(X_train_close,y_train_close)

y_pred_open = knn_open.predict(X_test_open)
y_pred_high = knn_high.predict(X_test_high)
y_pred_low = knn_low.predict(X_test_low)
y_pred_close = knn_close.predict(X_test_close)

print(metrics.accuracy_score(y_test_open, y_pred_open))
print(metrics.accuracy_score(y_test_high, y_pred_high))
print(metrics.accuracy_score(y_test_low, y_pred_low))
print(metrics.accuracy_score(y_test_close, y_pred_close))

dump(knn_open,'models_created/model_open.joblib')
dump(knn_high,'models_created/model_high.joblib')
dump(knn_low,'models_created/model_low.joblib')
dump(knn_close,'models_created/model_close.joblib')