import datetime
import time
import random
import logging
import requests
import configUtil
from send import sendMSG


def request(url, authorization, type="POST", parm=None):  # 封装请求方法
    header = {"Content-Type": "application/json", "authorization": authorization}
    r = requests.request(method=type, url=url, headers=header, json=parm)
    if r.status_code != 201 and r.status_code != 200:
        logging.error("请求失败,响应状态码:" + str(r.status_code))
        raise Exception("响应状态码:" + str(r.status_code) + "\n请求url:" + url + "\n消息:API可能已经变更，请暂停使用程序！")
    return r


def getCode(phone):  # 获取验证码
    logging.info("开始请求验证码")
    url = "http://tiantang.mogencloud.com/web/api/login/code"
    r = requests.post(url, data={'phone': phone})
    if r.status_code != 201 and r.status_code != 200:
        logging.error("请求失败,响应状态码:" + str(r.status_code))
        raise Exception("响应状态码:" + str(r.status_code) + "\n请求url:" + url + "\n消息:API可能已经变更，请暂停使用程序！")
    data = r.json()
    if data['errCode'] != 0:
        logging.error("请求验证码失败,[提示信息]" + data['msg'] + "[错误码]" + str(data['errCode']))
    else:
        logging.info("请求验证码成功")


def getToken(phone, authCode):  # 获取Token
    logging.info("开始请求Token")
    url = "http://tiantang.mogencloud.com/web/api/login"
    r = requests.post(url, data={'phone': phone, 'authCode': authCode})
    if r.status_code != 201 and r.status_code != 200:
        logging.error("请求失败,响应状态码:" + str(r.status_code))
        raise Exception("响应状态码:" + str(r.status_code) + "\n请求url:" + url + "\n消息:API可能已经变更，请暂停使用程序！")
    data = r.json()
    if data['errCode'] != 0:
        data = r.json()
        msg = data['msg']
        d = ""
        errCode = data['errCode']
        logging.error("登陆失败,[提示信息]" + data['msg'] + "[错误码]" + str(data['errCode']))
    else:
        msg = data['msg']
        d = data['data']['token']
        errCode = 0
        logging.info("登陆成功,[Token]" + d)
    return {'msg': msg, 'data': d, 'errCode': errCode}


def getUserInfo(authorization):  # 甜糖用户初始化信息，可以获取待收取的推广信息数，可以获取账户星星数
    logging.info("开始获取用户信息")
    url = "http://tiantang.mogencloud.com/web/api/account/message/loading"
    data = request(url, authorization).json()
    if data['errCode'] != 0:
        logging.error("authorization已经失效!")
        configUtil.updataConfig({'authorization': ''})
        raise Exception("authorization已经失效!")
    logging.info("用户信息获取成功,[账户昵称]" + data['data']['nickName'] + "[手机号]" + data['data']['phoneNum'])
    return data['data']


def getDevicesList(authorization):  # 获取当前设备列表，可以获取待收的星星数
    logging.info("开始获取设备列表")
    url = "http://tiantang.mogencloud.com/api/v1/devices?page=1&type=2&per_page=200"
    data = request(url, authorization, type="GET").json()
    if data['errCode'] != 0:
        configUtil.updataConfig({'authorization': ''})
        raise Exception("authorization已经失效")
    devicesList = data['data']['data']
    logging.info("获取设备列表成功,[设备数量]" + str(len(devicesList)))
    if len(devicesList) == 0:
        logging.error("该账号尚未绑定设备，请绑定设备后再尝试！")
        raise Exception("该账号尚未绑定设备，请绑定设备后再尝试！")
    return devicesList


def signIn(authorization):  # 签到功能
    logging.info("开始收取签到收益")
    url = "http://tiantang.mogencloud.com/web/api/account/sign_in"
    data = request(url, authorization).json()
    if data['errCode'] != 0:
        msg = "[签到奖励]0-🌟(失败:" + data['msg'] + ")"
        star = 0
        errCode = data['errCode']
        logging.info("签到失败,[提示信息]" + data['msg'] + "[错误码]" + str(data['errCode']))
    else:
        msg = "[签到奖励]" + str(data['data']) + "-🌟"
        star = data['data']
        errCode = 0
        logging.info("签到成功,获取到" + str(data['data']))
    return {'msg': msg, 'data': star, 'errCode': errCode}


def scoreLogs(authorization, score):  # 收取推广奖励星星
    logging.info("开始收取推广收益")
    if score == 0:
        msg = "[推广奖励]" + str(score) + "-🌟"
        star = score
        errCode = 0
        logging.info("无推广收益")
    else:
        url = "http://tiantang.mogencloud.com/api/v1/promote/score_logs"
        data = request(url, authorization, parm={'score': score}).json()
        if data['errCode'] != 0:
            msg = "[推广奖励]0-🌟(收取异常)"
            star = 0
            errCode = data['errCode']
            logging.info("收取推广奖励失败,[提示信息]" + data['msg'] + "[错误码]" + str(data['errCode']))
        else:
            msg = "[推广奖励]" + str(score) + "-🌟"
            star = score
            errCode = 0
            logging.info("收取推广奖励成功,获取到" + str(score))
    return {'msg': msg, 'data': star, 'errCode': errCode}


