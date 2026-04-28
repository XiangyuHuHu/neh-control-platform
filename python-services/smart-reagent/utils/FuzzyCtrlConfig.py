## 模糊控制配置函数
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def create_fuzzy_variables(config):
    """
    创建模糊变量：名字、论域、隶属度分级等
    :param config:
    :return:
    """
    densityErr_config = config.get("densityErr", {})
    liquidLevel_config = config.get("liquidLevel", {})
    densityErrChangeRate_config = config.get("densityErrChangeRate", {})
    diverterValve_config = config.get("diverterValve", {})
    waterValve_config = config.get("waterValve", {})

    densityErr = create_antecedent_variable(
        densityErr_config.get("name", "densityErr"),
        densityErr_config.get("universe_l", -1),
        densityErr_config.get("universe_r", 1),
        densityErr_config.get("num_intervals", 5),
        densityErr_config.get("is_trapmf", False)
    )

    liquidLevel = create_antecedent_variable(
        liquidLevel_config.get("name", "liquidLevel"),
        liquidLevel_config.get("universe_l", 0),
        liquidLevel_config.get("universe_r", 1),
        liquidLevel_config.get("num_intervals", 3),
        liquidLevel_config.get("is_trapmf", False)
    )

    densityErrChangeRate = create_antecedent_variable(
        densityErrChangeRate_config.get("name", "densityErrChangeRate"),
        densityErrChangeRate_config.get("universe_l", -1),
        densityErrChangeRate_config.get("universe_r", 1),
        densityErrChangeRate_config.get("num_intervals", 5),
        densityErrChangeRate_config.get("is_trapmf", False)
    )

    diverterValve = create_consequent_variable(
        diverterValve_config.get("name", "diverterValve"),
        diverterValve_config.get("universe_l", 0),
        diverterValve_config.get("universe_r", 1),
        diverterValve_config.get("num_intervals", 5)
    )

    waterValve = create_consequent_variable(
        waterValve_config.get("name", "waterValve"),
        waterValve_config.get("universe_l", 0),
        waterValve_config.get("universe_r", 1),
        waterValve_config.get("num_intervals", 5)
    )

    return densityErr, liquidLevel, densityErrChangeRate, diverterValve, waterValve


def create_antecedent_variable(name, universe_l, universe_r, num_intervals, is_trapmf=False):
    """
    创建模糊前件变量，并自动生成隶属度函数

    参数:
    name (str): 变量名称
    universe_l (float): 论域的左边界
    universe_r (float): 论域的右边界
    num_intervals (int): 划分的区间数量（用于确定隶属度函数个数）
    is_trapmf (bool): 是否使用梯形隶属度函数（默认False使用三角形隶属度函数）

    返回:
    ctrl.Antecedent: 创建好的模糊前件变量对象
    """
    universe = np.arange(universe_l, universe_r, (universe_r - universe_l) / 1000)  # 精细划分论域
    var = ctrl.Antecedent(universe, name)
    interval_width = (universe_r - universe_l) / num_intervals
    for i in range(num_intervals):
        if is_trapmf:
            left = universe_l + i * interval_width
            right = universe_l + (i + 1) * interval_width
            if i == 0:
                left_l = left
                left_r = left
            else:
                left_l = universe_l + (i - 1) * interval_width
            if i == num_intervals - 1:
                right_l = right
                right_r = right
            else:
                right_r = universe_l + (i + 2) * interval_width
            label = get_label(i, num_intervals)
            var[label] = fuzz.trapmf(var.universe, [left_l, left, right, right_r])
        else:
            center = universe_l + (i + 0.5) * interval_width
            left = center - interval_width / 2
            right = center + interval_width / 2
            label = get_label(i, num_intervals)
            var[label] = fuzz.trimf(var.universe, [left, center, right])
    return var


def create_consequent_variable(name, universe_l, universe_r, num_intervals):
    """
    创建模糊后件变量，并自动生成隶属度函数

    参数:
    name (str): 变量名称
    universe_l (float): 论域的左边界
    universe_r (float): 论域的右边界
    num_intervals (int): 划分的区间数量（用于确定隶属度函数个数）

    返回:
    ctrl.Consequent: 创建好的模糊后件变量对象
    """
    universe = np.arange(universe_l, universe_r, (universe_r - universe_l) / 1000)  # 精细划分论域
    var = ctrl.Consequent(universe, name)
    interval_width = (universe_r - universe_l) / num_intervals
    for i in range(num_intervals):
        center = universe_l + (i + 0.5) * interval_width
        left = center - interval_width / 2
        right = center + interval_width / 2
        label = get_label(i, num_intervals)
        var[label] = fuzz.trimf(var.universe, [left, center, right])
    return var


def get_label(index, num_intervals):
    """
    根据索引和区间数量生成隶属度函数的标签

    参数:
    index (int): 当前区间的索引
    num_intervals (int): 总的区间数量

    返回:
    str: 隶属度函数的标签，如'NB'、'NM'等
    """
    labels = ['NB', 'NM', 'NS', 'ZO', 'PS', 'PM', 'PB']
    if num_intervals == 3:
        labels = ['NB', 'ZO', 'PB']
    elif num_intervals == 5:
        labels = ['NB', 'NS', 'ZO', 'PS', 'PB']
    return labels[index]