#Delete Blacklist Post- Made by Dangfer
#功能：自动删除黑名单用户在指定贴吧的帖子和回帖
#第一次使用请填好你的BDUSS, fid, tbs

import requests
import json
import hashlib
import time
from urllib.parse import urlencode

def GetThread():
    global fid, lastThread, paramProfile, uidlist
    for uid in uidlist: #遍历黑名单
        paramProfile['uid'] = uid
        paramProfile['sign'] = sign(paramProfile)
        url = 'http://c.tieba.baidu.com/c/u/user/profile?' + urlencode(paramProfile)
        response = requests.get(url).json()
        tmp = 0
        for i in response['post_list']:
            s = i['forum_id']
            if s != fid: #没有在目标贴吧发帖
                continue
            t = int(i['create_time']) #获取发帖时间
            if t > lastThread[uid]: #发了新贴
                if t > tmp: #仅更新1次
                    tmp = t
                print('发帖：', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t)), ' uid:', uid)
                DeleteThread(i['thread_id'])
        if tmp != 0: #发了新帖
            lastThread[uid] = tmp
    return

def GetRepost():
    global fid, lastRepost, paramRepost, uidlist
    for uid in uidlist:
        paramRepost['uid'] = uid
        paramRepost['sign'] = sign(paramRepost)
        url = 'http://c.tieba.baidu.com/c/u/feed/userpost?' + urlencode(paramRepost)
        response = requests.get(url).json() #这里json中的time和id是int类型的
        tmp = 0
        for i in response['post_list']:
            s = i['forum_id']
            if s != int(fid): #没有在目标贴吧回帖
                continue
            t = i['create_time']
            if t > lastRepost[uid]: #回了新帖
                if t > tmp:
                    tmp = t
                print('回帖：', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t)), ' uid:', uid)
                DeleteRepost(str(i['post_id']), str(i['thread_id']))
        if tmp != 0: #回了新帖
            lastRepost[uid] = tmp
    return

def DeleteThread(z):
    global paramDT
    paramDT['z'] = z
    paramDT['sign'] = sign(paramDT)
    url = 'http://c.tieba.baidu.com/c/c/bawu/delthread?' + urlencode(paramDT)
    response = requests.get(url).json()
    if response['error_code'] == '0':
        print('帖子删除成功')
    else:
        print('操作失败，错误信息：', response['error_msg'])
    return

def DeleteRepost(pid, z):
    global paramDP
    paramDP['pid'] = pid
    paramDP['z'] = z
    paramDP['sign'] = sign(paramDP)
    url = 'http://c.tieba.baidu.com/c/c/bawu/delpost?' + urlencode(paramDP)
    response = requests.get(url).json()
    if response['error_code'] == '0':
        print('回帖删除成功')
    else:
        print('操作失败，错误信息：', response['error_msg'])
    return

def sign(src):
    s = ''
    if 'sign' in src: #重新签名
        del src['sign']
    #生成报文
    for k, v in src.items():
        s += k + '=' + v
    s += 'tiebaclient!!!'
    return hashlib.md5(s.encode()).hexdigest()

def initdict(uidlist):
    d = {}
    for uid in uidlist:
        d[uid] = 0
    return d

#黑名单uid列表
uidlist = ['黑名单用户uid']
lastRepost = lastThread = initdict(uidlist) #初始化字典
#仅获取profile的前三个帖子, 若读取发帖会一次性读60个
paramProfile = {'_client_type': '2',
                '_client_version': '7.2.0.0'}
#获取回帖
paramRepost = {'rn': '20'}
#删除帖子
#！----------重要----------！
#BDUSS请打开浏览器的Cookies找到其中的BDUSS
#fid请用 http://tieba.baidu.com/f/commit/share/fnameShareApi?ie=utf-8&fname=吧名 获取
#tbs请用 http://tieba.baidu.com/dc/common/tbs 获取
BDUSS = '你的BDUSS'
tbs = '你的tbs'
fid = '目标贴吧的fid'

paramDT = {'BDUSS': BDUSS,
           'fid': fid,
           'tbs': tbs,
           'z': ''}
paramDP = {'BDUSS': BDUSS,
           'fid': fid,
           'pid': '',
           'tbs': tbs,
           'z': ''}

while True:
    GetThread()
    GetRepost()
    time.sleep(600) #每10分钟获取一次消息
