# 数据预处理函数
# version 1.0


import numpy as np
from datetime import datetime
from PyEMD import EMD
import pandas as pd

def all_values_are_same(arr):
    return all(x == arr[0] for x in arr)

def prepareSeriesData(seriesData, n_past, n_future=1):
    """
    滑窗构造LSTM输入与输出
    :param seriesData: 输入数据序列
    :param n_past: 历史步长
    :param n_future: 未来预测步长
    :return: 切分后的输入特征x和标签y
    """
    X = []
    y = []
    for i in range(len(seriesData)-(n_past+n_future-1)):
        temp_x = seriesData[i:i+n_past,0:]  #不算泵频率自己作为输入的话，x从1列开始，算的话从0开始，用下面一行
        temp_y = seriesData[i+n_past,0]
        X.append(temp_x)
        y.append(temp_y)
    X = np.asarray(X)
    y = np.asarray(y)
    return X,y

def prepareSeriesData_nfuture(seriesData, n_past, n_future):
    """
    多步预测的滑窗构造LSTM输入和输出
    :param seriesData:输入数据序列
    :param n_past:历史步长
    :param n_future:预测步长
    :return:切分后的输入特征x和标签y
    """
    X = []
    y = []
    for i in range(len(seriesData)-(n_past+n_future-1)):
        # temp_x = seriesData[i:i+n_past,1:]  #不算泵频率自己作为输入的话，x从1列开始，算的话从0开始，用下面一行
        temp_x = seriesData[i:i+n_past, 0:]
        temp_y = seriesData[i+n_past:i+n_past+n_future,0]
        X.append(temp_x)
        y.append(temp_y)
    X = np.asarray(X)
    y = np.asarray(y)
    return X,y

def abnormalValueRemove(sample_data, col):
    """
    使用3σ原则检测异常值并剔除
    :param sample_data: 输入数组
    :param col: 剔除第几列的异常值
    :return: 处理后的数据
    """
    in_range = sample_data
    state = False
    for i in col:
        data_mean = in_range[:,i].mean()   # 计算均值
        data_std = in_range[:,i].std()   # 计算标准差
        data_max = data_mean + 3 * data_std
        data_min = data_mean - 3 * data_std
        rule = (data_min <= in_range[:,i]) & (data_max >= in_range[:,i]) # 选择 大于μ-3σ 且 小于 μ+3σ的数据，也就是正常值
        index = np.arange(in_range.shape[0])[rule]  # 得到正常值索引
        in_range = in_range[index,:]   # 获取正常数据
    return in_range

def abnormalValueMikong(sample_data, col):
    """
    判断是否存在异常值，适用于密控模型
    :param sample_data: 输入数组：rho, yw, valve
    :param col: 剔除第几列的异常值
    :return: 处理后的数据，是否存在异常值
    """
    meanValue = [1.15, 853, 19]   #均值
    stdValue = [0.51, 1079, 17.3]  #标准差
    in_range = sample_data
    state = False
    for i in col:
        data_max = meanValue[i] + 3 * stdValue[i]
        data_min = meanValue[i] - 3 * stdValue[i]
        not_rule = (data_min > in_range[:, i]) | (data_max < in_range[:, i])  #存在异常值
        if np.any(not_rule):
            state = True
        else:
            state = False
    return state

def abnormalValueJiayao(sample_data, col):
    """
    判断是否存在异常值，适用于加药模型
    :param sample_data: 输入数组：pumpFreq, zd, jm, yl, gdkd
    :param col: 剔除第几列的异常值
    :return: 处理后的数据，是否存在异常值
    """
    meanValue = [23, 4.5, 1.8, 0.7, 54]   #均值
    stdValue = [11, 5.8, 1.13, 0.18, 9.7]  #标准差
    in_range = sample_data
    state = False
    for i in col:
        data_max = meanValue[i] + 3 * stdValue[i]
        data_min = meanValue[i] - 3 * stdValue[i]
        not_rule = (data_min > in_range[:, i]) | (data_max < in_range[:, i])  #存在异常值
        if np.any(not_rule):
            state = True
        else:
            state = False
    return state

