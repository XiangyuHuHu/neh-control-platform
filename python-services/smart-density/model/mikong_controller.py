

#状态 2-煤量低，3-液位异常，4-缺介，5-稀介桶高，6-异常，7-液位危险，23-煤量低且液位异常，45-缺介且稀介桶高

import numpy as np
import pandas as pd
import keras
from utils.dataPreprocess import slidingAverage
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from PyEMD import EMD
from utils.algorithm import *
from utils.algorithm import rho_diverter_controller_3207, rho_water_controller_3207
from utils.algorithm import rho_diverter_controller_3208, rho_water_controller_3208
from utils.algorithm import rho_diverter_controller_316, rho_water_controller_316
from utils.dataPreprocess import all_values_are_same
from scipy.ndimage import gaussian_filter1d
from utils.dataPreprocess import *
from utils.FuzzyCtrlConfig import *


rho_SDQueue_3207 = ListQueue(2)
rho_SDQueue_3208 = ListQueue(2)
rho_SDQueue_316 = ListQueue(2)
data_Freq = 5
minutePerIndex = int(60/data_Freq)

#----------------------------------------------------------------------------------------------------------------------
def predict_rhoSD(HF201, HF501, HF502):

    HF201_MEAN = np.mean(HF201)
    HF501_MEAN = np.mean(HF501)
    HF502_MEAN = np.mean(HF502)

    rho_SD_pred_MM = 0.0007 * HF201_MEAN - 0.0891 * HF502_MEAN + 2.045
    rho_SD_pred_KM = 0.0003 * HF201_MEAN - 0.0008 * HF501_MEAN + 1.444

    return rho_SD_pred_MM, rho_SD_pred_KM
