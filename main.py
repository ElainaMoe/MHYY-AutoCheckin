import requests as r
import json
import os
import re
import urllib3 


# with open('./config.json', 'rt') as f:   # Local debugging
#     config = json.loads(f.read())
#     f.close()


class RunError(Exception):
    pass


# Running in Github Action, use this to get the config
config = json.loads(os.environ.get('config'))

token = config['token']
client_type = config['type']
version = config['version']
android = config['android']
deviceid = config['deviceid']
devicename = config['devicename']
devicemodel = config['devicemodel']
appid = config['appid']
analytics = config['analytics']

bbsid = re.findall(r'oi=[0-9]+', token)[0].replace('oi=', '')

NotificationURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/listNotifications?status=NotificationStatusUnread&type=NotificationTypePopup&is_sort=true'
WalletURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/wallet/wallet/get'
AnnouncementURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/getAnnouncementInfo'
# PriorityAnnouncementURL = f'https://hk4e-api.mihoyo.com/common/clgm_cn/announcement/announcementapi/getAlertAnn?game=clgm&game_biz=clgm_cn&region=cg_cn&platform=android&bundle_id=com.miHoYo.cloudgames.ys&lang=zh-cn&uid={bbsid[0]}&level=10'
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
    if config == '':
        # Verify config
        raise RunError(
            f"请在Settings->Secrets->Actions页面中新建名为config的变量，并将你的配置填入后再运行！")
    else:
        if token == '' or android == 0 or deviceid == '' or devicemodel == '' or appid == 0:
            raise RunError(f'请确认您的配置文件配置正确再运行本程序！')
    if analytics:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)     # Disable SSL warning of analytics server
        ana = r.get(
            f'https://analytics.api.ninym.top/mhyy?type={client_type}&version={version}&android={android}&deviceid={deviceid}&devicename={devicename}&devicemodel={devicemodel}&appid={appid}', verify=False)
        if json.loads(ana.text)['msg'] == 'OK': print('统计信息提交成功，感谢你的支持！')
        elif json.loads(ana.text)['msg'] == 'Duplicated': print('你的统计信息已经提交过啦！感谢你的支持！')
        else: print(f'[WARN] 统计信息提交错误：{ana.text}')
    wallet = r.get(WalletURL, headers=headers)
    print(
        f"你当前拥有免费时长 {json.loads(wallet.text)['data']['free_time']['free_time']} 分钟，畅玩卡状态为 {json.loads(wallet.text)['data']['play_card']['short_msg']}，拥有米云币 {json.loads(wallet.text)['data']['coin']['coin_num']} 枚")
    announcement = r.get(AnnouncementURL, headers=headers)
    print(f'获取到公告列表：{json.loads(announcement.text)["data"]}')
    # priorityannouncement = r.get(PriorityAnnouncementURL, headers=headers)
    # print(priorityannouncement.text)
    # priorityannouncementinfo = '无' if json.loads(priorityannouncement.text)["data"]["alert"] == False else '收到重要通知，请登录云原神APP查看！'
    # print(f'当前所拥有的重要通知：{priorityannouncementinfo}')
    res = r.get(NotificationURL, headers=headers)
    try:
        success = True if json.loads(res.text)['data']['list'][0]['msg'] == {
            "num": 15, "over_num": 0, "type": 2, "msg": "每日登录奖励"} else False
    except IndexError:
        success = False
    if success:
        print(
            f'获取签到情况成功！当前签到情况为{json.loads(res.text)["data"]["list"][0]["msg"]}')
        print(f'完整返回体为：{res.text}')
    else:
        raise RunError(
            f"签到失败！请带着本次运行的所有log内容到 https://github.com/ElainaMoe/MHYY-AutoCheckin/issues 发起issue解决（或者自行解决）。签到出错，返回信息如下：{res.text}")
