import base64
import hashlib
import hmac
import logging
import time
import urllib
import configUtil
import requests


def sendPushPlus(token, text, desp):  # 发送PushPlus代码
    url = "http://www.pushplus.plus/send"
    body_json = {"token": token, "title": text, "content": desp, "template": "html"}
    r = requests.post(url, json=body_json)
    if r.status_code != 200:
        logging.error("sendPushPlus(新版)方法请求失败")
        sendPushPlusOld(token, text, desp)
    else:
        logging.info("消息已经推送至PushPlus，请注意查验！")


def sendPushPlusOld(token, text, desp):  # 发送PlusPlus代码(旧版)
    url = "http://pushplus.hxtrip.com/send"
    body_json = {"token": token, "title": text, "content": desp, "template": "html"}
    r = requests.post(url, json=body_json)
    if r.status_code != 200:
        logging.error("sendPushPlus(旧版)方法请求失败")
    else:
        logging.info("消息已经推送至PushPlus，请注意查验！")


def sendTelegram(token, chatId, desp):  # 发送Telegram代码
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    body_json = {"chat_id": chatId, "text": desp}
    r = requests.post(url, json=body_json)
    if r.status_code.status != 200:
        logging.error("sendTelegram方法请求失败，请确保连接了外国网络！")
    else:
        logging.info("消息已经推送至Telegram，请注意查验！")


def sendDingDing(token, secret, desp):  # 发送Telegram代码
    url = "https://oapi.dingtalk.com/robot/send?access_token=" + token
    if len(secret) > 10:
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = url + "&timestamp=" + str(timestamp) + "&sign=" + sign
    body_json = {"msgtype": "text", "text": {"content": desp}}
    r = requests.post(url, json=body_json)
    if r.status_code.status != 200:
        logging.error("sendDingDing方法请求失败")
    else:
        logging.info("消息已经推送至钉钉群机器人，请注意查验！")


def sendIYUU(token, text, desp):  # 发送PlusPlus代码
    url = "http://iyuu.cn/" + token + ".send"
    body_json = "text=" + text + "&desp=" + desp
    r = requests.post(url, json=body_json)
    if r.status_code.status != 200:
        logging.error("sendIYUU方法请求失败")
    else:
        logging.info("消息已经推送至爱语飞飞公众号，请注意查验！")


def sendQMSG(token, desp):  # 发送QMSG代码
    url = "https://qmsg.zendee.cn/send/" + token
    body_json = "msg=" + desp
    r = requests.post(url, json=body_json)
    if r.status_code.status != 200:
        logging.error("sendQMSG方法请求失败")
    else:
        logging.info("消息已经推送至QQ，请注意查验！")


def sendBark(token, text, desp):  # 发送PlusPlus代码
    url = "http://api.day.app/" + token + "/"
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    body_json = "title=" + text + "&body=" + desp
    r = requests.post(url, json=body_json)
    if r.status_code.status != 200:
        logging.error("sendBark方法请求失败")
    else:
        logging.info("消息已经推送至Bark，请注意查验！")


def sendMSG(title, content):
    content.append("注意:以上统计仅供参考，一切请以甜糖客户端APP为准。")
    config = configUtil.getConfig()
    if len(config['PushPlus_token']) > 10:  # PushPlus(先发送新版，失败后发送旧版)
        msgContent = ""
        num = 0
        for item in content:
            num = num + 1
            if len(content) == num:
                msgContent = msgContent + "<hr style='border: 2px dashed #ccc'>"
            if isinstance(item, list):
                for i in item:
                    msgContent = msgContent + "|------" + i + "<br>"
            else:
                msgContent = msgContent + "" + item + "<br>"
        sendPushPlus(config['PushPlus_token'],title, msgContent)

    if len(config['tg_bot_token']) > 10 and len(config['chat_id']) != 0:  # (tg推送)
        msgContent = title + "\n\n"
        num = 0
        for item in content:
            num = num + 1
            if len(content) == num:
                msgContent = msgContent + "\n"
            if isinstance(item, list):
                for i in item:
                    msgContent = msgContent + "|----" + i + "\n"
            else:
                msgContent = msgContent + "" + item + "\n"
        sendTelegram(config['tg_bot_token'],config['chat_id'],msgContent)
    if len(config['DingDing_access_token']) > 10:  # (钉钉推送)
        msgContent = title + "\n\n"
        num = 0
        for item in content:
            num = num + 1
            if len(content) == num:
                msgContent = msgContent + "\n"
            if isinstance(item, list):
                for i in item:
                    msgContent = msgContent + "|----" + i + "\n"
            else:
                msgContent = msgContent + "" + item + "\n"
        sendDingDing(config['DingDing_access_token'],config['DingDing_secret'],msgContent)

    if len(config['iyuu_token']) > 10:  # (爱语飞飞推送)
        msgContent = ""
        num = 0
        for item in content:
            num = num + 1
            if len(content) == num:
                msgContent = msgContent + "***\n"
            if isinstance(item, list):
                for i in item:
                    msgContent = msgContent + ">" + i + "\n"
            else:
                msgContent = msgContent + item + "\n"
        sendIYUU(config['iyuu_token'],title, msgContent)

    if len(config['QMSG_key']) > 10:  # (QMSG酱推送)
        msgContent = title + "\n\n"
        num = 0
        for item in content:
            num = num + 1
            if len(content) == num:
                msgContent = msgContent + "\n"
            if isinstance(item, list):
                for i in item:
                    msgContent = msgContent + "|----" + i + "\n"
            else:
                msgContent = msgContent + "" + item + "\n"
        sendQMSG(config['QMSG_key'],msgContent)

    if len(config['Bark_key']) > 10:  # (Bark推送)
        msgContent = ""
        num = 0
        for item in content:
            num = num + 1
            if len(content) == num:
                msgContent = msgContent + "\n"
            if isinstance(item, list):
                for i in item:
                    msgContent = msgContent + "|----" + i + "\n"
            else:
                msgContent = msgContent + "" + item + "\n"
        sendBark(config['Bark_key'],title, msgContent)
