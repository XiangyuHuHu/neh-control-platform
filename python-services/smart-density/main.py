##   1

import os
import sys

import uvicorn
from pydantic import BaseModel
from typing import Union
import datetime
from cfg import console_cfg
from fastapi import FastAPI, Form, File, UploadFile
from model import mikong3207, mikong3208, mikong316
from model import predict_RhoSD
import requests

app = FastAPI()

# pwm_ctrl = 0   #设置占空比计数器，1分钟内，1-3次计算，4-6次保持不变
counter3207 = 0 #总调用次数计数器
counter3208 = 0
counter316 = 0
counter601 = 0
counter602 = 0
counter5201 = 0
counter5202 = 0

pwm_ctrl_3208 = 0
prev_pred_d_3208 = 0
prev_pred_w_3208 = 0
prev_pred_rho_3208 = 0
prev_state_3208 = 0
prev_state_name_3208 = 0


url = os.getenv("MODEL_WRITEBACK_URL", "http://192.168.100.171:1880/Post_mikong")

class predict_params(BaseModel):
    data_long: list
    data_short: list
    para: dict

class predRho_params(BaseModel):
    data:list

class jiayao_params(BaseModel):
    data: list
    para: dict

# 密度设定值预测函数
@app.post("/predictRhoSD")
def predictRhoSD(params: predRho_params):

    pred_rho_SD_MM, pred_rho_SD_KM = predict_RhoSD(params.data)
    return {"data":
                {
                    "pred_MMrho_SD": pred_rho_SD_MM,
                    "pred_KMrho_SD": pred_rho_SD_KM
                },
            "code": 200,
            "msg": "预测成功"}

# 3207密度控制调用接口
@app.post("/mikong3207_predict")
def mikong3207_predict(params: predict_params):

    global counter3207

    counter3207 += 1
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    str = "\n\n---3207({})---".format(counter3207)
    print(str+formatted_time+"----------------------------------------")

    if counter3207 == 1:
        params.para["update_ctrl"] = 1   #首次启动就更新控制器


    pred_d, pred_w, pred_rho, state, state_name = mikong3207(params.data_long, params.data_short, params.para)

    print("---分流控制器最终设定：%d---补水控制器最终设定：%d---" % (pred_d, pred_w))

    #计数器更新操作
    if state == 1:  #如果停车，计数器清0
        counter3207 = 0

    #-------------------------写入操作-------------------
    #---写分流---
    try:
        payload = {
            "Print": "ns=2;s=3207密度.OPC.分流阀设定开度",
            "Type": "Int16",
            "Value": pred_d
        }
        # 发送POST请求
        response = requests.post(
            url,
            json=payload,  # 自动设置 Content-Type 为 application/json
            timeout=1
        )
        # 检查响应状态
        response.raise_for_status()  # 如果状态码非2xx会抛异常
    except requests.exceptions.RequestException as e:
        print("请求异常：", str(e))

    # ---写补水---
    water_switch = params.para["water_switch"]    # 判断补水阀切换按钮状态

    if water_switch == 0:
        try:
            payload = {
                "Print": "ns=2;s=3207密度.OPC.3207稀释水阀",
                "Type": "Float",
                "Value": pred_w
            }
            # 发送POST请求
            response = requests.post(
                url,
                json=payload,  # 自动设置 Content-Type 为 application/json
                timeout=1
            )
            # 检查响应状态
            response.raise_for_status()  # 如果状态码非2xx会抛异常
        except requests.exceptions.RequestException as e:
            print("请求异常：", str(e))

    # ---写备用补水---
    if water_switch == 1:
        try:
            payload = {
                "Print": "ns=2;s=3207密度.3207密度.补水阀设定",
                "Type": "Float",
                "Value": pred_w
            }
            # 发送POST请求
            response = requests.post(
                url,
                json=payload,  # 自动设置 Content-Type 为 application/json
                timeout=1
            )
            # 检查响应状态
            response.raise_for_status()  # 如果状态码非2xx会抛异常
        except requests.exceptions.RequestException as e:
            print("请求异常：", str(e))

    # 返回字典结构
    return {"data":
                {
                    "pred_d": pred_d,
                    "pred_w": pred_w,
                    "pred_rho": pred_rho,
                    "state": state,
                    "state_name": state_name
                },
            "code": 200,
            "msg": "预测成功"}