def slidingAverage(sample_data, window_size):
    """
    滑动均值滤波
    :param sample_data: 输入数组
    :param window_size: 滑窗尺寸
    :return:
    """
    window = np.ones(window_size) / window_size
    return np.convolve(sample_data, window, mode='same')

def pumpAdjust(sample_data, N=3):
    """
    调整加药泵频率，调整为N的倍数
    :param sample_data:
    :return:
    """
    a = np.arange(0, 48, N)
    for i in range(len(sample_data)):
        sample_data[i] = min(a, key=lambda x: abs(x - sample_data[i]))
        #print(min(a, key=lambda x: abs(x - b)))
    return sample_data

def pumpAdjustMultySteps(sample_data, windowsize):
    """
    输出加药泵频率值调整，采用多步预测后，每一步的值为N次预测该时刻的平均值
    :param sample_data: 输入数据
    :param windowsize: 预测步长
    :return:处理后的数据
    """
    processData = np.zeros(sample_data.shape[0])
    processData[:windowsize] = sample_data[:windowsize].mean(axis=1)
    for i in range(windowsize-1, sample_data.shape[0]-windowsize+1, 1):
        tmpValue = 0
        for j in range(windowsize):
            tmpValue = tmpValue + sample_data[i-windowsize+1+j, j]
        processData[i] = (tmpValue) / windowsize
    processData[sample_data.shape[0]-windowsize+1:-1] = sample_data[sample_data.shape[0]-windowsize+1:-1].mean(axis=1)
    return processData

def densityCtrlPreprocessing(df1, df2, df3, densityDesired, startDay="2024-10-27 00:01:00", days=4, emd_flag=False, emd_cols=0, emd_imfs=0):
    """
    密控模型数据预处理函数
    :param df1: 时间+密度测量
    :param df2: 液位
    :param df3: 分流阀开度设定
    :param densityDesired: 期望密度
    :param startDay: 开始时间
    :param days: 取多少天数据
    :param emd_flag: 是否做EMD分解，默认False
    :param emd_cols: 对第几列做EMD分解
    :param emd_imfs:保留imf的个数
    :return: inputData处理后的输入数据
    """
    # 获取数据
    data_time = df1['DATETIME'].values
    MD_3210_value = df1['VALUE'].values
    YW3208_value = df2['VALUE'].values
    KDSD3249_value = df3['VALUE'].values
    MDSD_valueIntervel = densityDesired

    dataForDays = days * 24 * 60
    value_startDayIndex = np.where(data_time == startDay)[0][0]
    timeDisplayIntervel = data_time[value_startDayIndex:value_startDayIndex + dataForDays + 1:2 * 60]
    xlabels = np.array([])
    time_format = '%H:%M:%S'
    for i in range(len(timeDisplayIntervel)):
        xlabels_tmp = datetime.strptime(timeDisplayIntervel[i], "%Y-%m-%d %H:%M:%S")
        tmp = xlabels_tmp.strftime(time_format)
        xlabels = np.append(xlabels, tmp)

    MD_3210_valueIntervel = MD_3210_value[value_startDayIndex:value_startDayIndex + dataForDays + 1]
    YW3208_valueIntervel = YW3208_value[value_startDayIndex:value_startDayIndex + dataForDays + 1]
    KDSD3249_valueIntervel = KDSD3249_value[value_startDayIndex:value_startDayIndex + dataForDays + 1]
    # KDSD3249_prev_valueIntervel = KDSD3249_value[value_startDayIndex - 1:value_startDayIndex + dataForDays]
    timeIntervel = data_time[value_startDayIndex:value_startDayIndex + dataForDays + 1]
    densityErr_valueIntervel = MD_3210_valueIntervel - MDSD_valueIntervel
    densityErrDot_valueIntervel = densityErr_valueIntervel[1:] - densityErr_valueIntervel[0:-1]
    # 创建数据帧并合并
    timeIntervel = pd.DataFrame({'time': timeIntervel})
    MD_3210_valueIntervel = pd.DataFrame({'MD': MD_3210_valueIntervel})
    YW3208_valueIntervel = pd.DataFrame({'YW': YW3208_valueIntervel})
    KDSD3249_valueIntervel = pd.DataFrame({'KDSD': KDSD3249_valueIntervel})
    # KDSD3249_prev_valueIntervel = pd.DataFrame({'KDSDPREV': KDSD3249_prev_valueIntervel})
    densityErr_valueIntervel = pd.DataFrame({'densityErr': densityErr_valueIntervel})
    densityErrDot_valueIntervel = pd.DataFrame({'densityErrDot': densityErrDot_valueIntervel})

    inputIntervel = pd.concat([timeIntervel, KDSD3249_valueIntervel, MD_3210_valueIntervel, YW3208_valueIntervel, densityErr_valueIntervel], axis=1)
    # inputIntervel = pd.concat([timeIntervel, KDSD3249_valueIntervel, MD_3210_valueIntervel, YW3208_valueIntervel, densityErr_valueIntervel, densityErrDot_valueIntervel], axis=1)
    inputIntervel = inputIntervel.values

    # 检查数据长度并进行调整
    print("Time length:", len(timeIntervel))
    print("Data length:", len(inputIntervel))
    if len(timeIntervel)!= len(inputIntervel):
        min_length = min(len(timeIntervel), len(inputIntervel))
        timeIntervel = timeIntervel[:min_length]
        inputIntervel = inputIntervel[:min_length]

    # # 剔除异常值
    # inputIntervel = abnormalValueRemove(inputIntervel, [3])
    # if emd_flag:
    #     #EEMD 处理
    #     inputIntervel = EMD_process(inputIntervel, emd_cols, emd_imfs)
    #
    # print("剔除异常值后截取区间大小为：", inputIntervel.shape)
    return inputIntervel