def collectDevice(authorization):  # 收取设备奖励
    resultStr = []
    resultScore = 0
    for device in getDevicesList(authorization):
        logging.info("开始收取[" + device['alias'] + "]设备")
        parm = {'device_id': device['hardware_id'], 'score': device['inactived_score'], 'name': device['alias']}
        if parm['score'] == 0:
            resultStr.append("[" + parm['name'] + "]0-🌟")
            logging.info("[" + device['alias'] + "]设备无收益")
        else:
            url = "http://tiantang.mogencloud.com/api/v1/score_logs"
            data = request(url, authorization, parm=parm).json()
            if data['errCode'] != 0:
                resultStr.append("[" + parm['name'] + "]0-🌟(收取异常)")
                logging.info("收取[" + device['alias'] + "]设备异常,[提示信息]" + data['msg'] + "[错误码]" + str(data['errCode']))
            else:
                resultStr.append("[" + parm['name'] + "]" + str(parm['score']) + "-🌟")
                resultScore += parm['score']
                logging.info("收取[" + device['alias'] + "]设备成功,获取到" + str(parm['score']))
            sleep_time = random.randint(1, 4)
            time.sleep(sleep_time)
    logging.info("全部设备收取完成,获取到" + str(resultScore))
    return {'msg': resultStr, 'data': resultScore, 'errCode': 0}


def countBandwidth(authorization):  # 计算结算带宽
    logging.info("开始获取设备日志")
    url = "http://tiantang.mogencloud.com/api/v1/device_logs?page=1&per_page=200"
    data = request(url, authorization, type="GET").json()
    if data['errCode'] == 0:
        logging.info("获取设备日志成功,开始计算结算带宽")
        day_time = int(time.mktime(datetime.date.today().timetuple()))
        billing_bandwidth = 0
        for device_info in data['data']['data']:
            if day_time >= device_info['completed_at']:
                break
            billing_bandwidth = billing_bandwidth + device_info['billing_bandwidth']
        billing_bandwidth = billing_bandwidth / 1024
        billing_bandwidth = round(billing_bandwidth, 2)
        logging.info("结算带宽计算成功,获取到" + str(billing_bandwidth) + "Mbps")
        return {'data': str(billing_bandwidth), 'msg': "[结算带宽]" + str(billing_bandwidth) + "Mbps", 'errCode': 0}
    else:
        logging.error("获取设备日志失败")
        return {'data': "", 'msg': "[结算带宽]获取失败", 'errCode': data['errCode']}


def aliPay(authorization, realName, cardId, score):  # 支付宝提现
    url = "http://tiantang.mogencloud.com/api/v1/withdraw_logs"
    score = score - score % 100
    if score < 1000:
        return "[自动提现]支付宝提现失败，星愿数不足1000", ""
    if score >= 10000:
        score = 9900
    parm = {
        'score': score,
        'real_name': realName,
        'card_id': cardId,
        'bank_name': "支付宝",
        'sub_bank_name': '',
        'type': 'zfb'
    }
    data = request(url, authorization, parm=parm).json()
    if data['errCode'] == 403002:
        logging.error("[自动提现]支付宝提现失败，[错误信息]" + data['msg'] + "[星愿数]" + str(score))
        return "[自动提现]支付宝提现失败，" + data['msg'], ""
    if data['errCode'] != 0:
        print("" + data['msg'] + str(score))
        logging.error("[自动提现]支付宝提现失败，[错误信息]" + data['msg'] + "[星愿数]" + str(score))
        return "[自动提现]支付宝提现失败，请关闭自动提现等待更新并及时查看甜糖客户端app的账目", ""

    data = data['data']
    zfbID = data['card_id']
    pre = zfbID[0:4]
    end = zfbID[len(zfbID) - 4:len(zfbID)]
    zfbID = pre + "***" + end
    item = []
    item.append("提现方式：支付宝")
    item.append("支付宝号：" + zfbID)
    logging.info("[自动提现]扣除" + str(score))
    return "[自动提现]扣除" + str(score) + "-🌟", item


def bankCard(authorization, realName, cardId, score, bankName, subBankName):  # 银行卡提现
    url = "http://tiantang.mogencloud.com/api/v2/withdraw_logs"
    parm = {
        'score': score,
        'real_name': realName,
        'card_id': cardId,
        'bank_name': bankName,
        'sub_bank_name': subBankName,
        'type': 'bank_card'
    }
    data = request(url, authorization, parm=parm).json()
    if score < 1000:
        logging.info("[自动提现]银行卡提现失败，星愿数不足1000")
        return "[自动提现]银行卡提现失败，星愿数不足1000", ""

    if data['errCode'] == 403002:
        logging.error("[自动提现]银行卡提现失败，[错误信息]" + data['msg'] + "[星愿数]" + str(score))
        return "[自动提现]银行卡提现失败，" + data['msg'], ""
    if data['errCode'] != 0:
        print("" + data['msg'] + str(score))
        logging.error("[自动提现]银行卡提现失败，[错误信息]" + data['msg'] + "[星愿数]" + str(score))
        return "[自动提现]银行卡提现失败，请关闭自动提现等待更新并及时查看甜糖客户端app的账目", ""

    data = data['data']
    yhkID = data['card_id']
    pre = yhkID[0:4]
    end = yhkID[len(yhkID) - 4:len(yhkID)]
    yhkID = pre + "****" + end
    item = []
    item.append("提现方式：银行卡")
    item.append("银行卡号：" + yhkID)
    logging.info("[自动提现]扣除" + str(score))
    return "[自动提现]扣除" + str(score) + "-🌟", item


