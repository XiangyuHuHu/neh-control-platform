## 通过过去浊度、耙压、界面仪等参数预测未来浊度变化
## version 2.0  updated in 20250918

import os
import keras
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import Input
from keras.models import Model
from keras.callbacks import *
from keras.optimizers import *
import math
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error
from scipy import stats
from sklearn.preprocessing import StandardScaler

from copy import deepcopy

if __name__ == '__main__':
    import sys, os
    ctrl_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ctrl包所在的目录
    sys.path.append(ctrl_dir)


#定义参数
n_past = 5   #历史步长 m
n_future = 1   #预测步长
evaluate = False
startDay = "2024-10-27 00:01:00"    #哪天开始取值
days = 4   #连续取多少天数据
desired = 1.38
n_features = 5

inputIntervel = readJiaYaoData(desired, startDay, days)

inputIntervel = inputIntervel[inputIntervel[:,0] >= 0.8]
inputIntervel = abnormalValueRemove(inputIntervel, [0])    #剔除异常值

train_size = int(len(inputIntervel)*0.75)   #训练数据尺寸
test_size = len(inputIntervel)-train_size   #测试数据尺寸
train_data = inputIntervel[:train_size ,0:]
test_data = inputIntervel[train_size: ,0:]

## 3. 数据切分与准备
X_train, y_train = prepareSeriesData(train_data, n_past)      #从训练数据里切分输入与输出
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], n_features))   #整理为LSTM的三输入格式[样本数量，步长，特征数]
X_test, y_test = prepareSeriesData(test_data,n_past)
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], n_features))

X_train = X_train.astype('float64')
y_train = y_train.astype('float64')
X_test = X_test.astype('float64')

x_scalar = StandardScaler()
X_train = x_scalar.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
X_test = x_scalar.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)

y_scalar = StandardScaler()
y_train = y_scalar.fit_transform(y_train.reshape(y_train.shape[-1], -1)).reshape(y_train.shape)
y_test = y_scalar.transform(y_test.reshape(y_test.shape[-1], -1)).reshape(y_test.shape)

model = build_lstm_model(X_train.shape[1:])
model.summary()  #打印模型结构

weight_path = 'JiaYaoBest-4feature-60stepsIn-10StpesOut-20241115test10.model.keras'  # 保存模型路径及文件名
checkpointer = ModelCheckpoint(filepath=weight_path, monitor='val_loss', save_best_only=True, verbose=1)  # 迭代过程保存最佳模型
es = EarlyStopping(monitor='val_loss', mode='min', patience=10, verbose=1)  # 早停
reduce = ReduceLROnPlateau(monitor='val_loss', mode='min', factor=0.5, patience=3, verbose=1)  # 如果不下降就调整学习率

history = model.fit(X_train, y_train, epochs=200, batch_size=32, validation_data=[X_train, y_train], callbacks=[checkpointer, es, reduce])
plt.figure()
plt.plot(history.history['loss'], c='b', label='loss')
plt.legend()
plt.show()

pred_test = model.predict(X_test)
#反归一化
pred_test = y_scalar.inverse_transform(pred_test.reshape(-1, pred_test.shape[-1])).reshape(-1,)
y_test = y_scalar.inverse_transform(y_test.reshape(y_test.shape[-1], -1)).reshape(-1,)

print("test Pred Values-- ", pred_test)
print("\ntest Original Values-- ", y_test)
plt.plot(y_test, color = 'red', label = 'real value')
plt.plot(pred_test, color = 'blue', label = 'predicted value')
plt.legend()
plt.show()

# 计算误差

testScore2 = mean_absolute_error(y_test, pred_test)
print('平均绝对误差MAE: %.2f' % (testScore2))
mape2 = testScore2/np.mean(y_test)
print('平均绝对误差百分比MAPE: %.2f' % (mape2*100))
