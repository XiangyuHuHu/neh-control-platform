# version 2.0   updated in 20250918

import numpy as np
import pandas as pd
import keras
from utils.dataPreprocess import slidingAverage
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from utils.algorithm import *
from utils.algorithm import jiayao_controller_601, jiayao_controller_602, jiayao_controller_5201, jiayao_controller_5202
from utils.dataPreprocess import all_values_are_same
from scipy.ndimage import gaussian_filter1d

data_Freq = 5   #数据读取频率，5s
minutePerIndex = int(60/data_Freq)   #每分钟数据个数
lower_limit = 20

def jiayaoCtrl601(ZD, PY, JM, PDC, pump, MN_in, ZD_SD, PY_max, update_ctrl, para1 ,para2, para3, JM_measured):


    global jiayao_controller_601
    state_name = "正常"  # 状态，0正常，1停车，2压耙，3浊度过高
    state = 0
    pumpNext = 0
    Gain = 100
    valve_MN = MN_in[-1]
    base = 20
    bkpumpNext = 0

    JM_errorRange = 0.5


    sigma = 5
    sigma2 = 5
    ZD_filter = gaussian_filter1d(ZD, sigma)[-1]
    PY_filter = gaussian_filter1d(PY, sigma2)[-1]
    JM_filter = gaussian_filter1d(JM, sigma)[-1]
    ZD_filter_array = gaussian_filter1d(ZD, sigma)
    PY_filter_array = gaussian_filter1d(PY, sigma2)
    JM_filter_array = gaussian_filter1d(JM, sigma2)

    print("---浊度计当前测量值为：%.2f---滤波值为：%.2f---" % (ZD[-1], ZD_filter))
    print("---耙压当前测量值为：%.2f---滤波值为：%.2f---耙压最大值为：%.2f---" % (PY[-1], PY_filter, PY_max))
    print("---界面仪当前测量值为：%.2f---滤波值：%.4f---2小时测量值为：%.3f---" % (JM[-1], JM_filter, JM_measured))


    fitIntervel = -5 * minutePerIndex
    ZD_trend_5 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -10 * minutePerIndex
    ZD_trend_10 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -30 * minutePerIndex
    ZD_trend_30 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]


    fitIntervel = -5 * minutePerIndex
    coeff_linear = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(10 * minutePerIndex))

    ZD_future_1 = y_fit_linear[-5 * minutePerIndex]
    ZD_future_5 = y_fit_linear[-1]


    fitIntervel = -30 * minutePerIndex
    coeff_linear = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(90 * minutePerIndex))

    ZD_future_30 = y_fit_linear[-30 * minutePerIndex]
    ZD_future_60 = y_fit_linear[-1]
    print("---5min浊度变化率：%.4f---10min浊度变化率：%.4f---30min浊度变化率：%.4f---" % (ZD_trend_5, ZD_trend_10, ZD_trend_30))
    print("---未来1min浊度趋势预测：%.2f---未来5min浊度趋势预测：%.2f---未来30min浊度趋势预测：%.2f---未来60min浊度趋势预测: %.2f---" % (ZD_future_1, ZD_future_5,y_fit_linear[-30 * minutePerIndex], y_fit_linear[-1]))



    fitIntervel = -5 * minutePerIndex
    PY_trend_5 = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -30 * minutePerIndex
    PY_trend_30 = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)[0]


    fitIntervel = -5 * minutePerIndex
    coeff_linear = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(10 * minutePerIndex))

    PY_future_1 = y_fit_linear[-5 * minutePerIndex]
    PY_future_5 = y_fit_linear[-1]


    fitIntervel = -30 * minutePerIndex
    coeff_linear = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(90 * minutePerIndex))

    PY_future_30 = y_fit_linear[-30 * minutePerIndex]
    PY_future_60 = y_fit_linear[-1]

    print("---5min耙压变化率：%.4f---30min耙压变化率：%.4f---" % (PY_trend_5, PY_trend_30))
    print("---未来1min耙压趋势预测：%.2f---未来5min耙压趋势预测：%.2f---未来30min耙压趋势预测：%.2f---未来60min耙压趋势预测: %.2f---" % (PY_future_1, PY_future_5, y_fit_linear[-30 * minutePerIndex], y_fit_linear[-1]))



    if np.mean(ZD[-5*minutePerIndex:]) < ZD_SD:
        update_ctrl = True

    if update_ctrl:
        print("---加药泵控制器初始化---")
        jiayao_controller_601 = Controller(1, para1, para2, para3, -50, 50)


    #----------------------------异常情况-------------------
    if np.mean(PDC[-5*minutePerIndex:]) <= 100:
        state = 1
        state_name = "无煤"
        print("---无煤---")
        pumpNext = 0
        return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

    if PY_filter >= PY_max:
        state = 2
        state_name = "压耙"
        print("---压耙---")
        pumpNext = 0
        return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

    if PY_trend_5 >= 0.05:
        state = 3
        state_name = "耙压变化异常"

    #-----------------------------------耙压正常情况------------------------------------------
    # if ZD_filter >= ZD_SD:
    ZD_filter_calc = ZD_filter
    # if ZD_filter >= 20 + ZD_SD:
    #     ZD_filter_calc = 20 + ZD_SD

    pumpNext_ctrl = jiayao_controller_601.update_Jiayao_AntiWindup(ZD_SD, ZD_filter_calc, para1, para2, para3)
    pumpNext_ctrl = base + ((50 - base) / (50 - 0)) * (pumpNext_ctrl - 0)

    if pumpNext_ctrl <= lower_limit:
        pumpNext_ctrl = lower_limit


    pumpNext = pumpNext_ctrl

    print("---加药泵反馈：%.2f---" % pump[-1])
    print("---加药控制器计算结果：%d---" % pumpNext)

    delta_ZD = 0
    delta_MN = 0
    delta_PY = 0
    delta_PDC = 0
    delta_JM = 0

    delta_MN = MN_in[-1] / 30


    if ZD_trend_10 >= 0 and ZD_future_60 >= ZD_SD and ZD_future_60 > ZD_filter:
        if ZD_future_60 - ZD_filter >= 10:  #10-15   #8-10
            x = ZD_future_60 - ZD_filter
            delta_ZD = 8 + ((x - 10) * (10 - 8)) / (50 - 10)
        if ZD_future_60 - ZD_filter >= 1 and ZD_future_60 - ZD_filter < 10:  # 6-10  #5-8
            # delta_ZD = round(ZD_future_60 - ZD_filter) / 2
            x = ZD_future_60 - ZD_filter
            delta_ZD = 5 + ((x - 1) * (8 - 5)) / (10 - 1)
        elif ZD_future_60 - ZD_filter < 1 and ZD_future_60 - ZD_filter >= 0.1:  # 2-5  #2-5
            # delta_ZD = round(ZD_future_60 - ZD_filter) * 5
            x = ZD_future_60 - ZD_filter
            delta_ZD = 2 + ((x - 0.1) * (5 - 2)) / (1 - 0.1)
        else:    #1-2
            # delta_ZD = round(ZD_future_60 - ZD_filter) * 10
            x = ZD_future_60 - ZD_filter
            delta_ZD = 0 + ((x - 0) * (2 - 0)) / (0.1 - 0)

    if delta_ZD >= 10:
        delta_ZD = 10

    if PY_filter >= 1.2 and PY_future_60 >= 1.2 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 4
    if PY_filter >= 1.5 and PY_future_60 >= 1.5 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 7
    if PY_filter >= 2.0 and PY_future_60 >= 2.0 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 10

    if delta_PY <= -10:
        delta_PY = -10

    delta_MN = (np.mean(PDC[-12:])*MN_in[-1]) / 10000

    delta_JM = -(JM_filter - 1.5) * 4

    pumpNext = round(pumpNext + delta_MN + delta_ZD + delta_PDC + delta_JM)
    print("---煤泥入料修正量：%.2f---浊度趋势修正量：%.2f---耙压趋势修正量：%.2f---界面仪修正量：%.2f---" % (delta_MN, delta_ZD, delta_PY, delta_JM))

    #停泵
    if JM_filter >= 1.5 and PY_filter >= 1.5 and ZD_filter <= ZD_SD and ZD_future_5 <= ZD_SD and ZD_future_60 <= ZD_SD:
        print("---停泵---界面仪正常，浊度正常，耙压正常，未来不会超过浊度高值---")
        pumpNext = 0

    print("---加药控制器修正结果：%d---" % pumpNext)

    if pumpNext < lower_limit:
        pumpNext = 0
    if pumpNext >= 50:
        pumpNext = 50
        bkpumpNext = pumpNext - 50
        bkpumpNext = bkpumpNext + 20
        if bkpumpNext >= 50:
            bkpumpNext = 50

    print("-----------------------------------------------------------------------------")

    return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name