def EMD_process(data, range_values, remaining_imfs):
    """
    EMD分解
    :param data:输入数组
    :param range_values: 用于EMD分解的列
    :param remaining_imfs: 保留的imf个数
    :return: 处理后数组
    """
    for i in range(len(range_values)):
        index = range_values[i]
        s = data[:, index]  # 直接使用 range_values 作为列索引选择多列
        emd = EMD()     #创建一个 EMD 对象
        s = s.reshape(-1)
        s = s.astype(float)
        IMFs = emd.emd(s)
        A = 0
        for imf in IMFs[-remaining_imfs:]:
            A = A + imf
        data[:,index] = A
    return data

def EMD_process_v2(data, range_values, unreconstructed_imfs):
    """
    EMD分解
    :param data:输入数组
    :param range_values: 用于EMD分解的列
    :param remaining_imfs: 去掉的imf个数
    :return: 处理后数组
    """
    for i in range(len(range_values)):
        index = range_values[i]
        s = data[:, index]  # 直接使用 range_values 作为列索引选择多列
        emd = EMD()     #创建一个 EMD 对象
        s = s.reshape(-1)
        s = s.astype(float)
        IMFs = emd.emd(s)
        A = 0
        for imf in IMFs[unreconstructed_imfs:]:
            A = A + imf
        data[:,index] = A
    return data

def EMD_process_AddFeature(data, range_values, remaining_imfs):
    """
    EMD分解，并使分解结果作为输入特征
    :param data:输入数据
    :param range_values:待分解的列
    :param remaining_imfs:保留imf个数
    :return:处理后的数据
    """
    newData = data
    for i in range(len(range_values)):
        index = range_values[i]
        s = data[:, index]  # 直接使用 range_values 作为列索引选择多列
        emd = EMD()     #创建一个 EMD 对象
        s = s.reshape(-1)
        s = s.astype(float)
        IMFs = emd.emd(s)
        #检查保留IMFs个数是否超过分解个数
        if IMFs.shape[0] < remaining_imfs:
            remaining_imfs = IMFs.shape[0]
        newDataTmp = np.zeros((data.shape[0], remaining_imfs))
        for num, imf in enumerate(IMFs[-remaining_imfs:]):
            newDataTmp[:,num] = imf
        newData = np.hstack((newData, newDataTmp))
    return newData

