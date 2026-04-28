import os
import yaml

root_path = os.path.dirname(__file__).replace("\\","/")

def read_cfg(name):
    with open(f"{root_path}/{name}.yaml", "r") as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    return config

api_cfg, console_cfg, database_cfg = read_cfg("api"), read_cfg("console"), read_cfg("database")
