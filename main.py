import requests as r
import json
import os

# with open('./config.json', 'rt') as f:   # Local debugging
#     config = json.loads(f.read())
#     f.close()

class RunError():
    pass

# Running in Github Action, use this to get the config
config = os.environ.get['config']

token = config['token']
client_type = config['type']
android = config['android']
deviceid = config['deviceid']
devicename = config['devicename']
devicemodel = config['devicemodel']
appid = config['appid']
version = '2.2.0'

SignURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/listNotifications?status=NotificationStatusUnread&type=NotificationTypePopup&is_sort=true'
headers = {
    'x-rpc-combo_token': token,
    'x-rpc-client_type': str(client_type),
    'x-rpc-app_version': str(version),
    'x-rpc-sys_version': str(android),
    'x-rpc-channel': 'mihoyo',
    'x-rpc-device_id': deviceid,
    'x-rpc-device_name': devicename,
    'x-rpc-device_model': devicemodel,
    'x-rpc-app_id': str(appid),
    'Referer': 'https://app.mihoyo.com',
    'Host': 'api-cloudgame.mihoyo.com',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'okhttp/4.9.0'
}

if __name__ == '__main__':
    if config == '': raise RunError(f"请在Settings->Secrets->Actions页面中新建名为config的变量，并将你的配置填入后再运行！")    # Verify config
    else:
        if token == '' or android == 0 or deviceid == '' or devicemodel == '' or appid == 0:
            raise RunError(f'请确认您的配置文件配置正确再运行本程序！')
    res = r.get(SignURL, headers=headers)
    if json.loads(res.text)['message'] != 'OK':
        raise RunError(f"请带着一下内容到 https://github.com/ElainaMoe/MHYY-AutoCheckin/issues 发起issue解决（或者自行解决）。签到出错，返回信息如下：{res['text']}")
    else: pass