#3208密控接口
@app.post("/mikong3208_predict")
def mikong3208_predict(params: predict_params):

    global counter3208, pwm_ctrl_3208,prev_pred_d_3208,prev_pred_w_3208,prev_pred_rho_3208,prev_state_3208,prev_state_name_3208

    counter3208 += 1
    # pwm_ctrl_3208 += 1
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    str = "\n\n---3208({})---".format(counter3208)
    print(str+formatted_time+"----------------------------------------")

    if counter3208 == 1:
        params.para["update_ctrl"] = 1   #首次启动就更新控制器

    # if pwm_ctrl_3208 == 2 or pwm_ctrl_3208 == 4 or pwm_ctrl_3208 == 6:
    pred_d, pred_w, pred_rho, state, state_name = mikong3208(params.data_long, params.data_short, params.para)
    prev_pred_d_3208 = pred_d
    prev_pred_w_3208 = pred_w
    prev_pred_rho_3208 = pred_rho
    prev_state_3208 = state
    prev_state_name_3208 = state_name
    # else:
    #     pred_d, pred_w, pred_rho, state, state_name = mikong3208(params.data_long, params.data_short, params.para)
    #     pred_d = prev_pred_d_3208
    #     pred_w = prev_pred_w_3208
    #     prev_pred_rho = pred_rho
    #     state = state
    #     state_name = state_name

    print("---分流控制器最终设定：%d---补水控制器最终设定：%d---" % (pred_d, pred_w))

    #计数器更新操作
    if state == 1:  #如果停车，计数器清0
        counter3208 = 0
    # if pwm_ctrl_3208 == 6:
    #     pwm_ctrl_3208 = 0

    # -------------------------写入操作-------------------
    #---写分流---
    try:
        payload = {
            "Print": "ns=2;s=3208密度.OPC.分流阀设定开度",
            "Type": "Float",
            "Value": pred_d
        }
        # 发送POST请求
        response = requests.post(
            url,
            json=payload,  # 自动设置 Content-Type 为 application/json
            timeout=1
        )
        # 检查响应状态
        response.raise_for_status()  # 如果状态码非2xx会抛异常
    except requests.exceptions.RequestException as e:
        print("请求异常：", str(e))

    # ---写补水---
    water_switch = params.para["water_switch"]  # 判断补水阀切换按钮状态
    if water_switch == 0:
        try:
            payload = {
                "Print": "ns=2;s=3208密度.OPC.3208稀释水阀",
                "Type": "Float",
                "Value": pred_w
            }
            # 发送POST请求
            response = requests.post(
                url,
                json=payload,  # 自动设置 Content-Type 为 application/json
                timeout=1
            )
            # 检查响应状态
            response.raise_for_status()  # 如果状态码非2xx会抛异常
        except requests.exceptions.RequestException as e:
            print("请求异常：", str(e))

    # ---写备用补水---
    if water_switch == 1:
        try:
            payload = {
                "Print": "ns=2;s=3208密度.3208密度.补水阀设定",
                "Type": "Float",
                "Value": pred_w
            }
            # 发送POST请求
            response = requests.post(
                url,
                json=payload,  # 自动设置 Content-Type 为 application/json
                timeout=1
            )
            # 检查响应状态
            response.raise_for_status()  # 如果状态码非2xx会抛异常
        except requests.exceptions.RequestException as e:
            print("请求异常：", str(e))

    # 返回字典结构
    return {"data":
                {
                    "pred_d": pred_d,
                    "pred_w": pred_w,
                    "pred_rho": pred_rho,
                    "state": state,
                    "state_name": state_name
                },
            "code": 200,
            "msg": "预测成功"}


#316密控接口
@app.post("/mikong316_predict")
def mikong316_predict(params: predict_params):

    global counter316

    counter316 += 1
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    str = "\n\n---316({})---".format(counter316)
    print(str+formatted_time+"----------------------------------------")

    if counter316 == 1:
        params.para["update_ctrl"] = 1   #首次启动就更新控制器


    pred_d, pred_w, pred_rho, state, state_name = mikong316(params.data_long, params.data_short, params.para)

    print("---分流控制器最终设定：%d---补水控制器最终设定：%d---" % (pred_d, pred_w))
    #计数器更新操作
    if state == 1:  #如果停车，计数器清0
        counter316 = 0

    # -------------------------写入操作-------------------
    #---写分流---
    try:
        payload = {
            "Print": "ns=2;s=块煤密度.块煤密度.分流阀设定开度1",
            "Type": "Float",
            "Value": pred_d
        }
        # 发送POST请求
        response = requests.post(
            url,
            json=payload,  # 自动设置 Content-Type 为 application/json
            timeout=1
        )
        # 检查响应状态
        response.raise_for_status()  # 如果状态码非2xx会抛异常
    except requests.exceptions.RequestException as e:
        print("请求异常：", str(e))

    # ---写补水---
    water_switch = params.para["water_switch"]  # 判断补水阀切换按钮状态
    if water_switch == 0:
        try:
            payload = {
                "Print": "ns=2;s=块煤密度.块煤密度.补水阀设定1",
                "Type": "Float",
                "Value": pred_w
            }
            # 发送POST请求
            response = requests.post(
                url,
                json=payload,  # 自动设置 Content-Type 为 application/json
                timeout=1
            )
            # 检查响应状态
            response.raise_for_status()  # 如果状态码非2xx会抛异常
        except requests.exceptions.RequestException as e:
            print("请求异常：", str(e))

    # ---写备用补水---
    if water_switch == 1:
        try:
            payload = {
                "Print": "ns=2;s=块煤密度.块煤密度.补水阀设定",
                "Type": "Float",
                "Value": pred_w
            }
            # 发送POST请求
            response = requests.post(
                url,
                json=payload,  # 自动设置 Content-Type 为 application/json
                timeout=1
            )
            # 检查响应状态
            response.raise_for_status()  # 如果状态码非2xx会抛异常
        except requests.exceptions.RequestException as e:
            print("请求异常：", str(e))

    # 返回字典结构
    return {"data":
                {
                    "pred_d": pred_d,
                    "pred_w": pred_w,
                    "pred_rho": pred_rho,
                    "state": state,
                    "state_name": state_name
                },
            "code": 200,
            "msg": "预测成功"}

# # 加药控制预测接口
# # 1min调用一次
# @app.post("/jiayao601_predict")
# def jiayao601_predict(params: jiayao_params):
#
#     global counter601
#     counter601 += 1
#     now = datetime.datetime.now()
#     formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
#
#     str = "\n\n---601({})---".format(counter601)
#     print(str+formatted_time+"----------------------------------------")
#
#     pred_pump, state, state_name = jiayao601(params.data, params.para)
#
#     return {"data":
#         {
#             "pred_pump": pred_pump,
#             "state": state,
#             "state_name": state_name
#         },
#         "code": 200,
#         "msg": "预测成功"}

# 服务启动
if __name__ == "__main__":
    uvicorn.run(app,host=console_cfg["host"],port=console_cfg["port"])


