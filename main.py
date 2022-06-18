import requests as r
import json
import os
import re
import urllib3
import sentry_sdk
import random
import time

# with open('./config.json', 'rt') as f:   # Local debugging
#     config = json.loads(f.read())
#     f.close()

sentry_sdk.init(
    "https://425d7b4536f94c9fa540fe34dd6609a2@o361988.ingest.sentry.io/6352584",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

# Running in Github Action, use this to get the config
config = json.loads(os.environ.get('config'))

with open('./config.json', 'rt') as f:   # ONLY FOR TESTING
    config = json.loads(f.read())
    f.close()

class RunError(Exception):
    pass

if config['type'] == 2:
    token = config['token']
    version = config['version']
    android = config['android']
    deviceid = config['deviceid']
    devicename = config['devicename']
    devicemodel = config['devicemodel']
    analytics = config['analytics']
elif config['type'] == 1:
    token = config['token']
    version = config['version']
    auth = config['auth']
    deviceid = config['deviceid']
    iOS_ver = config['iOS_ver']
    cookie = config['cookie']
    analytics = config['analytics']
else:
    raise RunError(f'Excepted correct type 1(iOS) or 2(Android) not {config["type"]}')

bbsid = re.findall(r'oi=[0-9]+', token)[0].replace('oi=', '')

NotificationURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/listNotifications?status=NotificationStatusUnread&type=NotificationTypePopup&is_sort=true'
WalletURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/wallet/wallet/get'
AnnouncementURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/getAnnouncementInfo'
headers = {
    'x-rpc-combo_token': token,
    'x-rpc-client_type': 2,
    'x-rpc-app_version': str(version),
    'x-rpc-sys_version': str(android),
    'x-rpc-channel': 'mihoyo',
    'x-rpc-device_id': deviceid,
    'x-rpc-device_name': devicename,
    'x-rpc-device_model': devicemodel,
    'x-rpc-app_id': '1953439974',
    'Referer': 'https://app.mihoyo.com',
    'Host': 'api-cloudgame.mihoyo.com',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'okhttp/4.9.0'
}

iOSHeaders={
    'Host': 'api-cloudgame.mihoyo.com',
    'x-rpc-device_model': 'iPhone11,8',
    'Referer': 'https://app.mihoyo.com',
    'x-rpc-device_name': 'iPhone',
    'cms-signature': 'hmac-sha1',
    # Content-Length: 2618
    'CONTENT-MD5': '2fcf1c313d507ec6652fe075ca920271',
    'Date': str(int(time.time())),
    'x-rpc-channel': 'appstore',
    'x-rpc-app_version': str(version),
    'Authorization': str(auth),
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'Connection': 'keep-alive',
    'x-rpc-client_type': '1',
    'x-rpc-device_id': str(deviceid),
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br',
    'x-rpc-sys_version': str(iOS_ver),
    'x-rpc-combo_token': str(token),
    'Cookie': str(cookie)
}


#coding:utf-8
 
import hashlib
import hmac
 
# 秘钥
sk = "e3988cce1bdcd1db1b0a1313e598b12040d4e16f"
 
# 需要加密的msg，自定义
msg = "GET\nuid:001\n1467556840"
 
 
#授权
def get_authorization(sk, msg):
    hashing = hmac.new(sk, msg, hashlib.sha1).hexdigest()
    return hashing
 

if __name__ == '__main__':
    if config == '':
        # Verify config
        raise RunError(
            f"请在Settings->Secrets->Actions页面中新建名为config的变量，并将你的配置填入后再运行！")
    else:
        if token == '' or android == 0 or deviceid == '' or devicemodel == '':
            raise RunError(f'请确认您的配置文件配置正确再运行本程序！')
    if analytics:
        # Disable SSL warning of analytics server
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if type == 2:
            ana = r.get(
                f'https://analytics.api.ninym.top/mhyy?type={config["type"]}&version={version}&android={android}&deviceid={deviceid}&devicename={devicename}&devicemodel={devicemodel}&appid={appid}&bbsid={bbsid}', verify=False)
        # else:     # iOS is not supported yet
        #     ana = r.get(
        #         f'https://analytics.api.ninym.top/mhyy?type={config["type"]}&version={version}&android={android}&deviceid={deviceid}&devicename={devicename}&devicemodel={devicemodel}&appid={appid}&bbsid={bbsid}', verify=False)
        if json.loads(ana.text)['msg'] == 'OK':
            print('统计信息提交成功，感谢你的支持！')
        elif json.loads(ana.text)['msg'] == 'Duplicated':
            print('你的统计信息已经提交过啦！感谢你的支持！')
        else:
            print(f'[WARN] 统计信息提交错误：{ana.text}')
    wait_time = random.randint(1, 3600) # Random Sleep to Avoid Ban
    print(f'为了避免同一时间签到人数太多导致被官方怀疑，开始休眠 {wait_time} 秒')
    time.sleep(wait_time)
    wallet = r.get(WalletURL, headers=headers)
    print(
        f"你当前拥有免费时长 {json.loads(wallet.text)['data']['free_time']['free_time']} 分钟，畅玩卡状态为 {json.loads(wallet.text)['data']['play_card']['short_msg']}，拥有米云币 {json.loads(wallet.text)['data']['coin']['coin_num']} 枚")
    announcement = r.get(AnnouncementURL, headers=headers)
    print(f'获取到公告列表：{json.loads(announcement.text)["data"]}')
    res = r.get(NotificationURL, headers=headers)
    try:
        if list(json.loads(res.text)['data']['list']) == []:
            success = True
            Signed = True
            Over = False
        elif json.loads(json.loads(res.text)['data']['list'][0]['msg']) == {"num": 15, "over_num": 0, "type": 2, "msg": "每日登录奖励"}:
            success = True
            Signed = False
            Over = False
        elif json.loads(json.loads(res.text)['data']['list'][0]['msg'])['over_num'] > 0:
            success = True
            Signed = False
            Over = True
        else:
            success = False
    except IndexError:
        success = False
    if success:
        if Signed:
            print(
                f'获取签到情况成功！今天是否已经签到过了呢？')
            print(f'完整返回体为：{res.text}')
        elif not Signed and Over:
            print(
                f'获取签到情况成功！当前免费时长已经达到上限！签到情况为{json.loads(res.text)["data"]["list"][0]["msg"]}')
            print(f'完整返回体为：{res.text}')
        else:
            print(
                f'获取签到情况成功！当前签到情况为{json.loads(res.text)["data"]["list"][0]["msg"]}')
            print(f'完整返回体为：{res.text}')
    else:
        raise RunError(
            f"签到失败！请带着本次运行的所有log内容到 https://github.com/ElainaMoe/MHYY-AutoCheckin/issues 发起issue解决（或者自行解决）。签到出错，返回信息如下：{res.text}")
