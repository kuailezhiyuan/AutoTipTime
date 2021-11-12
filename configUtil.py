import json
import logging
import traceback
from werkzeug.security import generate_password_hash, check_password_hash

baseConfig = {
    'authorization': "",
    'week': "",
    'PushPlus_token': "",
    'tg_bot_token': "",
    'chat_id': "",
    'DingDing_access_token': "",
    'DingDing_secret': "",
    'iyuu_token': "",
    'QMSG_key': "",
    'Bark_key': ""
}

basePasswd = "123456"


def getDict(new, old):  # 新旧信息合并
    temp = old
    for key in new.keys() & old.keys():
        temp[key] = new[key]
    return temp


def getPassword():
    with open('passwd', "a+", encoding='utf-8') as f:
        f.seek(0)
        passwd = f.read()
        if passwd == "":
            passwd = setPassword(basePasswd)
        return passwd


def setPassword(passwd):
    with open('passwd', "w", encoding='utf-8') as f:
        passwd = generate_password_hash(passwd)
        f.write(passwd)
    return passwd


def getConfig():  # 获取配置信息
    with open('config.json', 'a+') as f:
        f.seek(0)
        try:
            config = json.loads(f.read())
        except Exception as e:
            traceback.print_exc()
            logging.error("配置文件读取失败,初始化操作")
            config = baseConfig
            f.seek(0)
            f.truncate()
            f.write(json.dumps(config, indent=4, ensure_ascii=False))
    return config


def updataConfig(config):  # 更新配置信息
    with open('config.json', 'a+') as f:
        f.seek(0)
        try:
            old = json.loads(f.read())
        except Exception as e:
            traceback.print_exc()
            logging.error("配置文件读取失败,初始化操作")
            old = baseConfig
        f.seek(0)
        f.truncate()
        f.write(json.dumps(getDict(config, old), indent=4, ensure_ascii=False))


# 定时任务
class APSchedulerJobConfig(object):
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    JOBS = [
        {
            'id': 'No1',  # 任务唯一ID
            'func': 'client:taskJob',
            'args': '',  # 如果function需要参数，就在这里添加
            'trigger': {
                'type': 'cron',  # 类型
                'day_of_week': "*",  # 可定义具体哪几天要执行
                'hour': '9',  # 小时数
                'minute': '0'
            }
        }
    ]
