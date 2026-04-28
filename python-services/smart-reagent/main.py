## version 2.0 updated in 20250918
##   1
#端口号 6788


import os
import sys

import uvicorn
from pydantic import BaseModel
from typing import Union
import datetime
from cfg import console_cfg
from fastapi import FastAPI, Form, File, UploadFile
from model import jiayao601, jiayao602, jiayao5201, jiayao5202
import requests

app = FastAPI()

counter601 = 0
counter602 = 0
counter5201 = 0
counter5202 = 0

url = os.getenv("MODEL_WRITEBACK_URL", "http://192.168.100.171:1880/Post_mikong")


class jiayao_params(BaseModel):
    data_long: list
    data_short: list
    para: dict


# 加药控制预测接口
# 1min调用一次
@app.post("/jiayao601_predict")
def jiayao601_predict(params: jiayao_params):

    global counter601
    counter601 += 1
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    str = "\n\n---601({})---".format(counter601)
    print(str+formatted_time+"----------------------------------------")

    pred_pump, numPump, pred_bkpump, valveMN, state, state_name = jiayao601(params.data_long, params.data_short, params.para)

    #计数器更新操作
    if state == 1:  #如果停车，计数器清0
        counter601 = 0

    #-------------------------写入操作-------------------
    numPump = params.para["pumpNumber"]
    if numPump == 1:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 2:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 3:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 4:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 5:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 6:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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

    numbkPump = params.para["backupPumpNumber"]   #备用泵
    if numbkPump != 0:
        if numbkPump == 1:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 2:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 3:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 4:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 5:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 6:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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

    return {"data":
        {
            "pred_pump": pred_pump,
            "state": state,
            "state_name": state_name,
            "pred_bkpump": pred_bkpump
        },
        "code": 200,
        "msg": "预测成功"}

@app.post("/jiayao602_predict")
def jiayao602_predict(params: jiayao_params):

    global counter602
    counter602 += 1
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    str = "\n\n---602({})---".format(counter602)
    print(str+formatted_time+"----------------------------------------")

    pred_pump, numPump, pred_bkpump, valveMN, state, state_name = jiayao602(params.data_long, params.data_short, params.para)

    #计数器更新操作
    if state == 1:  #如果停车，计数器清0
        counter602 = 0

    #-------------------------写入操作-------------------
    numPump = params.para["pumpNumber"]
    if numPump == 1:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 2:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 3:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 4:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 5:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 6:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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

    numbkPump = params.para["backupPumpNumber"]   #备用泵
    if numbkPump != 0:
        if numbkPump == 1:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 2:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 3:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 4:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 5:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 6:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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

    return {"data":
        {
            "pred_pump": pred_pump,
            "state": state,
            "state_name": state_name,
            "pred_bkpump": pred_bkpump
        },
        "code": 200,
        "msg": "预测成功"}

@app.post("/jiayao5201_predict")
def jiayao5201_predict(params: jiayao_params):

    global counter5201
    counter5201 += 1
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    str = "\n\n---5201({})---".format(counter5201)
    print(str+formatted_time+"----------------------------------------")

    pred_pump, numPump, pred_bkpump, valveMN, state, state_name = jiayao5201(params.data_long, params.data_short, params.para)

    #计数器更新操作
    if state == 1:  #如果停车，计数器清0
        counter5201 = 0

    #-------------------------写入操作-------------------
    numPump = params.para["pumpNumber"]
    if numPump == 1:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 2:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 3:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 4:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 5:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 6:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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

    numbkPump = params.para["backupPumpNumber"]   #备用泵
    if numbkPump != 0:
        if numbkPump == 1:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 2:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 3:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 4:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 5:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 6:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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

    return {"data":
        {
            "pred_pump": pred_pump,
            "state": state,
            "state_name": state_name,
            "pred_bkpump": pred_bkpump
        },
        "code": 200,
        "msg": "预测成功"}

@app.post("/jiayao5202_predict")
def jiayao5202_predict(params: jiayao_params):

    global counter5202
    counter5202 += 1
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    str = "\n\n---5202({})---".format(counter5202)
    print(str+formatted_time+"----------------------------------------")

    pred_pump, numPump, pred_bkpump, valveMN, state, state_name = jiayao5202(params.data_long, params.data_short, params.para)

    #计数器更新操作
    if state == 1:  #如果停车，计数器清0
        counter5202 = 0

    #-------------------------写入操作-------------------
    numPump = params.para["pumpNumber"]
    if numPump == 1:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 2:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 3:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 4:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 5:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤1号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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
    if numPump == 6:
        try:
            payload = {
                "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤2号给定频率",
                "Type": "Int16",
                "Value": pred_pump
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

    numbkPump = params.para["backupPumpNumber"]   #备用泵
    if numbkPump != 0:
        if numbkPump == 1:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 2:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.末煤2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 3:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 4:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.新加药2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 5:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤1号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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
        if numbkPump == 6:
            try:
                payload = {
                    "Print": "ns=2;s=卓郎加药系统6个泵.加药系统6个泵.块煤2号给定频率",
                    "Type": "Int16",
                    "Value": pred_bkpump
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

    return {"data":
        {
            "pred_pump": pred_pump,
            "state": state,
            "state_name": state_name,
            "pred_bkpump": pred_bkpump
        },
        "code": 200,
        "msg": "预测成功"}

# 服务启动
if __name__ == "__main__":
    uvicorn.run(app,host=console_cfg["host"],port=console_cfg["port"])


