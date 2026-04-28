## 2
## version 2.0   updated in 20250918

import numpy as np
from model.jiayao_controller import jiayaoCtrl601, jiayaoCtrl602, jiayaoCtrl5201, jiayaoCtrl5202
import pymysql



def jiayao601(data_long, data_short, para):

    # 接受数据
    ZD = np.array(data_long[0])   #浊度
    PY = np.array(data_long[1])   #耙压
    JM = np.array(data_long[2])   #界面仪
    PDC = np.array(data_long[3])   #皮带秤瞬时量
    pump = np.array(data_short[0])   #加药泵频率
    MN_in = np.array(data_short[1])   #煤泥入料


    # 接受参数
    ZD_SD = para["ZD_SD"]
    PY_max = 3.5
    para1 = para["para1"]
    para2 = para["para2"]
    para3 = para["para3"]
    update_ctrl = para["update_ctrl"]
    numPump = para["pumpNumber"]
    JM_measured = para["JM_measured"]

    valuePump, valveMN, pred_bkpump, state, state_name = jiayaoCtrl601(ZD, PY, JM, PDC, pump, MN_in, ZD_SD, PY_max, update_ctrl, para1, para2, para3, JM_measured)

    return int(valuePump), int(numPump), int(pred_bkpump), int(valveMN), state, state_name

def jiayao602(data_long, data_short, para):
    # 接受数据
    ZD = np.array(data_long[0])  # 浊度
    PY = np.array(data_long[1])  # 耙压
    JM = np.array(data_long[2])  # 界面仪
    PDC = np.array(data_long[3])  # 皮带秤瞬时量
    pump = np.array(data_short[0])  # 加药泵频率
    MN_in = np.array(data_short[1])  # 煤泥入料

    # 接受参数
    ZD_SD = para["ZD_SD"]
    PY_max = 3.5
    para1 = para["para1"]
    para2 = para["para2"]
    para3 = para["para3"]
    update_ctrl = para["update_ctrl"]
    numPump = para["pumpNumber"]
    JM_measured = para["JM_measured"]

    valuePump, valveMN, pred_bkpump, state, state_name = jiayaoCtrl602(ZD, PY, JM, PDC, pump, MN_in, ZD_SD, PY_max, update_ctrl,
                                                          para1, para2, para3, JM_measured)

    return int(valuePump), int(numPump), int(pred_bkpump), int(valveMN), state, state_name

def jiayao5201(data_long, data_short, para):
    # 接受数据
    ZD = np.array(data_long[0])  # 浊度
    PY = np.array(data_long[1])  # 耙压
    JM = np.array(data_long[2])  # 界面仪
    PDC = np.array(data_long[3])  # 皮带秤瞬时量
    pump = np.array(data_short[0])  # 加药泵频率
    MN_in = np.array(data_short[1])  # 煤泥入料

    # 接受参数
    ZD_SD = para["ZD_SD"]
    PY_max = 3.5
    para1 = para["para1"]
    para2 = para["para2"]
    para3 = para["para3"]
    update_ctrl = para["update_ctrl"]
    numPump = para["pumpNumber"]
    JM_measured = para["JM_measured"]

    valuePump, valveMN, pred_bkpump, state, state_name = jiayaoCtrl5201(ZD, PY, JM, PDC, pump, MN_in, ZD_SD, PY_max, update_ctrl,
                                                          para1, para2, para3, JM_measured)

    return int(valuePump), int(numPump), int(pred_bkpump), int(valveMN), state, state_name

def jiayao5202(data_long, data_short, para):
    # 接受数据
    ZD = np.array(data_long[0])  # 浊度
    PY = np.array(data_long[1])  # 耙压
    JM = np.array(data_long[2])  # 界面仪
    PDC = np.array(data_long[3])  # 皮带秤瞬时量
    pump = np.array(data_short[0])  # 加药泵频率
    MN_in = np.array(data_short[1])  # 煤泥入料

    # 接受参数
    ZD_SD = para["ZD_SD"]
    PY_max = 3.5
    para1 = para["para1"]
    para2 = para["para2"]
    para3 = para["para3"]
    update_ctrl = para["update_ctrl"]
    numPump = para["pumpNumber"]
    JM_measured = para["JM_measured"]

    valuePump, valveMN, pred_bkpump, state, state_name = jiayaoCtrl5202(ZD, PY, JM, PDC, pump, MN_in, ZD_SD, PY_max, update_ctrl,
                                                          para1, para2, para3, JM_measured)

    return int(valuePump), int(numPump), int(pred_bkpump), int(valveMN), state, state_name