def jiayaoCtrl602(ZD, PY, JM, PDC, pump, MN_in, ZD_SD, PY_max, update_ctrl, para1 ,para2, para3, JM_measured):

    global jiayao_controller_602
    state_name = "正常"  # 状态，0正常，1停车，2压耙，3浊度过高
    state = 0
    pumpNext = 0
    Gain = 100
    valve_MN = MN_in[-1]
    base = 20
    JM_errorRange = 0.5
    bkpumpNext = 0

    sigma = 5
    sigma2 = 5
    ZD_filter = gaussian_filter1d(ZD, sigma)[-1]
    PY_filter = gaussian_filter1d(PY, sigma2)[-1]
    JM_filter = gaussian_filter1d(JM, sigma)[-1]
    ZD_filter_array = gaussian_filter1d(ZD, sigma)
    PY_filter_array = gaussian_filter1d(PY, sigma2)
    JM_filter_array = gaussian_filter1d(JM, sigma2)

    print("---浊度计当前测量值为：%.2f---滤波值为：%.2f---" % (ZD[-1], ZD_filter))
    print("---耙压当前测量值为：%.2f---滤波值为：%.2f---耙压最大值为：%.2f---" % (PY[-1], PY_filter, PY_max))
    print("---界面仪当前测量值为：%.2f---滤波值：%.4f---2小时测量值为：%.3f---" % (JM[-1], JM_filter, JM_measured))


    fitIntervel = -5 * minutePerIndex
    ZD_trend_5 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -10 * minutePerIndex
    ZD_trend_10 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -30 * minutePerIndex
    ZD_trend_30 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]


    fitIntervel = -5 * minutePerIndex
    coeff_linear = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(10 * minutePerIndex))

    ZD_future_1 = y_fit_linear[-5 * minutePerIndex]
    ZD_future_5 = y_fit_linear[-1]


    fitIntervel = -30 * minutePerIndex
    coeff_linear = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(90 * minutePerIndex))

    ZD_future_30 = y_fit_linear[-30 * minutePerIndex]
    ZD_future_60 = y_fit_linear[-1]
    print("---5min浊度变化率：%.4f---10min浊度变化率：%.4f---30min浊度变化率：%.4f---" % (
    ZD_trend_5, ZD_trend_10, ZD_trend_30))
    print(
        "---未来1min浊度趋势预测：%.2f---未来5min浊度趋势预测：%.2f---未来30min浊度趋势预测：%.2f---未来60min浊度趋势预测: %.2f---" % (
        ZD_future_1, ZD_future_5, y_fit_linear[-30 * minutePerIndex], y_fit_linear[-1]))


    fitIntervel = -5 * minutePerIndex
    PY_trend_5 = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -30 * minutePerIndex
    PY_trend_30 = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)[0]


    fitIntervel = -5 * minutePerIndex
    coeff_linear = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(10 * minutePerIndex))

    PY_future_1 = y_fit_linear[-5 * minutePerIndex]
    PY_future_5 = y_fit_linear[-1]


    fitIntervel = -30 * minutePerIndex
    coeff_linear = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(90 * minutePerIndex))

    PY_future_30 = y_fit_linear[-30 * minutePerIndex]
    PY_future_60 = y_fit_linear[-1]

    print("---5min耙压变化率：%.4f---30min耙压变化率：%.4f---" % (PY_trend_5, PY_trend_30))
    print(
        "---未来1min耙压趋势预测：%.2f---未来5min耙压趋势预测：%.2f---未来30min耙压趋势预测：%.2f---未来60min耙压趋势预测: %.2f---" % (
        PY_future_1, PY_future_5, y_fit_linear[-30 * minutePerIndex], y_fit_linear[-1]))

    if np.mean(ZD[-5 * minutePerIndex:]) < ZD_SD:
        update_ctrl = True

    if update_ctrl:
        print("---加药泵控制器初始化---")
        jiayao_controller_602 = Controller(1, para1, para2, para3, -50, 50)

    # ----------------------------异常情况-------------------
    if np.mean(PDC[-5 * minutePerIndex:]) <= 100:
        state = 1
        state_name = "无煤"
        print("---无煤---")
        pumpNext = 0
        return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

    if PY_filter >= PY_max:
        state = 2
        state_name = "压耙"
        print("---压耙---")
        pumpNext = 0
        return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

    if PY_trend_5 >= 0.05:
        state = 3
        state_name = "耙压变化异常"


    # -----------------------------------耙压正常情况------------------------------------------
    # if ZD_filter >= ZD_SD:
    ZD_filter_calc = ZD_filter
    # if ZD_filter >= 20 + ZD_SD:
    #     ZD_filter_calc = 20 + ZD_SD

    pumpNext_ctrl = jiayao_controller_602.update_Jiayao_AntiWindup(ZD_SD, ZD_filter_calc, para1, para2, para3)
    pumpNext_ctrl = base + ((50 - base) / (50 - 0)) * (pumpNext_ctrl - 0)
    # if pumpNext_ctrl >= 50:
    #     pumpNext_ctrl = 50
    if pumpNext_ctrl <= lower_limit:
        pumpNext_ctrl = lower_limit


    pumpNext = pumpNext_ctrl

    print("---加药泵反馈：%.2f---" % pump[-1])
    print("---加药控制器计算结果：%d---" % pumpNext)

    delta_ZD = 0
    delta_MN = 0
    delta_PY = 0
    delta_PDC = 0
    delta_JM = 0

    delta_MN = MN_in[-1] / 30

    if ZD_trend_10 >= 0 and ZD_future_60 >= ZD_SD and ZD_future_60 > ZD_filter:
        if ZD_future_60 - ZD_filter >= 10:  #10-15   #8-10
            x = ZD_future_60 - ZD_filter
            delta_ZD = 8 + ((x - 10) * (10 - 8)) / (50 - 10)
        if ZD_future_60 - ZD_filter >= 1 and ZD_future_60 - ZD_filter < 10:  # 6-10  #5-8
            # delta_ZD = round(ZD_future_60 - ZD_filter) / 2
            x = ZD_future_60 - ZD_filter
            delta_ZD = 5 + ((x - 1) * (8 - 5)) / (10 - 1)
        elif ZD_future_60 - ZD_filter < 1 and ZD_future_60 - ZD_filter >= 0.1:  # 2-5  #2-5
            # delta_ZD = round(ZD_future_60 - ZD_filter) * 5
            x = ZD_future_60 - ZD_filter
            delta_ZD = 2 + ((x - 0.1) * (5 - 2)) / (1 - 0.1)
        else:    #1-2
            # delta_ZD = round(ZD_future_60 - ZD_filter) * 10
            x = ZD_future_60 - ZD_filter
            delta_ZD = 0 + ((x - 0) * (2 - 0)) / (0.1 - 0)

    if delta_ZD >= 10:
        delta_ZD = 10


    if PY_filter >= 1.2 and PY_future_60 >= 1.2 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 4
    if PY_filter >= 1.5 and PY_future_60 >= 1.5 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 7
    if PY_filter >= 2.0 and PY_future_60 >= 2.0 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 10

    if delta_PY <= -10:
        delta_PY = -10

    delta_MN = (np.mean(PDC[-12:])*MN_in[-1]) / 10000


    delta_JM = -(JM_filter - 1.5) * 4

    pumpNext = round(pumpNext + delta_MN + delta_ZD + delta_PDC + delta_JM)
    print("---煤泥入料修正量：%.2f---浊度趋势修正量：%.2f---耙压趋势修正量：%.2f---界面仪修正量：%.2f---" % (delta_MN, delta_ZD, delta_PY, delta_JM))

    #停泵
    if JM_filter >= 1.5 and PY_filter >= 1.5 and ZD_filter <= ZD_SD and ZD_future_5 <= ZD_SD and ZD_future_60 <= ZD_SD:
        print("---停泵---界面仪正常，浊度正常，耙压正常，未来不会超过浊度高值---")
        pumpNext = 0

    print("---加药控制器修正结果：%d---" % pumpNext)

    if pumpNext < lower_limit:
        pumpNext = 0
    if pumpNext >= 50:
        pumpNext = 50
        bkpumpNext = pumpNext - 50
        bkpumpNext = bkpumpNext + 20
        if bkpumpNext >= 50:
            bkpumpNext = 50

    print("-----------------------------------------------------------------------------")

    return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