def withdrawType(authorization, userInfo):  # 根据用户是否签约来决定提现方式
    isEContract = userInfo['isEContract']
    if isEContract:
        logging.info("[自动提现]银行卡提现")
        # 已经实名签约的采用银行卡提现
        bankCardList = userInfo['bankCardList']  # 获取支付宝列表
        if len(bankCardList) == 0:
            withdraw_str = "[自动提现]银行卡提现失败，原因是未绑定银行卡，请绑定一张银行卡"
            return withdraw_str, ""
        else:
            withdraw_str, item = bankCard(score=userInfo['score'],
                                          realName=bankCardList[0]['name'],
                                          cardId=bankCardList[0]['bankCardNum'],
                                          bankName=bankCardList[0]['bankName'],
                                          subBankName=bankCardList[0]['subBankName'])
    else:
        # 未实名签约采用支付宝提现
        logging.info("[自动提现]支付宝提现")
        zfbList = userInfo['zfbList']  # 获取支付宝列表
        if len(zfbList) == 0:
            withdraw_str = "[自动提现]支付提现失败，原因是未绑定支付宝号，请绑定支付宝账户"
            return withdraw_str, ""
        else:
            withdraw_str, item = aliPay(authorization=authorization,
                                        score=userInfo['score'],
                                        realName=zfbList[0]['name'],
                                        cardId=zfbList[0]['account'])
    return withdraw_str, item


def withdraw(authorization, week, userInfo):
    now_week = int(datetime.datetime.now().isoweekday())  # 获取今天是星期几返回1-7
    items = None
    msg = "无"
    errCode = 1
    if week == now_week:
        logging.info("[自动提现]到达设定日期，开始提现")
        msg, items = withdrawType(authorization, userInfo)
        errCode = 0
    return {'data': items, 'msg': msg, 'errCode': errCode}


def createContent(userInfo,signInData,scoreLogData,deviceData,bandwidthData,withdrawData):
    total = signInData['data'] + scoreLogData['data'] + deviceData['data']
    total_str = "[日总收益]" + str(total) + "-🌟"
    accountScore = userInfo['score']
    nickName = "[账户昵称]" + userInfo['nickName']
    accountScore_str = "[账户星愿]" + str(accountScore+total) + "-🌟"
    now_time = datetime.datetime.now().strftime('%F %T')
    now_time_str = "[当前时间]" + now_time
    content = []
    content.append(now_time_str)
    content.append(nickName)
    content.append(bandwidthData['msg'])
    content.append(accountScore_str)
    content.append(total_str)
    total_info_str = []
    total_info_str.append(signInData['msg'])
    total_info_str.append(scoreLogData['msg'])
    total_info_str.append("[设备收益]" + str(deviceData['data']) + "-🌟")
    content.append(total_info_str)
    # 提现详情
    if withdrawData['errCode'] == 0:
        content.append(withdrawData['msg'])
        if len((withdrawData['data'])) != 0:
            content.append(withdrawData['data'])

    # 设备详情
    content.append("[设备详细]：")
    content = content + deviceData['msg']  # 设备消息返回的是list
    return content


# 收取星星并提现
def collect_star(config):
    authorization = config.get('authorization')
    userInfo = getUserInfo(authorization)  # 获取用户信息
    signInData = signIn(authorization)  # 收取签到收益
    scoreLogData = scoreLogs(authorization, userInfo['inactivedPromoteScore'])  # 收取推广收益
    deviceData = collectDevice(authorization)  # 收取设备收益
    bandwidthData = countBandwidth(authorization)  # 计算结算带宽
    withdrawData = withdraw(authorization, config.get('week'), userInfo)  # 自动提现

    content = createContent(userInfo=userInfo,  #生成消息内容
                            signInData=signInData,
                            scoreLogData=scoreLogData,
                            deviceData=deviceData,
                            bandwidthData=bandwidthData,
                            withdrawData=withdrawData)
    sendMSG("[甜糖星愿]星愿日结详细", content)  # 发送消息


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config = configUtil.getConfig()
    if config['authorization'] !=None and len(config['authorization'])>10:
        collect_star(config)
    else:
        print("获取Token")
        phone = input('请输入手机号')
        getCode(phone)
        code = input('请输入验证码')
        configUtil.updataConfig({"authorization":getToken(phone,code)['data']})

