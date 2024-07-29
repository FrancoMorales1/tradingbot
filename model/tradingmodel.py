import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from joblib import dump, load

df = pd.read_csv('output.csv')
col = ['open_time','open','high','low','close']
n = int((df.shape[0]-100000))
d = []
result = []
j=0
for i in range((df.shape[0]-75000),df.shape[0]-4):
    d.append(np.asarray(df.iloc[i:i+3,1]))
    d[j][np.isnan(d[j])]=0

    maxValue = max(d[j])
    if (maxValue < df.iloc[i+4,4]):
        result.append('Comprar')
    elif (maxValue == df.iloc[i+4,4]):
        result.append('Nada')
    else:
        result.append('Vender')
    j=j+1

X = d
y = result

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train,y_train)
y_pred = knn.predict(X_test)
print(y_pred)
j = -1
arr =[]
for x in y_pred:
    if(x=='Comprar'):
        if(j!=-1 and arr[j][0]=='Comprar'):
            arr[j][1] += 1
        else:
            arr.append(['Comprar',1])
            j+=1
    elif (x=='Vender'):
        if(j!=-1 and arr[j][0]=='Vender'):
            arr[j][1] += 1
        else:
            arr.append(['Vender',1])
            j+=1

usdt=100
btc=0.0001
cantCompraBTC=0.0001
cantVentaBTC=0.0001
contadorOportunidadesPerdidasVenta = 0
contadorOportunidadesPerdidasCompra = 0
for x, y in zip(X_test, y_pred):
    if y=='Comprar':
        if (usdt - cantCompraBTC*min(x) >= 0):
            usdt = usdt - cantCompraBTC*min(x)
            btc = btc + cantCompraBTC
        else:
            contadorOportunidadesPerdidasCompra += 1
    elif y=='Vender':
        if(btc - cantVentaBTC >= 0):
            btc = btc - cantVentaBTC
            usdt = usdt + cantVentaBTC*max(x)
        else:
            contadorOportunidadesPerdidasVenta +=1
    else:
        pass
print('Tiempo transcurrido')
print(str(len(y_pred)/(60*24))+'Dias')
print('Plata inicial')
print(str(100 + 0.0001*57507.99)+' USDT')
print('Plata final')
print(str(usdt)+' USDT')
print(str(btc)+' BTC')
print('Ganancia final')
print(str(usdt - 100)+' USDT')
print(str(btc - 0.0001)+' BTC')
print('Ganancia final en dolares')
print(str((usdt - 100) + (btc - 0.0001)*58693.43)+' USDT')
print('Contador oportunidades perdidas de compra')
print(contadorOportunidadesPerdidasCompra)
print('Contador oportunidades perdidas de venta')
print(contadorOportunidadesPerdidasVenta)
print(metrics.accuracy_score(y_test, y_pred))
dump(knn,'decisionModel.joblib')