def jiayaoCtrl5201(ZD, PY, JM, PDC, pump, MN_in, ZD_SD, PY_max, update_ctrl, para1 ,para2, para3, JM_measured):

    global jiayao_controller_5201
    state_name = "正常"  # 状态，0正常，1停车，2压耙，3浊度过高
    state = 0
    pumpNext = 0
    Gain = 100
    valve_MN = MN_in[-1]
    base = 20
    JM_errorRange = 0.5
    bkpumpNext = 0

    sigma = 5
    sigma2 = 5
    ZD_filter = gaussian_filter1d(ZD, sigma)[-1]
    PY_filter = gaussian_filter1d(PY, sigma2)[-1]
    JM_filter = gaussian_filter1d(JM, sigma)[-1]
    ZD_filter_array = gaussian_filter1d(ZD, sigma)
    PY_filter_array = gaussian_filter1d(PY, sigma2)
    JM_filter_array = gaussian_filter1d(JM, sigma2)

    print("---浊度计当前测量值为：%.2f---滤波值为：%.2f---" % (ZD[-1], ZD_filter))
    print("---耙压当前测量值为：%.2f---滤波值为：%.2f---耙压最大值为：%.2f---" % (PY[-1], PY_filter, PY_max))
    print("---界面仪当前测量值为：%.2f---滤波值：%.4f---2小时测量值为：%.3f---" % (JM[-1], JM_filter, JM_measured))

    fitIntervel = -5 * minutePerIndex
    ZD_trend_5 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -10 * minutePerIndex
    ZD_trend_10 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -30 * minutePerIndex
    ZD_trend_30 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]

    fitIntervel = -5 * minutePerIndex
    coeff_linear = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(10 * minutePerIndex))

    ZD_future_1 = y_fit_linear[-5 * minutePerIndex]
    ZD_future_5 = y_fit_linear[-1]

    fitIntervel = -30 * minutePerIndex
    coeff_linear = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(90 * minutePerIndex))

    ZD_future_30 = y_fit_linear[-30 * minutePerIndex]
    ZD_future_60 = y_fit_linear[-1]
    print("---5min浊度变化率：%.4f---10min浊度变化率：%.4f---30min浊度变化率：%.4f---" % (
    ZD_trend_5, ZD_trend_10, ZD_trend_30))
    print(
        "---未来1min浊度趋势预测：%.2f---未来5min浊度趋势预测：%.2f---未来30min浊度趋势预测：%.2f---未来60min浊度趋势预测: %.2f---" % (
        ZD_future_1, ZD_future_5, y_fit_linear[-30 * minutePerIndex], y_fit_linear[-1]))


    fitIntervel = -5 * minutePerIndex
    PY_trend_5 = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -30 * minutePerIndex
    PY_trend_30 = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)[0]


    fitIntervel = -5 * minutePerIndex
    coeff_linear = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(10 * minutePerIndex))

    PY_future_1 = y_fit_linear[-5 * minutePerIndex]
    PY_future_5 = y_fit_linear[-1]


    fitIntervel = -30 * minutePerIndex
    coeff_linear = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(90 * minutePerIndex))

    PY_future_30 = y_fit_linear[-30 * minutePerIndex]
    PY_future_60 = y_fit_linear[-1]

    print("---5min耙压变化率：%.4f---30min耙压变化率：%.4f---" % (PY_trend_5, PY_trend_30))
    print(
        "---未来1min耙压趋势预测：%.2f---未来5min耙压趋势预测：%.2f---未来30min耙压趋势预测：%.2f---未来60min耙压趋势预测: %.2f---" % (
        PY_future_1, PY_future_5, y_fit_linear[-30 * minutePerIndex], y_fit_linear[-1]))

    if np.mean(ZD[-5 * minutePerIndex:]) < ZD_SD:
        update_ctrl = True

    if update_ctrl:
        print("---加药泵控制器初始化---")
        jiayao_controller_5201 = Controller(1, para1, para2, para3, -50, 50)


    # ----------------------------异常情况-------------------
    if np.mean(PDC[-5 * minutePerIndex:]) <= 100:
        state = 1
        state_name = "无煤"
        print("---无煤---")
        pumpNext = 0
        return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

    if PY_filter >= PY_max:
        state = 2
        state_name = "压耙"
        print("---压耙---")
        pumpNext = 0
        return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

    if PY_trend_5 >= 0.05:
        state = 3
        state_name = "耙压变化异常"


    # -----------------------------------耙压正常情况------------------------------------------
    # if ZD_filter >= ZD_SD:
    ZD_filter_calc = ZD_filter
    # if ZD_filter >= 20 + ZD_SD:
    #     ZD_filter_calc = 20 + ZD_SD

    pumpNext_ctrl = jiayao_controller_5201.update_Jiayao_AntiWindup(ZD_SD, ZD_filter_calc, para1, para2, para3)
    pumpNext_ctrl = base + ((50 - base) / (50 - 0)) * (pumpNext_ctrl - 0)
    # if pumpNext_ctrl >= 50:
    #     pumpNext_ctrl = 50
    if pumpNext_ctrl <= lower_limit:
        pumpNext_ctrl = lower_limit


    pumpNext = pumpNext_ctrl

    print("---加药泵反馈：%.2f---" % pump[-1])
    print("---加药控制器计算结果：%d---" % pumpNext)

    delta_ZD = 0
    delta_MN = 0
    delta_PY = 0
    delta_PDC = 0
    delta_JM = 0

    delta_MN = MN_in[-1] / 30


    if ZD_trend_10 >= 0 and ZD_future_60 >= ZD_SD and ZD_future_60 > ZD_filter:
        if ZD_future_60 - ZD_filter >= 10:  #10-15   #8-10
            x = ZD_future_60 - ZD_filter
            delta_ZD = 8 + ((x - 10) * (10 - 8)) / (50 - 10)
        if ZD_future_60 - ZD_filter >= 1 and ZD_future_60 - ZD_filter < 10:  # 6-10  #5-8
            # delta_ZD = round(ZD_future_60 - ZD_filter) / 2
            x = ZD_future_60 - ZD_filter
            delta_ZD = 5 + ((x - 1) * (8 - 5)) / (10 - 1)
        elif ZD_future_60 - ZD_filter < 1 and ZD_future_60 - ZD_filter >= 0.1:  # 2-5  #2-5
            # delta_ZD = round(ZD_future_60 - ZD_filter) * 5
            x = ZD_future_60 - ZD_filter
            delta_ZD = 2 + ((x - 0.1) * (5 - 2)) / (1 - 0.1)
        else:    #1-2
            # delta_ZD = round(ZD_future_60 - ZD_filter) * 10
            x = ZD_future_60 - ZD_filter
            delta_ZD = 0 + ((x - 0) * (2 - 0)) / (0.1 - 0)

    if delta_ZD >= 10:
        delta_ZD = 10


    if PY_filter >= 1.2 and PY_future_60 >= 1.2 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 4
    if PY_filter >= 1.5 and PY_future_60 >= 1.5 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 7
    if PY_filter >= 2.0 and PY_future_60 >= 2.0 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 10

    if delta_PY <= -10:
        delta_PY = -10

    delta_MN = (np.mean(PDC[-12:])*MN_in[-1]) / 10000


    delta_JM = -(JM_filter - 1.5) * 4

    pumpNext = round(pumpNext + delta_MN + delta_ZD + delta_PDC + delta_JM)
    print("---煤泥入料修正量：%.2f---浊度趋势修正量：%.2f---耙压趋势修正量：%.2f---界面仪修正量：%.2f---" % (delta_MN, delta_ZD, delta_PY, delta_JM))

    #停泵
    if JM_filter >= 1.5 and PY_filter >= 1.5 and ZD_filter <= ZD_SD and ZD_future_5 <= ZD_SD and ZD_future_60 <= ZD_SD:
        print("---停泵---界面仪正常，浊度正常，耙压正常，未来不会超过浊度高值---")
        pumpNext = 0

    print("---加药控制器修正结果：%d---" % pumpNext)

    if pumpNext < lower_limit:
        pumpNext = 0
    if pumpNext >= 50:
        pumpNext = 50
        bkpumpNext = pumpNext - 50
        bkpumpNext = bkpumpNext + 20
        if bkpumpNext >= 50:
            bkpumpNext = 50

    print("-----------------------------------------------------------------------------")

    return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