#----------------------------------------------------------------------------------------------------------------------
def densityCtrl3207(rho, yw, diverter, water, yw_XJ, PDC, QT, JJB, rho_SD, yw_space, yw_min, yw_max, update_ctrl, \
                diverterCtrlPara1, diverterCtrlPara2, diverterCtrlPara3, waterCtrlPara1, waterCtrlPara2, waterCtrlPara3, diverter_offset, water_offset, \
                    water_upperlimit, diverter_upperlimit):

    global rho_water_controller_3207, rho_diverter_controller_3207

    state_name = "正常"  # 状态，0正常，1停工，2液位异常，3提示加介，4液位危险
    state = 0
    diverterNext = 0
    waterNext = 0
    pred_rho = 0
    Gain_BS = 100
    Gain_FL = 100

    steps = 5
    fall_steps = 8
    fall_steps_BS = 20
    predict_steps = 2
    MMPD3203_delta = 100
    ctrl_gain1 = 0.6
    ctrl_gain2 = 0.9
    ctrl_gain3 = 1.2
    ctrl_gain4 = 1.5
    ctrl_gain5 = 2.0
    ywSpace = yw_space

    rhoE_threshold = 0.025
    rhoE_threshold_BS = 0.03
    rho_SD_ori = rho_SD  #
    ctrl_updata = False
    rho_adjust_BS = 0.002
    diverter_limit = diverter_upperlimit
    water_limit = water_upperlimit
    yw_XJ_limit = 95

    rho_trend_1 = np.polyfit(range(len(rho[-1*minutePerIndex:])), rho[-1*minutePerIndex:], 1)[0]
    rho_trend_1 = round(rho_trend_1, 4)
    sigma = 3
    rho_filter = gaussian_filter1d(rho, sigma)[-1]
    yw_filter = gaussian_filter1d(yw, sigma)[-1]
    rho_filter_array = gaussian_filter1d(rho, sigma)
    yw_filter_array = gaussian_filter1d(yw, sigma)

    print("---分流阀当前反馈为：%d---补水阀当前反馈为：%d---" % (diverter[-1], water[-1]))
    print("---当前密度实时值：%.4f---当前液位实时值：%.4f---" % (rho[-1], yw[-1]))
    print("---当前密度滤波值：%.4f---当前液位滤波值：%.4f---" % (rho_filter, yw_filter))


    if rho_SD - rho_filter >= rhoE_threshold and abs(rho_trend_1) <= 0.001:
        rho_SD_ori = rho_SD
        rho_SD = round(np.mean(rho[-3*minutePerIndex:]), 2) + rhoE_threshold
        if rho_SD >= rho_SD_ori:
            rho_SD = rho_SD_ori
        print("---低密度偏差过大，密度设定值调整为 %.4f---" % rho_SD)

    if rho_filter - rho_SD >= rhoE_threshold_BS:
        rho_SD_ori = rho_SD
        rho_SD = round(np.mean(rho[-3*minutePerIndex:]), 2) - rhoE_threshold_BS
        if rho_SD <= rho_SD_ori:
            rho_SD = rho_SD_ori
        print("---高密度偏差过大，密度设定值调整为 %.4f---" % rho_SD)

    print("---过去5min平均密度：%.4f---密度设定：%.4f---" % (np.mean(rho[-5*minutePerIndex:]), rho_SD_ori))

    MMPD3203_std = np.std(PDC[:-10*minutePerIndex+1])
    MMPD3203_mean = np.mean(PDC[:-10*minutePerIndex+1])

    if any(element == False for element in QT[-10*minutePerIndex:]) and np.mean(yw[-2:]) <= 35 and np.mean(PDC[-2:]) >= 100:
        yw_min = 35
        print("---刚启车，液位不足，液位下限调整为 %d---" % (yw_min))
    if np.mean(PDC[-5*minutePerIndex:]) <= 400 and np.mean(yw[-2:]) <= yw_min + ywSpace:
        yw_min = yw_min + ywSpace
        print("---刚启车，液位不足，液位下限调整为 %d---" % (yw_min))

    if update_ctrl:
        ctrl_updata = True
    if np.mean(PDC[-2:]) >= 100 and np.mean(PDC[-3*minutePerIndex:]) <= 100:
        print("---重新开始带煤---")
        ctrl_updata = True

    rho_SD_prev = rho_SDQueue_3207.items[0]
    if abs(rho_SD_prev - rho_SD) >= 0.01:
        ctrl_updata = True
    rho_SDQueue_3207.en_queue(rho_SD)

    if ctrl_updata == True:
        print("---分流---补水---控制初始化---")
        rho_diverter_controller_3207 = Controller(1, diverterCtrlPara1, diverterCtrlPara2, diverterCtrlPara3, 0, 1)
        rho_water_controller_3207 = Controller(1, waterCtrlPara1, waterCtrlPara2, waterCtrlPara3, 0, 1)
        yw_min = yw_min
        yw_max = yw_max
        rho_SD = rho_SD_ori

    if np.mean(rho[-5*minutePerIndex:]) < rho_SD + 0.005:
        print("---补水控制初始化---")
        rho_water_controller_3207 = Controller(1, waterCtrlPara1, waterCtrlPara2, waterCtrlPara3, 0, 1)
    if np.mean(rho[-5*minutePerIndex:]) > rho_SD + 0.005:
        print("---分流控制初始化---")
        rho_diverter_controller_3207 = Controller(1, diverterCtrlPara1, diverterCtrlPara2, diverterCtrlPara3, 0, 1)

    yw_trend = np.polyfit(range(len(yw_filter_array[-1*minutePerIndex:])), yw_filter_array[-1*minutePerIndex:], 1)[0]
    print("---1min密度变化率：%.4f---1min液位变化率：%.3f---" % (rho_trend_1, yw_trend))

    fitIntervel = -2*minutePerIndex
    coeff_linear = np.polyfit(range(len(rho_filter_array[fitIntervel:])), rho_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(len(rho_filter_array[fitIntervel:])))
    coeff_poly = np.polyfit(range(len(rho_filter_array[fitIntervel:])), rho_filter_array[fitIntervel:], 2)
    p_poly = np.poly1d(coeff_poly)
    y_fit_poly = p_poly(range(len(rho_filter_array[fitIntervel:])))

    y_fit_linear = p_linear(range(4*minutePerIndex))
    print("---未来1min密度趋势预测：%.4f---未来2min密度趋势预测: %.4f---" % (
    y_fit_linear[-1*minutePerIndex], y_fit_linear[-1]))
    pred_rho = y_fit_linear[-1]

    coeff_linear = np.polyfit(range(len(yw_filter_array[fitIntervel:])), yw_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(len(yw_filter_array[fitIntervel:])))
    coeff_poly = np.polyfit(range(len(yw_filter_array[fitIntervel:])), yw_filter_array[fitIntervel:], 2)
    p_poly = np.poly1d(coeff_poly)
    y_fit_poly = p_poly(range(len(yw_filter_array[fitIntervel:])))

    y_fit_linear = p_linear(range(4*minutePerIndex))
    print("---未来1min液位趋势预测：%.4f---未来2min液位趋势预测: %.4f---" % (
    y_fit_linear[-1*minutePerIndex], y_fit_linear[-1]))
    yw_future_1 = y_fit_linear[-1*minutePerIndex]
    yw_future_2 = y_fit_linear[-1]

    if QT[-1] == 0:  # 停工
        state_name = "停车"
        state = 1
        diverterNext = 0
        waterNext = 0
        print("---停车---")
        return diverterNext, waterNext, pred_rho, state, state_name

    if np.mean(PDC[-2:]) <= 100:
        if yw_filter >= yw_max or yw_filter <= yw_min:
            state_name = "煤量低且桶位异常"
            state = 23
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5


            if yw_filter <= yw_min and rho_filter >= rho_SD + 0.01:
                waterNext_ctrl = rho_water_controller_3207.update_BS_AntiWindup(rho_SD + 0.01, rho_filter, waterCtrlPara1,
                                                                               waterCtrlPara2, waterCtrlPara3) * Gain_BS
                waterNext = water_offset + ((water_limit - water_offset) / (100 - 0)) * (waterNext_ctrl - 0)
            print("---煤量低且桶位异常---")
            return diverterNext, waterNext, pred_rho, state, state_name
        elif yw_filter >= 40 :
            state_name = "煤量低桶位合适"
        else:
            state_name = "煤量低桶位不合适"
            state = 2
            diverterNext = diverter[-1] - steps
            if diverterNext <= 0:
                diverterNext = 0
            waterNext = water[-1] - fall_steps_BS
            if waterNext <= 0:
                waterNext = 0
            return diverterNext, waterNext, pred_rho, state, state_name

    if np.mean(rho[-5*minutePerIndex:]) - rho_SD_ori >= 0.03 and np.mean(
            yw[-5*minutePerIndex:]) >= yw_max - ywSpace and pred_rho - rho_SD_ori >= 0.02:
        state = 6
        state_name = "煤泥含量高"
        diverterNext = diverter[-1] + 5
        if diverterNext >= 65:
            diverterNext = 65
        waterNext = water[-1] + fall_steps_BS
        if waterNext >= water_limit:
            waterNext = water_limit
        print("---煤泥含量高---")
        if np.mean(yw_XJ[-6:]) >= yw_XJ_limit:
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5
            print("---稀介桶液位高---")
            state_name += "，稀介桶液位高"
        return diverterNext, waterNext, pred_rho, state, state_name


    if yw_filter > yw_max or yw[-1] > yw_max:
        waterNext = int(water[-1]) - fall_steps_BS
        if waterNext <= 0:
            waterNext = 0

        if diverter[-1] <= 40:
            steps = 10
        diverterNext = diverter[-1] + steps
        if diverterNext >= diverter_limit:
            diverterNext = diverter_limit
        state_name = "桶位超上限"
        state = 3

        if yw_filter >= yw_max + 5:
            diverterNext = diverter_limit

        print("---桶位超上限---")
        if np.mean(yw_XJ[-6:]) >= yw_XJ_limit:
            state_name += "，稀介桶液位高"

        return diverterNext, waterNext, pred_rho, state, state_name

    if yw_filter < yw_min or yw[-1] < yw_min:

        if diverter[-1] >= diverter_limit / 2:
            steps = 10
        diverterNext = diverter[-1] - steps

        delta_diverter = 0
        if rho_filter <= rho_SD:
            if rho_trend_1 <= -0.0005:
                delta_diverter = 10
            elif rho_trend_1 >= -0.0005 and rho_trend_1 < -0.0003:
                delta_diverter = 7
            elif rho_trend_1 >= -0.0003 and rho_trend_1 < -0.0002:
                delta_diverter = 3
            else:
                delta_diverter = 0
        if diverterNext <= 15 + delta_diverter:
            diverterNext = 15 + delta_diverter
        if np.mean(PDC) <= 50:
            diverterNext = 0
        state_name = "桶位超下限"
        state = 3

        if yw_min < 8:
            diverterNext = 5
        if yw_min > 8 and yw_filter <= 8:
            diverterNext = 5

        if rho_filter >= rho_SD + 0.002:
            waterNext_ctrl = rho_water_controller_3207.update_BS_AntiWindup(rho_SD + 0.002, rho_filter, waterCtrlPara1,
                                                                           waterCtrlPara2, waterCtrlPara3) * Gain_BS
            waterNext_ctrl = 0 + ((90 - 0) / (100 - 0)) * (waterNext_ctrl - 0)

            if water[-1] < waterNext_ctrl:
                waterNext = int(water[-1]) + fall_steps_BS
                if waterNext >= waterNext_ctrl:
                    waterNext = waterNext_ctrl
            else:
                waterNext = waterNext_ctrl
        print("---桶位超下限---")

        return diverterNext, waterNext, pred_rho, state, state_name

    if abs(rho_SD - rho_filter) >= 0.005:
        dangerSpace = 1
    elif abs(rho_SD - rho_filter) < 0.005 and abs(rho_SD - rho_filter) >= 0.002:
        dangerSpace = 3
    else:
        dangerSpace = 5

    if yw_filter > yw_min and yw_future_1 <= yw_min + dangerSpace:
        if diverter[-1] >= diverter_limit / 2:
            predict_steps = 5
        diverterNext = diverter[-1] - predict_steps

        if rho_SD - rho_filter >= 0.005:
            div_lower_band = 30
        elif rho_SD - rho_filter < 0.005 and rho_SD - rho_filter >= 0.003:
            div_lower_band = 25
        elif rho_SD - rho_filter < 0.003 and rho_SD - rho_filter >= 0:
            div_lower_band = 20
        elif rho_SD - rho_filter < 0 and rho_SD - rho_filter >= -0.003:
            div_lower_band = 10
        else:
            div_lower_band = 5
        if diverterNext <= div_lower_band:
            diverterNext = div_lower_band

        if rho_filter >= rho_SD + rho_adjust_BS and rho_filter < rho_SD + 0.1:
            waterNext = int(water[-1]) + predict_steps
            if waterNext >= 20:
                waterNext = 20
        if rho_filter >= rho_SD + 0.1:
            waterNext = int(water[-1]) + fall_steps_BS
            if waterNext >= 60:
                waterNext = 60

        state_name = "桶位低危险"
        state = 7
        print("---桶位进入低危险区---")

        return diverterNext, waterNext, pred_rho, state, state_name

    if yw_filter < yw_max and yw_future_1 >= yw_max - dangerSpace:
        if diverter[-1] <= diverter_limit / 2:
            predict_steps = 5
        diverterNext = diverter[-1] + predict_steps

        if rho_filter - rho_SD >= 0.015:
            div_upper_band = diverter_limit - 10
        elif rho_filter - rho_SD < 0.015 and rho_filter - rho_SD >= 0.01:
            div_upper_band = diverter_limit - 5
        else:
            div_upper_band = diverter_limit
        if diverterNext >= div_upper_band:
            diverterNext = div_upper_band

        waterNext = int(water[-1]) - fall_steps_BS
        if waterNext <= 0:
            waterNext = 0
        state = 7
        state_name = "桶位高危险"

        print("---桶位进入高危险区---")

        if np.mean(yw_XJ[-6:]) >= yw_XJ_limit:
            state_name += "，稀介桶液位高"
            if rho_filter >= rho_SD + 0.002:
                diverterNext = diverter[-1] - steps
                if diverterNext <= 5:
                    diverterNext = 5
                print("---稀介桶液位高---")

        return diverterNext, waterNext, pred_rho, state, state_name

    baseDiv = diverter_offset
    if abs(rho_SD - rho_filter) > 0.02:
        print("---2.0倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3207.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain5 * diverterCtrlPara1,
                                                                             ctrl_gain5 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3207.update_BS_AntiWindup(rho_SD, rho_filter, 1.5 * ctrl_gain5 * waterCtrlPara1,
                                                                       1.5 * ctrl_gain5 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD > 0.02:
            baseDiv = diverter_offset - 4*5
    if abs(rho_SD - rho_filter) <= 0.02 and abs(rho_SD - rho_filter) > 0.015:
        print("---1.5倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3207.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain4 * diverterCtrlPara1,
                                                                             ctrl_gain4 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3207.update_BS_AntiWindup(rho_SD, rho_filter, 1.5 * ctrl_gain4 * waterCtrlPara1,
                                                                       1.5 * ctrl_gain4 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.02 and rho_filter - rho_SD > 0.015:
            baseDiv = diverter_offset - 3*5
    if abs(rho_SD - rho_filter) <= 0.015 and abs(rho_SD - rho_filter) > 0.01:
        print("---1.2倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3207.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain3 * diverterCtrlPara1,
                                                                             diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3207.update_BS_AntiWindup(rho_SD, rho_filter, 1.5 * ctrl_gain3 * waterCtrlPara1,
                                                                       1.5 * ctrl_gain3 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.015 and rho_filter - rho_SD > 0.01:
            baseDiv = diverter_offset - 2*5
    if abs(rho_SD - rho_filter) <= 0.01 and abs(rho_SD - rho_filter) > 0.005:
        print("---0.9倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3207.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain2 * diverterCtrlPara1,
                                                                             ctrl_gain2 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3207.update_BS_AntiWindup(rho_SD, rho_filter, 1.5 * ctrl_gain2 * waterCtrlPara1,
                                                                       ctrl_gain2 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.001 and rho_filter - rho_SD > 0.005:
            baseDiv = diverter_offset - 1*5
    if abs(rho_SD - rho_filter) <= 0.005:
        print("---0.6倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3207.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain1 * diverterCtrlPara1,
                                                                             ctrl_gain1 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3207.update_BS_AntiWindup(rho_SD, rho_filter, ctrl_gain1 * waterCtrlPara1,
                                                                       ctrl_gain1 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.005:
            baseDiv = diverter_offset


    # diverter_limit = 70

    diverterNext_ctrl = baseDiv + ((diverter_limit - baseDiv) / (100 - 0)) * (diverterNext_ctrl - 0)

    if rho_filter < rho_SD + 0.0025:
        waterNext_ctrl = 0
    else:
        waterNext_ctrl = water_offset + ((water_limit - water_offset) / (100 - 0)) * (waterNext_ctrl - 0)

    print("---分流控制器计算结果：%d---补水控制器计算结果：%d---" % (diverterNext_ctrl, waterNext_ctrl))

    delta_diverter = 0
    if yw_future_2 >= yw_max:
        if abs(round(yw_trend * 10)) >= 2:
            delta_diverter = 2 * abs(round(yw_trend * 10))
        else:
            delta_diverter = 4
        diverterNext_ctrl = diverterNext_ctrl + delta_diverter
    if yw_future_2 >= yw_max - ywSpace and yw_future_2 < yw_max:
        if abs(round(yw_trend * 10)) >= 1:
            delta_diverter = 2 * abs(round(yw_trend * 10))
        else:
            delta_diverter = 2
        delta_diverter = 1 * abs(round(yw_trend * 10))
        diverterNext_ctrl = diverterNext_ctrl + delta_diverter

    delta_diverter = 0
    if yw_future_2 <= yw_min:
        if abs(round(yw_trend * 10)) >= 2:
            delta_diverter = 2 * abs(round(yw_trend * 10))
        else:
            delta_diverter = 4
        diverterNext_ctrl = diverterNext_ctrl - delta_diverter
    if yw_future_2 <= yw_min + ywSpace and yw_future_2 > yw_min:
        if abs(round(yw_trend * 10)) >= 1:
            delta_diverter = 2 * abs(round(yw_trend * 10))
        else:
            delta_diverter = 2
        delta_diverter = 1 * abs(round(yw_trend * 10))
        diverterNext_ctrl = diverterNext_ctrl - delta_diverter

    if yw_filter >= yw_max - 10 and yw_trend >= 0:
        diverterNext_ctrl = diverterNext_ctrl + 3
    if yw_filter < yw_max - 10 and yw_filter >= yw_max - 15 and yw_trend >= 0:
        if abs(round(yw_trend * 10)) >= 2:
            diverterNext_ctrl = diverterNext_ctrl + abs(round(yw_trend * 10))
        else:
            diverterNext_ctrl = diverterNext_ctrl + 2
    if yw_filter < yw_max - 15 and yw_filter >= yw_max - 20 and yw_trend >= 0:
        if abs(round(yw_trend * 10)) >= 1:
            diverterNext_ctrl = diverterNext_ctrl + abs(round(yw_trend * 10))
        else:
            diverterNext_ctrl = diverterNext_ctrl + 1

    if yw_filter <= yw_min + 5 and yw_trend <= 0:
        diverterNext_ctrl = diverterNext_ctrl - 3
    if yw_filter < yw_min - 10 and yw_filter >= yw_min + 5 and yw_trend <= 0:
        if abs(round(yw_trend * 10)) >= 2:
            diverterNext_ctrl = diverterNext_ctrl - abs(round(yw_trend * 10))
        else:
            diverterNext_ctrl = diverterNext_ctrl - 2

    print("---分流控制器修正结果：%d---补水控制器修正结果：%d---" % (diverterNext_ctrl, waterNext_ctrl))

    diverterNext = diverterNext_ctrl
    waterNext = waterNext_ctrl

    if abs(diverter[-1] - diverterNext_ctrl) >= steps:
        if diverter[-1] > diverterNext_ctrl:
            diverterNext = diverter[-1] - fall_steps
            if diverterNext <= diverterNext_ctrl:
                diverterNext = diverterNext_ctrl
        if diverter[-1] < diverterNext_ctrl:
            diverterNext = diverter[-1] + steps
            if diverterNext >= diverterNext_ctrl:
                diverterNext = diverterNext_ctrl

    if abs(int(water[-1]) - waterNext_ctrl) >= steps:
        if int(water[-1]) > waterNext_ctrl:
            waterNext = int(water[-1]) - fall_steps_BS
            if waterNext <= waterNext_ctrl:
                waterNext = waterNext_ctrl
        if water[-1] < waterNext_ctrl:
            waterNext = int(water[-1]) + fall_steps_BS
            if waterNext >= waterNext_ctrl:
                waterNext = waterNext_ctrl

    if np.mean(rho[-5 * minutePerIndex:]) <= rho_SD_ori - 0.01 and np.mean(yw[-5*minutePerIndex:]) <= yw_min + 10:
        state_name = state_name + "，" + "缺介建议补充"
        state = 4

    if abs(rho_SD_ori - np.mean(rho[-2*minutePerIndex:])) <= 0.002:
        waterNext = waterNext - 2
        if waterNext <= 0:
            waterNext = 0

    if np.mean(yw[-2*minutePerIndex:]) < yw_min and np.mean(PDC[-2*minutePerIndex:]) <= 100:
        waterNext = 0


    if np.mean(yw_XJ[-6:]) >= yw_XJ_limit:
        state_name += "，稀介桶液位高"
        state = 5
        if rho_filter >= rho_SD + 0.002:
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5
            print("---稀介桶液位高---")
        else:
            diverterNext = int(diverterNext_ctrl / 2)
            diverterNext = diverter[-1] - steps
            if diverterNext <= int(diverterNext_ctrl / 2):
                diverterNext = int(diverterNext_ctrl / 2)
            print("---稀介桶液位高---")

    return int(diverterNext), int(waterNext), float(pred_rho), int(state), state_name
#----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------
def densityCtrl3208(rho, yw, diverter, water, yw_XJ, PDC, QT, JJB, rho_SD, yw_space, yw_min, yw_max, update_ctrl, \
                diverterCtrlPara1,diverterCtrlPara2,diverterCtrlPara3, waterCtrlPara1,waterCtrlPara2, waterCtrlPara3, diverter_offset, water_offset, \
                    water_upperlimit, diverter_upperlimit):


    global rho_water_controller_3208, rho_diverter_controller_3208

    state_name = "正常"  # 状态，0正常，1停工，2液位异常，3提示加介，4液位危险
    state = 0
    diverterNext = 0
    waterNext = 0
    pred_rho = 0
    Gain_BS = 100
    Gain_FL = 100

    steps = 3
    fall_steps = 5
    fall_steps_BS = 15
    predict_steps = 3
    MMPD3203_delta = 100
    ctrl_gain1 = 0.6
    ctrl_gain2 = 0.9
    ctrl_gain3 = 1.2
    ctrl_gain4 = 1.5
    ctrl_gain5 = 2.0
    ywSpace = yw_space
    dangerSpace = yw_space

    rhoE_threshold = 0.025
    rhoE_threshold_BS = 0.03
    rho_SD_ori = rho_SD
    ctrl_updata = False
    rho_adjust_BS = 0.002
    diverter_limit = diverter_upperlimit
    water_limit = water_upperlimit
    yw_XJ_limit = 95

    sigma = 2
    rho_filter = gaussian_filter1d(rho, sigma)[-1]
    yw_filter = gaussian_filter1d(yw, sigma)[-1]
    rho_filter_array = gaussian_filter1d(rho, sigma)
    yw_filter_array = gaussian_filter1d(yw, sigma)

    rho_trend_1 = np.polyfit(range(len(rho_filter_array[int(-0.5*minutePerIndex):])), rho_filter_array[int(-0.5*minutePerIndex):], 1)[0]
    rho_trend_1 = round(rho_trend_1, 4)

    print("---分流阀当前反馈为：%d---补水阀当前反馈为：%d---" % (diverter[-1], water[-1]))
    print("---当前密度实时值：%.4f---当前液位实时值：%.4f---" % (rho[-1], yw[-1]))
    print("---当前密度滤波值：%.4f---当前液位滤波值：%.4f---" % (rho_filter, yw_filter))

    if rho_SD - rho_filter >= rhoE_threshold and abs(rho_trend_1) <= 0.001:
        rho_SD_ori = rho_SD
        rho_SD = round(np.mean(rho[-3*minutePerIndex:]), 2) + rhoE_threshold
        if rho_SD >= rho_SD_ori:
            rho_SD = rho_SD_ori
        print("---低密度偏差过大，密度设定值调整为 %.4f---" % rho_SD)

    if rho_filter - rho_SD >= rhoE_threshold_BS:
        rho_SD_ori = rho_SD
        rho_SD = round(np.mean(rho[-3*minutePerIndex:]), 2) - rhoE_threshold_BS
        if rho_SD <= rho_SD_ori:
            rho_SD = rho_SD_ori
        print("---高密度偏差过大，密度设定值调整为 %.4f---" % rho_SD)

    print("---过去1min平均密度：%.4f---密度设定：%.4f---" % (np.mean(rho[-1*minutePerIndex:]), rho_SD_ori))

    MMPD3203_std = np.std(PDC[:-10*minutePerIndex+1])
    MMPD3203_mean = np.mean(PDC[:-10*minutePerIndex+1])

    if any(element == False for element in QT[-5*minutePerIndex:]) and np.mean(yw[-2:]) <= 20 and np.mean(PDC[-2:]) >= 100:
        yw_min = 20
        print("---刚启车，液位不足，液位下限调整为 %d---" % (yw_min))
    if np.mean(PDC[-5*minutePerIndex:]) <= 400 and np.mean(yw[-2:]) <= yw_min + ywSpace:
        yw_min = yw_min + ywSpace
        print("---刚启车，液位不足，液位下限调整为 %d---" % (yw_min))

    if update_ctrl:
        ctrl_updata = True
    if np.mean(PDC[-2:]) >= 100 and np.mean(PDC[-3*minutePerIndex:]) <= 100:
        print("---重新开始带煤---")
        ctrl_updata = True

    rho_SD_prev = rho_SDQueue_3208.items[0]
    if abs(rho_SD_prev - rho_SD) >= 0.01:
        ctrl_updata = True
    rho_SDQueue_3208.en_queue(rho_SD)

    if ctrl_updata == True:
        print("---分流---补水---控制初始化---")
        rho_diverter_controller_3208 = Controller(1, diverterCtrlPara1, diverterCtrlPara2, diverterCtrlPara3, 0, 1)
        rho_water_controller_3208 = Controller(1, waterCtrlPara1, waterCtrlPara2, waterCtrlPara3, 0, 1)
        yw_min = yw_min
        yw_max = yw_max
        rho_SD = rho_SD_ori

    if np.mean(rho[-2*minutePerIndex:]) < rho_SD + 0.005:
        print("---补水控制初始化---")
        rho_water_controller_3208 = Controller(1, waterCtrlPara1, waterCtrlPara2, waterCtrlPara3, 0, 1)
    if np.mean(rho[-2*minutePerIndex:]) > rho_SD + 0.005:
        print("---分流控制初始化---")
        rho_diverter_controller_3208 = Controller(1, diverterCtrlPara1, diverterCtrlPara2, diverterCtrlPara3, 0, 1)

    yw_trend = np.polyfit(range(len(yw_filter_array[int(-0.5*minutePerIndex):])), yw_filter_array[int(-0.5*minutePerIndex):], 1)[0]
    print("---1min密度变化率：%.4f---1min液位变化率：%.3f---" % (rho_trend_1, yw_trend))

    # fitIntervel = int(-0.5*minutePerIndex)
    fitIntervel = int(-2 * minutePerIndex)
    coeff_linear = np.polyfit(range(len(rho_filter_array[fitIntervel:])), rho_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(len(rho_filter_array[fitIntervel:])))
    coeff_poly = np.polyfit(range(len(rho_filter_array[fitIntervel:])), rho_filter_array[fitIntervel:], 2)
    p_poly = np.poly1d(coeff_poly)
    y_fit_poly = p_poly(range(len(rho_filter_array[fitIntervel:])))

    # y_fit_linear = p_linear(range(2*minutePerIndex))
    y_fit_linear = p_linear(range(3 * minutePerIndex))
    # print("---未来30s密度趋势预测：%.4f---未来1min密度趋势预测: %.4f---" % (
    # y_fit_linear[int(-1*minutePerIndex)], y_fit_linear[int(-0.5*minutePerIndex)]))
    print("---未来30s密度趋势预测：%.4f---未来1min密度趋势预测: %.4f---" % (
    y_fit_linear[int(-0.5*minutePerIndex)], y_fit_linear[-1]))
    pred_rho = y_fit_linear[-1]

    coeff_linear = np.polyfit(range(len(yw_filter_array[fitIntervel:])), yw_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(len(yw_filter_array[fitIntervel:])))
    coeff_poly = np.polyfit(range(len(yw_filter_array[fitIntervel:])), yw_filter_array[fitIntervel:], 2)
    p_poly = np.poly1d(coeff_poly)
    y_fit_poly = p_poly(range(len(yw_filter_array[fitIntervel:])))

    # y_fit_linear = p_linear(range(2*minutePerIndex))
    y_fit_linear = p_linear(range(4 * minutePerIndex))
    print("---未来30s液位趋势预测：%.4f---未来1min液位趋势预测: %.4f---" % (y_fit_linear[int(-1.5*minutePerIndex)], y_fit_linear[int(-1*minutePerIndex)]))
    yw_future_1 = y_fit_linear[int(-1*minutePerIndex)]
    yw_future_2 = y_fit_linear[-1]


    if QT[-1] == 0:
        state_name = "停车"
        state = 1
        diverterNext = 0
        waterNext = 0
        print("---停车---")
        return diverterNext, waterNext, pred_rho, state, state_name

    if np.mean(PDC[-2:]) <= 100:
        if yw_filter >= yw_max or yw_filter <= yw_min:
            state_name = "煤量低且桶位异常"
            state = 23
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5


            if yw_filter <= yw_min and rho_filter >= rho_SD + 0.01:
                waterNext_ctrl = rho_water_controller_3208.update_BS_AntiWindup(rho_SD + 0.01, rho_filter, waterCtrlPara1,
                                                                               waterCtrlPara2, waterCtrlPara3) * Gain_BS
                waterNext = water_offset + ((water_limit - water_offset) / (100 - 0)) * (waterNext_ctrl - 0)
            print("---煤量低且桶位异常---")
            return diverterNext, waterNext, pred_rho, state, state_name
        elif yw_filter >= 20:
            state_name = "煤量低桶位合适"
        else:
            state_name = "煤量低"
            state = 2
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5
            waterNext = water[-1] - fall_steps_BS
            if waterNext <= 0:
                waterNext = 0
            return diverterNext, waterNext, pred_rho, state, state_name

    if np.mean(rho[-5*minutePerIndex:]) - rho_SD_ori >= 0.03 and np.mean(
            yw[-5*minutePerIndex:]) >= yw_max - ywSpace and pred_rho - rho_SD_ori >= 0.02:
        state = 6
        state_name = "煤泥含量高"
        diverterNext = diverter[-1] + 3
        if diverterNext >= diverter_limit:
            diverterNext = diverter_limit
        waterNext = water[-1] + fall_steps_BS
        if waterNext >= water_limit:
            waterNext = water_limit
        print("---煤泥含量高---")
        if np.mean(yw_XJ[-6:]) >= yw_XJ_limit:
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5
            print("---稀介桶液位高---")
            state_name += "，稀介桶液位高"

        return diverterNext, waterNext, pred_rho, state, state_name

    if yw_filter > yw_max or yw[-1] > yw_max:
        waterNext = 0

        if diverter[-1] <= int(diverter_limit / 2):
            steps = 6
        diverterNext = diverter[-1] + steps
        if diverterNext >= diverter_limit:
            diverterNext = diverter_limit
        state_name = "桶位超上限"
        state = 3

        if yw_filter >= yw_max + 5:
            diverterNext = diverter_limit

        print("---桶位超上限---")

        if np.mean(yw_XJ[-6:]) >= yw_XJ_limit:
            state_name += "，稀介桶液位高"

        return diverterNext, waterNext, pred_rho, state, state_name

    if yw_filter < yw_min or yw[-1] < yw_min:

        if diverter[-1] >= int(diverter_limit / 2):
            steps = 6
        diverterNext = diverter[-1] - steps
        if diverterNext <= 5:
            diverterNext = 5

        if np.mean(PDC) <= 50:
            diverterNext = 0
        state_name = "桶位超下限"
        state = 3

        if yw_min < 8:
            diverterNext = 5
        if yw_min > 8 and yw_filter <= 8:
            diverterNext = 5

        if rho_filter >= rho_SD + 0.002:
            waterNext_ctrl = rho_water_controller_3208.update_BS_AntiWindup(rho_SD + 0.002, rho_filter, waterCtrlPara1,
                                                                           waterCtrlPara2, waterCtrlPara3) * Gain_BS
            waterNext_ctrl = water_offset + ((water_limit - water_offset) / (100 - 0)) * (waterNext_ctrl - 0)

            if water[-1] < waterNext_ctrl:
                waterNext = int(water[-1]) + fall_steps_BS
                if waterNext >= waterNext_ctrl:
                    waterNext = waterNext_ctrl
            else:
                waterNext = waterNext_ctrl
        print("---桶位超下限---")

        return diverterNext, waterNext, pred_rho, state, state_name

    # if abs(rho_SD - rho_filter) >= 0.005:
    #     dangerSpace = 1
    # elif abs(rho_SD - rho_filter) < 0.005 and abs(rho_SD - rho_filter) >= 0.002:
    #     dangerSpace = 3
    # else:
    #     dangerSpace = 5

    if yw_filter > yw_min and yw_future_1 <= yw_min + dangerSpace:
        if diverter[-1] >= 20:
            predict_steps = 4
        diverterNext = diverter[-1] - predict_steps

        if rho_SD - rho_filter >= 0.005:
            div_lower_band = 15
        elif rho_SD - rho_filter < 0.005 and rho_SD - rho_filter >= 0.003:
            div_lower_band = 12
        elif rho_SD - rho_filter < 0.003 and rho_SD - rho_filter >= 0:
            div_lower_band = 10
        elif rho_SD - rho_filter < 0 and rho_SD - rho_filter >= -0.003:
            div_lower_band = 8
        else:
            div_lower_band = 5
        if diverterNext <= div_lower_band:
            diverterNext = div_lower_band

        if rho_filter >= rho_SD + rho_adjust_BS and rho_filter < rho_SD + 0.1:
            waterNext = int(water[-1]) + predict_steps
            if waterNext >= 20:
                waterNext = 20
        if rho_filter >= rho_SD + 0.1:
            waterNext = int(water[-1]) + fall_steps_BS
            if waterNext >= water_limit:
                waterNext = water_limit

        state_name = "桶位低危险"
        state = 7
        print("---桶位进入低危险区---")

        return diverterNext, waterNext, pred_rho, state, state_name

    if yw_filter < yw_max and yw_future_1 >= yw_max - dangerSpace:
        if diverter[-1] <= int(diverter_limit / 2):
            predict_steps = 4
        diverterNext = diverter[-1] + predict_steps

        if rho_filter - rho_SD >= 0.015:
            div_upper_band = diverter_limit - 10
        elif rho_filter - rho_SD < 0.015 and rho_filter - rho_SD >= 0.01:
            div_upper_band = diverter_limit - 5
        else:
            div_upper_band = diverter_limit

        if diverterNext >= div_upper_band:
            diverterNext = div_upper_band

        waterNext = int(water[-1]) - fall_steps_BS
        if waterNext <= 0:
            waterNext = 0
        state = 7
        state_name = "桶位高危险"

        print("---桶位进入高危险区---")

        if np.mean(yw_XJ[-6:]) >= yw_XJ_limit:
            state_name += "，稀介桶液位高"
            if rho_filter >= rho_SD + 0.002:
                diverterNext = diverter[-1] - steps
                if diverterNext <= 5:
                    diverterNext = 5
                print("---稀介桶液位高---")

        return diverterNext, waterNext, pred_rho, state, state_name

    baseDiv = diverter_offset
    if abs(rho_SD - rho_filter) > 0.02:
        print("---2.0倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3208.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain5 * diverterCtrlPara1,
                                                                             ctrl_gain5 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3208.update_BS_AntiWindup(rho_SD, rho_filter,  waterCtrlPara1,
                                                                       ctrl_gain5 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD > 0.02:
            baseDiv = diverter_offset - 4*2
    if abs(rho_SD - rho_filter) <= 0.02 and abs(rho_SD - rho_filter) > 0.015:
        print("---1.5倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3208.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain4 * diverterCtrlPara1,
                                                                             ctrl_gain4 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3208.update_BS_AntiWindup(rho_SD, rho_filter, waterCtrlPara1,
                                                                       ctrl_gain4 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.02 and rho_filter - rho_SD > 0.015:
            baseDiv = diverter_offset - 3*2
    if abs(rho_SD - rho_filter) <= 0.015 and abs(rho_SD - rho_filter) > 0.01:
        print("---1.2倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3208.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain3 * diverterCtrlPara1,
                                                                             diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3208.update_BS_AntiWindup(rho_SD, rho_filter, waterCtrlPara1,
                                                                       ctrl_gain3 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.015 and rho_filter - rho_SD > 0.01:
            baseDiv = diverter_offset - 2*2
    if abs(rho_SD - rho_filter) <= 0.01 and abs(rho_SD - rho_filter) > 0.005:
        print("---0.9倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3208.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain2 * diverterCtrlPara1,
                                                                             ctrl_gain2 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3208.update_BS_AntiWindup(rho_SD, rho_filter, ctrl_gain2 * waterCtrlPara1,
                                                                       ctrl_gain2 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.001 and rho_filter - rho_SD > 0.005:
            baseDiv = diverter_offset - 1*2
    if abs(rho_SD - rho_filter) <= 0.005:
        print("---0.6倍增益---")
        diverterNext_ctrl = rho_diverter_controller_3208.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain1 * diverterCtrlPara1,
                                                                             ctrl_gain1 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_3208.update_BS_AntiWindup(rho_SD, rho_filter, ctrl_gain1 * waterCtrlPara1,
                                                                       ctrl_gain1 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.005:
            baseDiv = diverter_offset

    # if yw_filter < 20 or np.mean(yw_filter_array[-2*minutePerIndex:]) < 20:
    #     diverter_limit = 40
    if np.mean(yw[-2*minutePerIndex:]) < yw_min + ywSpace or yw_filter < yw_min + ywSpace:
        diverter_limit = 30


    diverterNext_ctrl = baseDiv + ((diverter_limit - baseDiv) / (100 - 0)) * (diverterNext_ctrl - 0)

    if rho_filter < rho_SD + 0.0025:
        waterNext_ctrl = 0
    else:

        waterNext_ctrl = water_offset + ((water_limit - water_offset) / (100 - 0)) * (waterNext_ctrl - 0)

    print("---分流控制器计算结果：%d---补水控制器计算结果：%d---" % (diverterNext_ctrl, waterNext_ctrl))

    if yw_filter >= 20 and yw_filter < 30 and yw_trend > 0:
        diverterNext_ctrl = diverterNext_ctrl + round(yw_filter/10)
    if yw_filter >= 30 and yw_filter < 40 and yw_trend > 0:
        diverterNext_ctrl = diverterNext_ctrl + round((yw_filter/10)*1.2)
    if yw_filter >= 40 and yw_filter < 50 and yw_trend > 0:
        diverterNext_ctrl = diverterNext_ctrl + round((yw_filter/10)*1.5)

    # delta_diverter = 0
    # if yw_future_2 >= yw_max:
    #     if abs(round(yw_trend * 10)) > 3 and abs(round(yw_trend * 10)) <= 6:
    #         delta_diverter = abs(round(yw_trend * 10))
    #     else:
    #         delta_diverter = 3
    #     diverterNext_ctrl = diverterNext_ctrl + delta_diverter
    # if yw_future_2 >= yw_max - ywSpace and yw_future_2 < yw_max:
    #     if abs(round(yw_trend * 10)) > 2 and abs(round(yw_trend * 10)) <= 6:
    #         delta_diverter = abs(round(yw_trend * 10))
    #     else:
    #         delta_diverter = 2
    #     diverterNext_ctrl = diverterNext_ctrl + delta_diverter
    #
    # delta_diverter = 0
    # if yw_future_2 <= yw_min:
    #     if abs(round(yw_trend * 10)) > 3 and abs(round(yw_trend * 10)) <= 6:
    #         delta_diverter = abs(round(yw_trend * 10))
    #     else:
    #         delta_diverter = 3
    #     diverterNext_ctrl = diverterNext_ctrl - delta_diverter
    # if yw_future_2 <= yw_min + ywSpace and yw_future_2 > yw_min:
    #     if abs(round(yw_trend * 10)) > 2 and abs(round(yw_trend * 10)) <= 6:
    #         delta_diverter = abs(round(yw_trend * 10))
    #     else:
    #         delta_diverter = 2
    #     diverterNext_ctrl = diverterNext_ctrl - delta_diverter

    if yw_filter >= yw_max - 10 and yw_trend >= 0:
        diverterNext_ctrl = diverterNext_ctrl + 3
    if yw_filter < yw_max - 10 and yw_filter >= yw_max - 15 and yw_trend >= 0:
        if abs(round(yw_trend * 10)) >= 2:
            diverterNext_ctrl = diverterNext_ctrl + 2
        else:
            diverterNext_ctrl = diverterNext_ctrl + 2
    if yw_filter < yw_max - 15 and yw_filter >= yw_max - 20 and yw_trend >= 0:
        if abs(round(yw_trend * 10)) >= 1:
            diverterNext_ctrl = diverterNext_ctrl + 1
        else:
            diverterNext_ctrl = diverterNext_ctrl + 1

    if yw_filter <= yw_min + 5 and yw_trend <= 0:
        diverterNext_ctrl = diverterNext_ctrl - 3
    if yw_filter < yw_min + 10 and yw_filter >= yw_min + 5 and yw_trend <= 0:
        if abs(round(yw_trend * 10)) >= 2:
            diverterNext_ctrl = diverterNext_ctrl - 2
        else:
            diverterNext_ctrl = diverterNext_ctrl - 2

    print("---分流控制器修正结果：%d---补水控制器修正结果：%d---" % (diverterNext_ctrl, waterNext_ctrl))

    diverterNext = diverterNext_ctrl
    waterNext = waterNext_ctrl

    if abs(diverter[-1] - diverterNext_ctrl) >= steps:
        if diverter[-1] > diverterNext_ctrl:
            diverterNext = diverter[-1] - fall_steps
            if diverterNext <= diverterNext_ctrl:
                diverterNext = diverterNext_ctrl
        if diverter[-1] < diverterNext_ctrl:
            diverterNext = diverter[-1] + steps
            if diverterNext >= diverterNext_ctrl:
                diverterNext = diverterNext_ctrl

    if np.mean(rho[-5 * minutePerIndex:]) <= rho_SD_ori - 0.01 and np.mean(yw[-5*minutePerIndex:]) <= yw_min + 10:
        state_name = state_name + "，" + "缺介建议补充"
        state = 4

    if abs(rho_SD_ori - np.mean(rho[-2*minutePerIndex:])) <= 0.002:
        waterNext = waterNext - 2
        if waterNext <= 0:
            waterNext = 0

    if np.mean(yw[-2*minutePerIndex:]) < yw_min and np.mean(PDC[-2*minutePerIndex:]) <= 100:
        waterNext = 0

    if np.mean(yw_XJ[-6:]) >= yw_XJ_limit:
        state_name += "，稀介桶液位高"
        state = 5
        if rho_filter >= rho_SD + 0.002:
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5
            print("---稀介桶液位高---")
        else:
            diverterNext = int(diverterNext_ctrl / 2)
            diverterNext = diverter[-1] - steps
            if diverterNext <= int(diverterNext_ctrl / 2):
                diverterNext = int(diverterNext_ctrl / 2)
            print("---稀介桶液位高---")

    return int(diverterNext), int(waterNext), float(pred_rho), int(state), state_name

#----------------------------------------------------------------------------------------------------------------------
def densityCtrl316(rho, yw, diverter, water, PDC, QT, JJB, rho_SD, yw_space, yw_min, yw_max, update_ctrl, \
                diverterCtrlPara1,diverterCtrlPara2,diverterCtrlPara3, waterCtrlPara1,waterCtrlPara2, waterCtrlPara3, diverter_offset, water_offset, \
                   water_upperlimit, diverter_upperlimit):


    global rho_water_controller_316, rho_diverter_controller_316

    state_name = "正常"  # 状态，0正常，1停工，2液位异常，3提示加介，4液位危险
    state = 0
    diverterNext = 0
    waterNext = 0
    pred_rho = 0
    Gain_BS = 100
    Gain_FL = 100

    steps = 5
    fall_steps = 8
    fall_steps_BS = 14
    predict_steps = 2
    MMPD3203_delta = 100
    ctrl_gain1 = 0.6
    ctrl_gain2 = 1.0
    ctrl_gain3 = 1.2
    ctrl_gain4 = 1.6
    ctrl_gain5 = 2.2
    ywSpace = yw_space

    rhoE_threshold = 0.03
    rhoE_threshold_BS = 0.03
    rho_SD_ori = rho_SD
    ctrl_updata = False
    rho_adjust_BS = 0.005  
    diverter_limit = diverter_upperlimit
    water_limit = water_upperlimit
    yw_XJ_limit = 95

    sigma = 2
    rho_filter = gaussian_filter1d(rho, sigma)[-1]
    yw_filter = gaussian_filter1d(yw, sigma)[-1]
    rho_filter_array = gaussian_filter1d(rho, sigma)
    yw_filter_array = gaussian_filter1d(yw, sigma)

    rho_trend_1 = np.polyfit(range(len(rho_filter_array[-1*minutePerIndex:])), rho_filter_array[-1*minutePerIndex:], 1)[0]
    rho_trend_1 = round(rho_trend_1, 4)

    print("---分流阀当前反馈为：%d---补水阀当前反馈为：%d---" % (diverter[-1], water[-1]))
    print("---当前密度实时值：%.4f---当前液位实时值：%.4f---" % (rho[-1], yw[-1]))
    print("---当前密度滤波值：%.4f---当前液位滤波值：%.4f---" % (rho_filter, yw_filter))

    if rho_SD - rho_filter >= rhoE_threshold and abs(rho_trend_1) <= 0.001:
        rho_SD_ori = rho_SD
        rho_SD = round(np.mean(rho[-3*minutePerIndex:]), 2) + rhoE_threshold
        if rho_SD >= rho_SD_ori:
            rho_SD = rho_SD_ori
        print("---低密度偏差过大，密度设定值调整为 %.4f---" % rho_SD)

    if rho_filter - rho_SD >= rhoE_threshold_BS:
        rho_SD_ori = rho_SD
        rho_SD = round(np.mean(rho[-3*minutePerIndex:]), 2) - rhoE_threshold_BS
        if rho_SD <= rho_SD_ori:
            rho_SD = rho_SD_ori
        print("---高密度偏差过大，密度设定值调整为 %.4f---" % rho_SD)

    print("---过去5min平均密度：%.4f---密度设定：%.4f---" % (np.mean(rho[-5*minutePerIndex:]), rho_SD_ori))

    MMPD3203_std = np.std(PDC[:-10*minutePerIndex+1])
    MMPD3203_mean = np.mean(PDC[:-10*minutePerIndex+1])

    if any(element == False for element in QT[-5*minutePerIndex:]) and np.mean(yw[-2:]) <= 25 and np.mean(PDC[-2:]) >= 100:
        yw_min = 25
        print("---刚启车，液位不足，液位下限调整为 %d---" % (yw_min))
    if np.mean(PDC[-5*minutePerIndex:]) <= 400 and np.mean(yw[-2:]) <= yw_min + ywSpace:
        yw_min = yw_min + ywSpace
        print("---刚启车，液位不足，液位下限调整为 %d---" % (yw_min))

    if update_ctrl:
        ctrl_updata = True
    if np.mean(PDC[-2:]) >= 100 and np.mean(PDC[-3*minutePerIndex:]) <= 100:
        print("---重新开始带煤---")
        ctrl_updata = True

    rho_SD_prev = rho_SDQueue_316.items[0]
    if abs(rho_SD_prev - rho_SD) >= 0.01:
        ctrl_updata = True
    rho_SDQueue_316.en_queue(rho_SD)

    if ctrl_updata == True:
        print("---分流---补水---控制初始化---")
        rho_diverter_controller_316 = Controller(1, diverterCtrlPara1, diverterCtrlPara2, diverterCtrlPara3, 0, 1)
        rho_water_controller_316 = Controller(1, waterCtrlPara1, waterCtrlPara2, waterCtrlPara3, 0, 1)
        yw_min = yw_min
        yw_max = yw_max
        rho_SD = rho_SD_ori

    if np.mean(rho[-5*minutePerIndex:]) < rho_SD + 0.005:
        print("---补水控制初始化---")
        rho_water_controller_316 = Controller(1, waterCtrlPara1, waterCtrlPara2, waterCtrlPara3, 0, 1)
    if np.mean(rho[-5*minutePerIndex:]) > rho_SD + 0.005:
        print("---分流控制初始化---")
        rho_diverter_controller_316 = Controller(1, diverterCtrlPara1, diverterCtrlPara2, diverterCtrlPara3, 0, 1)

    print("---分流阀当前反馈为：%d---补水阀当前反馈为：%d---" % (diverter[-1], water[-1]))
    print("---当前密度滤波值：%.4f---当前液位滤波值：%.4f---" % (rho_filter, yw_filter))


    yw_trend = np.polyfit(range(len(yw[-1*minutePerIndex:])), yw[-1*minutePerIndex:], 1)[0]
    print("---1min密度变化率：%.4f---1min液位变化率：%.3f---" % (rho_trend_1, yw_trend))

    fitIntervel = -1*minutePerIndex
    coeff_linear = np.polyfit(range(len(rho_filter_array[fitIntervel:])), rho_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(len(rho_filter_array[fitIntervel:])))
    coeff_poly = np.polyfit(range(len(rho_filter_array[fitIntervel:])), rho_filter_array[fitIntervel:], 2)
    p_poly = np.poly1d(coeff_poly)
    y_fit_poly = p_poly(range(len(rho_filter_array[fitIntervel:])))

    y_fit_linear = p_linear(range(4*minutePerIndex))
    print("---未来1min密度趋势预测：%.4f---未来2min密度趋势预测: %.4f---" % (
    y_fit_linear[-1*minutePerIndex], y_fit_linear[-1]))
    pred_rho = y_fit_linear[-1]

    coeff_linear = np.polyfit(range(len(yw_filter_array[fitIntervel:])), yw_filter_array[fitIntervel:], 1)
    p_linear = np.poly1d(coeff_linear)
    y_fit_linear = p_linear(range(len(yw_filter_array[fitIntervel:])))
    coeff_poly = np.polyfit(range(len(yw_filter_array[fitIntervel:])), yw_filter_array[fitIntervel:], 2)
    p_poly = np.poly1d(coeff_poly)
    y_fit_poly = p_poly(range(len(yw_filter_array[fitIntervel:])))

    y_fit_linear = p_linear(range(4*minutePerIndex))
    print("---未来1min液位趋势预测：%.4f---未来2min液位趋势预测: %.4f---" % (
    y_fit_linear[-1*minutePerIndex], y_fit_linear[-1]))
    yw_future_1 = y_fit_linear[-1*minutePerIndex]
    yw_future_2 = y_fit_linear[-1]

    if QT[-1] == 0:
        state_name = "停车"
        state = 1
        diverterNext = 0
        waterNext = 0
        print("---停车---")
        return diverterNext, waterNext, pred_rho, state, state_name

    if np.mean(PDC[-2:]) <= 100:
        if yw_filter >= yw_max or yw_filter <= yw_min:
            state_name = "煤量低且桶位异常"
            state = 23
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5

            if yw_filter <= yw_min and rho_filter >= rho_SD + 0.01:
                waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD + 0.01, rho_filter, waterCtrlPara1,
                                                                               waterCtrlPara2, waterCtrlPara3) * Gain_BS
                waterNext = water_offset + ((water_limit - water_offset) / (100 - 0)) * (waterNext_ctrl - 0)
            print("---煤量低且桶位异常---")
            return diverterNext, waterNext, pred_rho, state, state_name
        elif yw_filter >= 40 :
            state_name = "煤量低桶位合适"
        else:
            state_name = "煤量低"
            state = 2
            diverterNext = diverter[-1] - steps
            if diverterNext <= 5:
                diverterNext = 5
            waterNext = water[-1] - fall_steps_BS
            if waterNext <= 0:
                waterNext = 0
            return diverterNext, waterNext, pred_rho, state, state_name


    if np.mean(rho[-5*minutePerIndex:]) - rho_SD_ori >= 0.03 and np.mean(
            yw[-5*minutePerIndex:]) >= yw_max - ywSpace and pred_rho - rho_SD_ori >= 0.02:
        state = 6
        state_name = "煤泥含量高"
        diverterNext = diverter[-1] + 5
        if diverterNext >= diverter_limit:
            diverterNext = diverter_limit
        waterNext = water[-1] + fall_steps_BS
        if waterNext >= water_limit:
            waterNext = water_limit
        print("---煤泥含量高---")

        return diverterNext, waterNext, pred_rho, state, state_name


    if yw_filter > yw_max or yw[-1] > yw_max:

        waterNext = int(water[-1]) - fall_steps_BS
        if waterNext <= 0:
            waterNext = 0

        if diverter[-1] <= diverter_limit/2:
            steps = 10
        diverterNext = diverter[-1] + steps
        if diverterNext >= diverter_limit:
            diverterNext = diverter_limit
        state_name = "桶位超上限"
        state = 3

        if yw_filter >= yw_max + 5:
            diverterNext = diverter_limit

        print("---桶位超上限---")

        return diverterNext, waterNext, pred_rho, state, state_name


    if yw_filter < yw_min or yw[-1] < yw_min:

        if diverter[-1] >= diverter_limit / 2:
            steps = 12
        diverterNext = diverter[-1] - steps

        delta_diverter = 0
        if rho_filter <= rho_SD:
            if rho_trend_1 <= -0.0005:
                delta_diverter = 10
            elif rho_trend_1 >= -0.0005 and rho_trend_1 < -0.0003:
                delta_diverter = 7
            elif rho_trend_1 >= -0.0003 and rho_trend_1 < -0.0002:
                delta_diverter = 3
            else:
                delta_diverter = 0
        if diverterNext <= 5 + delta_diverter:
            diverterNext = 5 + delta_diverter
        if np.mean(PDC) <= 50:
            diverterNext = 5
        state_name = "桶位超下限"
        state = 3

        if yw_min < 8:
            diverterNext = 5
        if yw_min > 8 and yw_filter <= 8:
            diverterNext = 5

        if rho_filter >= rho_SD + 0.002:
            waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter, waterCtrlPara1,
                                                                           waterCtrlPara2, waterCtrlPara3) * Gain_BS
            if abs(rho_SD - rho_filter) > 0.02:
                waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter,
                                                                               1.5 * ctrl_gain5 * waterCtrlPara1,
                                                                               1.5 * ctrl_gain5 * waterCtrlPara2,
                                                                               waterCtrlPara3) * Gain_BS
            if abs(rho_SD - rho_filter) <= 0.02 and abs(rho_SD - rho_filter) > 0.015:
                waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter,
                                                                               1.5 * ctrl_gain4 * waterCtrlPara1,
                                                                               1.5 * ctrl_gain4 * waterCtrlPara2,
                                                                               waterCtrlPara3) * Gain_BS
            if abs(rho_SD - rho_filter) <= 0.015 and abs(rho_SD - rho_filter) > 0.01:

                waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter,
                                                                               1.5 * ctrl_gain3 * waterCtrlPara1,
                                                                               1.5 * ctrl_gain3 * waterCtrlPara2,
                                                                               waterCtrlPara3) * Gain_BS
            if abs(rho_SD - rho_filter) <= 0.01 and abs(rho_SD - rho_filter) > 0.005:

                waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter,
                                                                               1.5 * ctrl_gain2 * waterCtrlPara1,
                                                                               ctrl_gain2 * waterCtrlPara2,
                                                                               waterCtrlPara3) * Gain_BS
            if abs(rho_SD - rho_filter) <= 0.005:
                waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter,
                                                                               ctrl_gain1 * waterCtrlPara1,
                                                                               ctrl_gain1 * waterCtrlPara2,
                                                                               waterCtrlPara3) * Gain_BS
            waterNext_ctrl = water_offset + ((water_limit - water_offset) / (100 - 0)) * (waterNext_ctrl - 0)

            if water[-1] < waterNext_ctrl:
                waterNext = int(water[-1]) + fall_steps_BS
                if waterNext >= waterNext_ctrl:
                    waterNext = waterNext_ctrl
            else:
                waterNext = waterNext_ctrl
        print("---桶位超下限---")

        return diverterNext, waterNext, pred_rho, state, state_name

    if abs(rho_SD - rho_filter) >= 0.005:
        dangerSpace = 1
    elif abs(rho_SD - rho_filter) < 0.005 and abs(rho_SD - rho_filter) >= 0.002:
        dangerSpace = 3
    else:
        dangerSpace = 5

    if yw_filter > yw_min and yw_future_1 <= yw_min + dangerSpace:
        if diverter[-1] >= diverter_limit / 2:
            predict_steps = 5
        diverterNext = diverter[-1] - predict_steps

        if rho_SD - rho_filter >= 0.005:
            div_lower_band = 30
        elif rho_SD - rho_filter < 0.005 and rho_SD - rho_filter >= 0.003:
            div_lower_band = 25
        elif rho_SD - rho_filter < 0.003 and rho_SD - rho_filter >= 0:
            div_lower_band = 20
        elif rho_SD - rho_filter < 0 and rho_SD - rho_filter >= -0.003:
            div_lower_band = 10
        else:
            div_lower_band = 5
        if diverterNext <= div_lower_band:
            diverterNext = div_lower_band

        if rho_filter >= rho_SD + rho_adjust_BS and rho_filter < rho_SD + 0.1:
            waterNext = int(water[-1]) + predict_steps
            if waterNext >= 30:
                waterNext = 30
        if rho_filter >= rho_SD + 0.1:
            waterNext = int(water[-1]) + fall_steps_BS
            if waterNext >= water_limit:
                waterNext = water_limit

        state_name = "桶位低危险"
        state = 7
        print("---桶位进入低危险区---")

        return diverterNext, waterNext, pred_rho, state, state_name

    if yw_filter < yw_max and yw_future_1 >= yw_max - dangerSpace:
        if diverter[-1] <= diverter_limit / 2:
            predict_steps = 5
        diverterNext = diverter[-1] + predict_steps

        if rho_filter - rho_SD >= 0.015:
            div_upper_band = diverter_limit - 10
        elif rho_filter - rho_SD < 0.015 and rho_filter - rho_SD >= 0.01:
            div_upper_band = diverter_limit - 5
        else:
            div_upper_band = diverter_limit
        if diverterNext >= div_upper_band:
            diverterNext = div_upper_band

        waterNext = int(water[-1]) - fall_steps_BS
        if waterNext <= 0:
            waterNext = 0
        state = 7
        state_name = "桶位高危险"

        print("---桶位进入高危险区---")

        return diverterNext, waterNext, pred_rho, state, state_name

    baseDiv = diverter_offset
    if abs(rho_SD - rho_filter) > 0.02:
        print("---2.0倍增益---")
        diverterNext_ctrl = rho_diverter_controller_316.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain5 * diverterCtrlPara1,
                                                                             ctrl_gain5 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter, 1.5*ctrl_gain5 * waterCtrlPara1,
                                                                       1.5*ctrl_gain5 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD > 0.02:
            baseDiv = 5
    if abs(rho_SD - rho_filter) <= 0.02 and abs(rho_SD - rho_filter) > 0.015:
        print("---1.5倍增益---")
        diverterNext_ctrl = rho_diverter_controller_316.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain4 * diverterCtrlPara1,
                                                                             ctrl_gain4 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter, 1.5*ctrl_gain4 * waterCtrlPara1,
                                                                       1.5*ctrl_gain4 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.02 and rho_filter - rho_SD > 0.015:
            baseDiv = 8
    if abs(rho_SD - rho_filter) <= 0.015 and abs(rho_SD - rho_filter) > 0.01:
        print("---1.2倍增益---")
        diverterNext_ctrl = rho_diverter_controller_316.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain3 * diverterCtrlPara1,
                                                                             diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter, 1.5*ctrl_gain3 * waterCtrlPara1,
                                                                      1.5*ctrl_gain3 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.015 and rho_filter - rho_SD > 0.01:
            baseDiv = 10

    if abs(rho_SD - rho_filter) <= 0.01 and abs(rho_SD - rho_filter) > 0.005:
        print("---0.9倍增益---")
        diverterNext_ctrl = rho_diverter_controller_316.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain2 * diverterCtrlPara1,
                                                                             ctrl_gain2 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter, 1.5*ctrl_gain2 * waterCtrlPara1,
                                                                       ctrl_gain2 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.001 and rho_filter - rho_SD > 0.005:
            baseDiv = 12
    if abs(rho_SD - rho_filter) <= 0.005:
        print("---0.6倍增益---")
        diverterNext_ctrl = rho_diverter_controller_316.update_FL_AntiWindup(rho_SD, rho_filter, ctrl_gain1 * diverterCtrlPara1,
                                                                             ctrl_gain1 * diverterCtrlPara2, diverterCtrlPara3) * Gain_FL
        waterNext_ctrl = rho_water_controller_316.update_BS_AntiWindup(rho_SD, rho_filter, ctrl_gain1 * waterCtrlPara1,
                                                                       ctrl_gain1 * waterCtrlPara2, waterCtrlPara3) * Gain_BS
        if rho_filter - rho_SD <= 0.005:
            baseDiv = 15

    diverterNext_ctrl = baseDiv + ((diverter_limit - baseDiv) / (100 - 0)) * (diverterNext_ctrl - 0)

    if rho_filter < rho_SD + 0.002:
        waterNext_ctrl = 0

        if abs(int(water[-1]) - waterNext_ctrl) >= steps:
            if int(water[-1]) > waterNext_ctrl:
                waterNext = int(water[-1]) - fall_steps_BS
                if waterNext <= waterNext_ctrl:
                    waterNext = waterNext_ctrl
                if diverterNext <= waterNext_ctrl:
                    waterNext = waterNext_ctrl
            if water[-1] < waterNext_ctrl:
                waterNext = int(water[-1]) + fall_steps_BS
                if waterNext >= waterNext_ctrl:
                    waterNext = waterNext_ctrl
    else:

        waterNext_ctrl = water_offset + ((water_limit - water_offset) / (100 - 0)) * (waterNext_ctrl - 0)

    print("---分流控制器计算结果：%d---补水控制器计算结果：%d---" % (diverterNext_ctrl, waterNext_ctrl))


    delta_diverter = 0
    if yw_future_2 >= yw_max:
        if abs(round(yw_trend * 10)) >= 2:
            delta_diverter = 2 * abs(round(yw_trend * 10))
        else:
            delta_diverter = 4
        diverterNext_ctrl = diverterNext_ctrl + delta_diverter
    if yw_future_2 >= yw_max - ywSpace and yw_future_2 < yw_max:
        if abs(round(yw_trend * 10)) >= 1:
            delta_diverter = 2 * abs(round(yw_trend * 10))
        else:
            delta_diverter = 2
        delta_diverter = 1 * abs(round(yw_trend * 10))
        diverterNext_ctrl = diverterNext_ctrl + delta_diverter


    delta_diverter = 0
    if yw_future_2 <= yw_min:
        if abs(round(yw_trend * 10)) >= 2:
            delta_diverter = 2 * abs(round(yw_trend * 10))
        else:
            delta_diverter = 4
        diverterNext_ctrl = diverterNext_ctrl - delta_diverter
    if yw_future_2 <= yw_min + ywSpace and yw_future_2 > yw_min:
        if abs(round(yw_trend * 10)) >= 1:
            delta_diverter = 2 * abs(round(yw_trend * 10))
        else:
            delta_diverter = 2
        delta_diverter = 1 * abs(round(yw_trend * 10))
        diverterNext_ctrl = diverterNext_ctrl - delta_diverter

    if yw_filter >= yw_max - 10 and yw_trend >= 0:
        diverterNext_ctrl = diverterNext_ctrl + 3
    if yw_filter < yw_max - 10 and yw_filter >= yw_max - 15 and yw_trend >= 0:
        if abs(round(yw_trend * 10)) >= 2:
            diverterNext_ctrl = diverterNext_ctrl + abs(round(yw_trend * 10))
        else:
            diverterNext_ctrl = diverterNext_ctrl + 2
    if yw_filter < yw_max - 15 and yw_filter >= yw_max - 20 and yw_trend >= 0:
        if abs(round(yw_trend * 10)) >= 1:
            diverterNext_ctrl = diverterNext_ctrl + abs(round(yw_trend * 10))
        else:
            diverterNext_ctrl = diverterNext_ctrl + 1

    if yw_filter <= yw_min + 5 and yw_trend <= 0:
        diverterNext_ctrl = diverterNext_ctrl - 3
    if yw_filter < yw_min - 10 and yw_filter >= yw_min + 5 and yw_trend <= 0:
        if abs(round(yw_trend * 10)) >= 2:
            diverterNext_ctrl = diverterNext_ctrl - abs(round(yw_trend * 10))
        else:
            diverterNext_ctrl = diverterNext_ctrl - 2

    print("---分流控制器修正结果：%d---补水控制器修正结果：%d---" % (diverterNext_ctrl, waterNext_ctrl))

    diverterNext = diverterNext_ctrl
    waterNext = waterNext_ctrl

    if abs(diverter[-1] - diverterNext_ctrl) >= steps:
        if diverter[-1] > diverterNext_ctrl:
            diverterNext = diverter[-1] - fall_steps
            if diverterNext <= diverterNext_ctrl:
                diverterNext = diverterNext_ctrl
        if diverter[-1] < diverterNext_ctrl:
            diverterNext = diverter[-1] + steps
            if diverterNext >= diverterNext_ctrl:
                diverterNext = diverterNext_ctrl

    if abs(int(water[-1]) - waterNext_ctrl) >= steps:
        if int(water[-1]) > waterNext_ctrl:
            waterNext = int(water[-1]) - fall_steps_BS
            if waterNext <= waterNext_ctrl:
                waterNext = waterNext_ctrl
        if water[-1] < waterNext_ctrl:
            waterNext = int(water[-1]) + fall_steps_BS
            if waterNext >= waterNext_ctrl:
                waterNext = waterNext_ctrl

    if np.mean(rho[-5 * minutePerIndex:]) <= rho_SD_ori - 0.01 and np.mean(yw[-5*minutePerIndex:]) <= yw_min + 10:
        state_name = state_name + "，" + "缺介建议补充"
        state = 4

    if abs(rho_SD_ori - np.mean(rho[-2*minutePerIndex:])) <= 0.002:
        waterNext = waterNext - 2
        if waterNext <= 0:
            waterNext = 0

    if np.mean(yw[-2*minutePerIndex:]) < yw_min and np.mean(PDC[-2*minutePerIndex:]) <= 100:
        waterNext = 0

    return int(diverterNext), int(waterNext), float(pred_rho), int(state), state_name

