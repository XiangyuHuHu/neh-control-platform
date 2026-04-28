## 2

import os

import numpy as np
import pymysql

from model.mikong_controller import densityCtrl316, densityCtrl3207, densityCtrl3208, predict_rhoSD


def _to_float(value):
    arr = np.asarray(value).reshape(-1)
    if arr.size == 0:
        raise ValueError("empty value")
    return float(arr[-1])


def _load_mysql_density(field_name):
    connection = None
    try:
        connection = pymysql.connect(
            host=os.getenv("SMART_DENSITY_DB_HOST", "192.168.100.170"),
            user=os.getenv("SMART_DENSITY_DB_USER", "user"),
            password=os.getenv("SMART_DENSITY_DB_PASSWORD", "666666"),
            port=int(os.getenv("SMART_DENSITY_DB_PORT", "3306")),
            database=os.getenv("SMART_DENSITY_DB_NAME", "ai_data"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=int(os.getenv("SMART_DENSITY_DB_TIMEOUT_SEC", "3")),
            read_timeout=int(os.getenv("SMART_DENSITY_DB_TIMEOUT_SEC", "3")),
            write_timeout=int(os.getenv("SMART_DENSITY_DB_TIMEOUT_SEC", "3")),
        )
        with connection.cursor() as cursor:
            sql = f"SELECT `{field_name}` FROM `{os.getenv('SMART_DENSITY_DB_TABLE', 'opcdata')}` ORDER BY `TIME` DESC LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()
            if not result or result.get(field_name) is None:
                return None
            return float(result[field_name])
    except Exception:
        return None
    finally:
        if connection:
            connection.close()


def _resolve_rho_sd(unit, field_name, para, fallback_signal):
    source = os.getenv("SMART_DENSITY_RHO_SOURCE", "param").strip().lower()

    if source == "mysql":
        value = _load_mysql_density(field_name)
        if value is not None:
            return value

    if "rho_SD" in para:
        return _to_float(para["rho_SD"])

    if "density_setpoint" in para:
        return _to_float(para["density_setpoint"])

    default_value = os.getenv(f"SMART_DENSITY_DEFAULT_{unit}")
    if default_value not in (None, ""):
        return float(default_value)

    return _to_float(fallback_signal)


def predict_RhoSD(data):
    HF201 = np.array(data[0])
    HF501 = np.array(data[1])
    HF502 = np.array(data[2])

    pred_rho_SD_MM, pred_rho_SD_KM = predict_rhoSD(HF201, HF501, HF502)

    return pred_rho_SD_MM, pred_rho_SD_KM


def mikong3207(data_long, data_short, para):
    rho = np.array(data_long[0])
    yw = np.array(data_long[1])
    diverter = np.array(data_long[2])
    PDC = np.array(data_long[3])
    QT = np.array(data_long[4])
    water = np.array(data_short[0])
    JJB = np.array(data_short[1])
    yw_XJ = np.array(data_short[2])

    rho_SD = _resolve_rho_sd("3207", "3207rhoSD_oldSys", para, rho)
    yw_space = para["yw_space"]
    yw_min = para["yw_min"]
    yw_max = para["yw_max"]
    diverterCtrlPara1 = para["kp_md_FL"]
    diverterCtrlPara2 = para["ki_md_FL"]
    diverterCtrlPara3 = para["kd_md_FL"]
    waterCtrlPara1 = para["kp_md_BS"]
    waterCtrlPara2 = para["ki_md_BS"]
    waterCtrlPara3 = para["kd_md_BS"]
    update_ctrl = para["update_ctrl"]
    diverter_offset = para["diverter_offset"]
    water_offset = para["water_offset"]
    water_switch = para["water_switch"]

    if water_switch == 1:
        water = np.array(data_short[3])

    valueD, valueW, pred_rho, state, state_name = densityCtrl3207(
        rho,
        yw,
        diverter,
        water,
        yw_XJ,
        PDC,
        QT,
        JJB,
        rho_SD,
        yw_space,
        yw_min,
        yw_max,
        update_ctrl,
        diverterCtrlPara1,
        diverterCtrlPara2,
        diverterCtrlPara3,
        waterCtrlPara1,
        waterCtrlPara2,
        waterCtrlPara3,
        diverter_offset,
        water_offset,
    )

    return int(valueD), int(valueW), pred_rho, int(state), state_name


def mikong3208(data_long, data_short, para):
    rho = np.array(data_long[0])
    yw = np.array(data_long[1])
    diverter = np.array(data_long[2])
    PDC = np.array(data_long[3])
    QT = np.array(data_long[4])
    water = np.array(data_short[0])
    JJB = np.array(data_short[1])
    yw_XJ = np.array(data_short[2])

    rho_SD = _resolve_rho_sd("3208", "3208rhoSD_oldSys", para, rho)
    yw_space = para["yw_space"]
    yw_min = para["yw_min"]
    yw_max = para["yw_max"]
    diverterCtrlPara1 = para["kp_md_FL"]
    diverterCtrlPara2 = para["ki_md_FL"]
    diverterCtrlPara3 = para["kd_md_FL"]
    waterCtrlPara1 = para["kp_md_BS"]
    waterCtrlPara2 = para["ki_md_BS"]
    waterCtrlPara3 = para["kd_md_BS"]
    update_ctrl = para["update_ctrl"]
    diverter_offset = para["diverter_offset"]
    water_offset = para["water_offset"]
    water_switch = para["water_switch"]

    if water_switch == 1:
        water = np.array(data_short[3])

    valueD, valueW, pred_rho, state, state_name = densityCtrl3208(
        rho,
        yw,
        diverter,
        water,
        yw_XJ,
        PDC,
        QT,
        JJB,
        rho_SD,
        yw_space,
        yw_min,
        yw_max,
        update_ctrl,
        diverterCtrlPara1,
        diverterCtrlPara2,
        diverterCtrlPara3,
        waterCtrlPara1,
        waterCtrlPara2,
        waterCtrlPara3,
        diverter_offset,
        water_offset,
    )

    return int(valueD), int(valueW), pred_rho, int(state), state_name


def mikong316(data_long, data_short, para):
    rho = np.array(data_long[0])
    yw = np.array(data_long[1])
    diverter = np.array(data_long[2])
    PDC = np.array(data_long[3])
    QT = np.array(data_long[4])
    water = np.array(data_short[0])
    JJB = np.array(data_short[1])

    rho_SD = _resolve_rho_sd("316", "KMrhoSD_oldSys", para, rho)
    yw_space = para["yw_space"]
    yw_min = para["yw_min"]
    yw_max = para["yw_max"]
    diverterCtrlPara1 = para["kp_md_FL"]
    diverterCtrlPara2 = para["ki_md_FL"]
    diverterCtrlPara3 = para["kd_md_FL"]
    waterCtrlPara1 = para["kp_md_BS"]
    waterCtrlPara2 = para["ki_md_BS"]
    waterCtrlPara3 = para["kd_md_BS"]
    update_ctrl = para["update_ctrl"]
    diverter_offset = para["diverter_offset"]
    water_offset = para["water_offset"]
    water_switch = para["water_switch"]

    if water_switch == 1:
        water = np.array(data_short[2])

    valueD, valueW, pred_rho, state, state_name = densityCtrl316(
        rho,
        yw,
        diverter,
        water,
        PDC,
        QT,
        JJB,
        rho_SD,
        yw_space,
        yw_min,
        yw_max,
        update_ctrl,
        diverterCtrlPara1,
        diverterCtrlPara2,
        diverterCtrlPara3,
        waterCtrlPara1,
        waterCtrlPara2,
        waterCtrlPara3,
        diverter_offset,
        water_offset,
    )

    return int(valueD), int(valueW), pred_rho, int(state), state_name
