import datetime

import pymysql
from cfg import database_cfg
from utils.common import get_strftime

db = pymysql.connect(
    host=database_cfg["connect"]["host"],
    port=database_cfg["connect"]["port"],
    user=database_cfg["connect"]["user"],
    password=database_cfg["connect"]["password"],
    database=database_cfg["connect"]["database"],
)
cursor = db.cursor()

def select_data(key, start, end):
    try:
        execute = f"SELECT TAG FROM lishijilu"
        cursor.execute(execute)
        fetch = cursor.fetchall()
        list = [row[0] for row in fetch]
        print(list)
        # if end == "":
            # end = get_strftime()
        # execute = f"SELECT TAG, VALUE, DATETIME FROM lishijilu WHERE DATETIME BETWEEN '{start}' AND '{end}'"
        # cursor.execute(execute)
        # fetch = cursor.fetchall()
        # for row in fetch:
        #     print(row,datetime.datetime.strftime(row[2], "%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        
        print(e)

select_data("density_predict")