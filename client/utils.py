import json
import os
import shutil


def replace_names_with_keys():
    f = open('lobby/test.json', encoding="utf8")
    data = json.load(f)
    champion_info = {}
    for key, value in data["data"].items():
        champion_info[value["id"]] = value["key"]
    icon_path = "C:/Users/pyron/PycharmProjects/magisterka/client/icons/"
    for item in os.listdir(icon_path):
        if item[:-4] in champion_info:
            shutil.copy(icon_path + item, icon_path + champion_info[item[:-4]] + '.png')