def readMikongData(densityDesired, startDay="2024-10-27 00:01:00", days=4):
    """
    读取密控数据，密度、液位和分流阀开度
    :param densityDesired: 期望密度
    :param startDay: 起始天，默认为"2024-10-27 00:01:00"
    :param days: 读取数据天数，默认为4
    :return: 读取并整理后的数据（列排序按模型顺序）
    """
    df1 = pd.read_csv('output_file_MD_3210.csv', encoding='utf-8')  # 密度
    df2 = pd.read_csv('output_file_3208YW.csv', encoding='utf-8')  # 液位
    df3 = pd.read_csv('output_file_3249KDSD.csv', encoding='utf-8')  # 开度设定

    data_time = df1['DATETIME'].values
    MD_3210_value = df1['VALUE'].values
    YW3208_value = df2['VALUE'].values
    KDSD3249_value = df3['VALUE'].values
    MDSD_valueIntervel = densityDesired

    dataForDays = days * 24 * 60
    value_startDayIndex = np.where(data_time == startDay)[0][0]
    timeDisplayIntervel = data_time[value_startDayIndex:value_startDayIndex + dataForDays + 1:2 * 60]
    xlabels = np.array([])
    time_format = '%H:%M:%S'
    for i in range(len(timeDisplayIntervel)):
        xlabels_tmp = datetime.strptime(timeDisplayIntervel[i], "%Y-%m-%d %H:%M:%S")
        tmp = xlabels_tmp.strftime(time_format)
        xlabels = np.append(xlabels, tmp)

    MD_3210_valueIntervel = MD_3210_value[value_startDayIndex:value_startDayIndex + dataForDays + 1]
    MD_3210_ChangeRate_valueIntervel = MD_3210_valueIntervel[1:] - MD_3210_valueIntervel[0:-1]
    YW3208_valueIntervel = YW3208_value[value_startDayIndex:value_startDayIndex + dataForDays + 1]
    YW3208_ChangeRate_valueIntervel = YW3208_valueIntervel[1:] - YW3208_valueIntervel[0:-1]
    KDSD3249_valueIntervel = KDSD3249_value[value_startDayIndex:value_startDayIndex + dataForDays + 1]
    KDSD_ChangeRate_valueIntervel = KDSD3249_valueIntervel[1:] - KDSD3249_valueIntervel[0:-1]

    MD_3210_valueIntervel = MD_3210_valueIntervel[1:]
    YW3208_valueIntervel = YW3208_valueIntervel[1:]
    KDSD3249_valueIntervel = KDSD3249_valueIntervel[1:]

    MD_3210_valueIntervel = pd.DataFrame({'MD': MD_3210_valueIntervel})
    MD_3210_ChangeRate_valueIntervel = pd.DataFrame({'MD_3210_ChangeRate': MD_3210_ChangeRate_valueIntervel})
    YW3208_valueIntervel = pd.DataFrame({'YW': YW3208_valueIntervel})
    YW3208_ChangeRate_valueIntervel = pd.DataFrame({'YW3208_ChangeRate': YW3208_ChangeRate_valueIntervel})
    KDSD3249_valueIntervel = pd.DataFrame({'KDSD': KDSD3249_valueIntervel})
    KDSD_ChangeRate_valueIntervel = pd.DataFrame({'KDSD_ChangeRate': KDSD_ChangeRate_valueIntervel})


    #返回数据格式，Y放第一个位置

    # inputIntervel = pd.concat([KDSD3249_valueIntervel, KDSD_ChangeRate_valueIntervel, MD_3210_valueIntervel, \
    #                            MD_3210_ChangeRate_valueIntervel, YW3208_valueIntervel, YW3208_ChangeRate_valueIntervel], axis=1)

    #密度预测用
    inputIntervel = pd.concat([MD_3210_valueIntervel, KDSD3249_valueIntervel, KDSD_ChangeRate_valueIntervel, \
                               YW3208_valueIntervel, YW3208_ChangeRate_valueIntervel], axis=1)
    #液位预测用
    # inputIntervel = pd.concat([YW3208_valueIntervel, YW3208_ChangeRate_valueIntervel, MD_3210_valueIntervel, KDSD3249_valueIntervel, KDSD_ChangeRate_valueIntervel], axis=1)

    inputIntervel = inputIntervel.values

    return inputIntervel
