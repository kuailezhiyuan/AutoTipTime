import json
import logging
import traceback

baseConfig = {
        'authorization':"",
        'week':"",
        'PushPlus_token':"",
        'tg_bot_token':"",
        'chat_id':"",
        'DingDing_access_token':"",
        'DingDing_secret':"",
        'iyuu_token':"",
        'QMSG_key':"",
        'Bark_key':""
    }


def getDict(new,old):  #新旧信息合并
    temp = old
    for key in new.keys() & old.keys():
        temp[key] = new[key]
    return temp


def getConfig():  #获取配置信息
    with open('config.json', 'a+') as f:
        f.seek(0)
        try:
            config = json.loads(f.read())
        except Exception as e:
            traceback.print_exc()
            logging.error("配置文件读取失败,初始化操作")
            config = baseConfig
    return config


def updataConfig(config): #更新配置信息
    with open('config.json', 'a+') as f:
        f.seek(0)
        try:
            old=json.loads(f.read())
        except Exception as e:
            traceback.print_exc()
            logging.error("配置文件读取失败,初始化操作")
            old= baseConfig
        f.seek(0)
        f.truncate()
        f.write(json.dumps(getDict(config,old), indent=4, ensure_ascii=False))