def jiayaoCtrl5202(ZD, PY, JM, PDC, pump, MN_in, ZD_SD, PY_max, update_ctrl, para1 ,para2, para3, JM_measured):

    global jiayao_controller_5202
    state_name = "正常"  # 状态，0正常，1停车，2压耙，3浊度过高
    state = 0
    pumpNext = 0
    Gain = 100
    valve_MN = MN_in[-1]
    base = 20
    JM_errorRange = 0.5
    bkpumpNext = 0

    sigma = 5
    sigma2 = 5
    ZD_filter = gaussian_filter1d(ZD, sigma)[-1]
    PY_filter = gaussian_filter1d(PY, sigma2)[-1]
    JM_filter = gaussian_filter1d(JM, sigma)[-1]
    ZD_filter_array = gaussian_filter1d(ZD, sigma)
    PY_filter_array = gaussian_filter1d(PY, sigma2)
    JM_filter_array = gaussian_filter1d(JM, sigma2)

    print("---浊度计当前测量值为：%.2f---滤波值为：%.2f---" % (ZD[-1], ZD_filter))
    print("---耙压当前测量值为：%.2f---滤波值为：%.2f---耙压最大值为：%.2f---" % (PY[-1], PY_filter, PY_max))
    print("---界面仪当前测量值为：%.2f---滤波值：%.4f---2小时测量值为：%.3f---" % (JM[-1], JM_filter, JM_measured))


    fitIntervel = -5 * minutePerIndex
    ZD_trend_5 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -10 * minutePerIndex
    ZD_trend_10 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -30 * minutePerIndex
    ZD_trend_30 = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)[0]

    fitIntervel = -5 * minutePerIndex
    coeff_linear = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(10 * minutePerIndex))

    ZD_future_1 = y_fit_linear[-5 * minutePerIndex]
    ZD_future_5 = y_fit_linear[-1]

    fitIntervel = -30 * minutePerIndex
    coeff_linear = np.polyfit(range(len(ZD_filter_array[fitIntervel:])), ZD_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(90 * minutePerIndex))

    ZD_future_30 = y_fit_linear[-30 * minutePerIndex]
    ZD_future_60 = y_fit_linear[-1]
    print("---5min浊度变化率：%.4f---10min浊度变化率：%.4f---30min浊度变化率：%.4f---" % (
    ZD_trend_5, ZD_trend_10, ZD_trend_30))
    print(
        "---未来1min浊度趋势预测：%.2f---未来5min浊度趋势预测：%.2f---未来30min浊度趋势预测：%.2f---未来60min浊度趋势预测: %.2f---" % (
        ZD_future_1, ZD_future_5, y_fit_linear[-30 * minutePerIndex], y_fit_linear[-1]))


    fitIntervel = -5 * minutePerIndex
    PY_trend_5 = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)[0]
    fitIntervel = -30 * minutePerIndex
    PY_trend_30 = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)[0]


    fitIntervel = -5 * minutePerIndex
    coeff_linear = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(10 * minutePerIndex))

    PY_future_1 = y_fit_linear[-5 * minutePerIndex]
    PY_future_5 = y_fit_linear[-1]


    fitIntervel = -30 * minutePerIndex
    coeff_linear = np.polyfit(range(len(PY_filter_array[fitIntervel:])), PY_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(90 * minutePerIndex))

    PY_future_30 = y_fit_linear[-30 * minutePerIndex]
    PY_future_60 = y_fit_linear[-1]

    print("---5min耙压变化率：%.4f---30min耙压变化率：%.4f---" % (PY_trend_5, PY_trend_30))
    print(
        "---未来1min耙压趋势预测：%.2f---未来5min耙压趋势预测：%.2f---未来30min耙压趋势预测：%.2f---未来60min耙压趋势预测: %.2f---" % (
        PY_future_1, PY_future_5, y_fit_linear[-30 * minutePerIndex], y_fit_linear[-1]))

    if np.mean(ZD[-5 * minutePerIndex:]) < ZD_SD:
        update_ctrl = True

    if update_ctrl:
        print("---加药泵控制器初始化---")
        jiayao_controller_5202 = Controller(1, para1, para2, para3, -50, 50)


    # ----------------------------异常情况-------------------
    if np.mean(PDC[-5 * minutePerIndex:]) <= 100:
        state = 1
        state_name = "无煤"
        print("---无煤---")
        pumpNext = 0
        return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

    if PY_filter >= PY_max:
        state = 2
        state_name = "压耙"
        print("---压耙---")
        pumpNext = 0
        return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name

    if PY_trend_5 >= 0.05:
        state = 3
        state_name = "耙压变化异常"


    # -----------------------------------耙压正常情况------------------------------------------
    # if ZD_filter >= ZD_SD:
    ZD_filter_calc = ZD_filter
    # if ZD_filter >= 20 + ZD_SD:
    #     ZD_filter_calc = 20 + ZD_SD

    pumpNext_ctrl = jiayao_controller_5202.update_Jiayao_AntiWindup(ZD_SD, ZD_filter_calc, para1, para2, para3)
    pumpNext_ctrl = base + ((50 - base) / (50 - 0)) * (pumpNext_ctrl - 0)
    # if pumpNext_ctrl >= 50:
    #     pumpNext_ctrl = 50
    if pumpNext_ctrl <= lower_limit:
        pumpNext_ctrl = lower_limit


    pumpNext = pumpNext_ctrl

    print("---加药泵反馈：%.2f---" % pump[-1])
    print("---加药控制器计算结果：%d---" % pumpNext)


    delta_ZD = 0
    delta_MN = 0
    delta_PY = 0
    delta_PDC = 0
    delta_JM = 0

    delta_MN = MN_in[-1] / 30


    if ZD_trend_10 >= 0 and ZD_future_60 >= ZD_SD and ZD_future_60 > ZD_filter:
        if ZD_future_60 - ZD_filter >= 10:  #10-15   #8-10
            x = ZD_future_60 - ZD_filter
            delta_ZD = 8 + ((x - 10) * (10 - 8)) / (50 - 10)
        if ZD_future_60 - ZD_filter >= 1 and ZD_future_60 - ZD_filter < 10:  # 6-10  #5-8
            # delta_ZD = round(ZD_future_60 - ZD_filter) / 2
            x = ZD_future_60 - ZD_filter
            delta_ZD = 5 + ((x - 1) * (8 - 5)) / (10 - 1)
        elif ZD_future_60 - ZD_filter < 1 and ZD_future_60 - ZD_filter >= 0.1:  # 2-5  #2-5
            # delta_ZD = round(ZD_future_60 - ZD_filter) * 5
            x = ZD_future_60 - ZD_filter
            delta_ZD = 2 + ((x - 0.1) * (5 - 2)) / (1 - 0.1)
        else:    #1-2
            # delta_ZD = round(ZD_future_60 - ZD_filter) * 10
            x = ZD_future_60 - ZD_filter
            delta_ZD = 0 + ((x - 0) * (2 - 0)) / (0.1 - 0)

    if delta_ZD >= 10:
        delta_ZD = 10


    if PY_filter >= 1.2 and PY_future_60 >= 1.2 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 4
    if PY_filter >= 1.5 and PY_future_60 >= 1.5 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 7
    if PY_filter >= 2.0 and PY_future_60 >= 2.0 and PY_future_60 >= np.mean(PY_filter_array[-12:]):
        delta_PY = -(PY_future_60 - PY_filter) * 10 * 10

    if delta_PY <= -10:
        delta_PY = -10

    delta_MN = (np.mean(PDC[-12:])*MN_in[-1]) / 10000


    delta_JM = -(JM_filter - 1.5) * 4

    pumpNext = round(pumpNext + delta_MN + delta_ZD + delta_PDC + delta_JM)
    print("---煤泥入料修正量：%.2f---浊度趋势修正量：%.2f---耙压趋势修正量：%.2f---界面仪修正量：%.2f---" % (delta_MN, delta_ZD, delta_PY, delta_JM))

    #停泵
    if JM_filter >= 1.5 and PY_filter >= 1.5 and ZD_filter <= ZD_SD and ZD_future_5 <= ZD_SD and ZD_future_60 <= ZD_SD:
        print("---停泵---界面仪正常，浊度正常，耙压正常，未来不会超过浊度高值---")
        pumpNext = 0

    print("---加药控制器修正结果：%d---" % pumpNext)

    if pumpNext < lower_limit:
        pumpNext = 0
    if pumpNext >= 50:
        pumpNext = 50
        bkpumpNext = pumpNext - 50
        bkpumpNext = bkpumpNext + 20
        if bkpumpNext >= 50:
            bkpumpNext = 50

    print("-----------------------------------------------------------------------------")

    return int(pumpNext), int(valve_MN), int(bkpumpNext), int(state), state_name