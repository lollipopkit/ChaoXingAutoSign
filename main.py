# -*- coding:utf-8 -*-
import multiprocessing
import random
from datetime import datetime, time
from time import sleep
import os
from urllib import parse
import json
import requests

# debug为真，则全天运行本脚本，方便调试。debug为假，则仅上课时运行
debug = False

# ！！！请填写下面6个参数
# 填写用户名和密码，以便登录
username = ''
password = ''
# uid为用户id
uid = ''
# 此三项为签到参数，经纬度和真实姓名
latitude = '-1'
longitude = '-1'
name = ''
clientip = ''
signuseragent = ''

useragent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ChaoXingStudy/ChaoXingStudy_3_4.4.1_ios_phone_202004111750_39 (@Kalimdor)_4375872153618237766 ChaoXingStudy/ChaoXingStudy_3_4.4.1_ios_phone_202004111750_39 (@Kalimdor)_4375872153618237766'
cookie = ''
encode_name = parse.quote(name)
COOKIE_FILENAME = 'chaoxing_cookies'

# 第一节课
CLASS_ONE_START = time(7, 55)
CLASS_ONE_END = time(8, 15)
# 第二节课
CLASS_TWO_START = time(10, 0)
CLASS_TWO_END = time(10, 20)
# 第三节课
CLASS_THREE_START = time(13, 30)
CLASS_THREE_END = time(13, 50)
# 第四节课
CLASS_FOUR_START = time(15, 30)
CLASS_FOUR_END = time(15, 46)


def myprint(string):
    print(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + '  ' + string)


def getCookies():
    myprint('正在登录，获取新Cookie')
    if username and password:
        global cookie
        url = 'https://passport2-api.chaoxing.com/v11/loginregister'
        rdata = {'uname': username, 'code': password, }
        session = requests.session()
        cookie_jar = session.post(url=url, data=rdata, headers={'User-Agent': useragent}).cookies
        cookie_dict = requests.utils.dict_from_cookiejar(cookie_jar)
        cookie_str = ''
        for key in cookie_dict:
            cookie_str += key + '=' + cookie_dict[key] + '; '
        cookie = cookie_str
        if cookie_str:
            with open(COOKIE_FILENAME, 'w', encoding='utf-8')as file:
                file.write(cookie_str)
                myprint('获取Cookie成功')

    else:
        myprint('plz edit username and password in this python file')


if os.path.exists(COOKIE_FILENAME):
    with open(COOKIE_FILENAME, 'r', encoding='utf-8') as f:
        data = f.read().strip()
        if data:
            cookie = data
        else:
            getCookies()
else:
    getCookies()

# 初始化空数据
coursedata = []
activeList = []
course_index = 0
status = 0
status2 = 0
activates = []

header = {
    "Cookie": cookie,
    "User-Agent": useragent,
}


def signThread():
    while 1:
        def backClassData():
            global coursedata
            cdata = {}
            url = 'http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1'
            while not cdata:
                res = requests.get(url, headers=header)
                cdata = json.loads(res.content.decode('utf-8'))
                if not cdata:
                    getCookies()
                    continue
                if cdata['result'] != 1:
                    myprint("课程列表获取失败")
                    return 0
                for item in cdata['channelList']:
                    if "course" not in item['content']:
                        continue
                    pushdata = {'courseid': item['content']['course']['data'][0]['id'],
                                'name': item['content']['course']['data'][0]['name'],
                                'imageurl': item['content']['course']['data'][0]['imageurl'],
                                'classid': item['content']['id']}
                    coursedata.append(pushdata)
                myprint("课程获取成功\n")
                printCourseData()

        def printCourseData():
            global course_index
            for index, item in enumerate(coursedata):
                print(str(index + 1) + "." + item['name'])
            startSign()

        def taskActiveList(courseId, classId):
            global activeList
            url = 'https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId=' + str(
                courseId) + '&classId=' + str(classId) + '&uid=' + uid
            res = requests.get(url, headers=header)
            data_json = json.loads(res.text)
            activeList = data_json['activeList']
            for item in activeList:
                if "nameTwo" not in item:
                    continue
                if item['activeType'] == 2 and item['status'] == 1:
                    signurl = item['url']
                    aid = getVar(signurl)
                    if aid not in activates:
                        myprint("待签到活动 名称:%s 状态:%s 时间:%s " % (
                            item['nameOne'], item['nameTwo'], item['nameFour']))
                        sign(aid, uid, courseId)

        def getVar(url):
            var1 = url.split("&")
            for var in var1:
                var2 = var.split("=")
                if var2[0] == "activePrimaryId":
                    return var2[1]
            return "notfound"

        def sign(aid, uid, courseid):
            global status, activates
            url = 'https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId=' + aid + '&uid=' + uid + '&clientip=' + clientip + '&useragent=' + signuseragent + '&latitude=' + latitude + '&longitude=' + longitude + '&appType=15&fid=2378&objectId=bafc13f7a93ce7b8f745c913d58f1785&name=' + encode_name
            res = requests.get(url, headers=header)
            course_name = ''
            for item in coursedata:
                if item['courseid'] == courseid:
                    course_name = item['name']
            if res.text == "success":
                myprint(course_name + ": 签到成功！")
                activates.append(aid)
                status = 2
            elif res.text == '您已签到过了':
                myprint(course_name + ': 您已签到过了')
                activates.append(aid)
                status = 2
            else:
                myprint(course_name + '签到失败')
                activates.append(aid)

        def startSign():
            global status, status2
            status = 1
            status2 = 1
            while status != 0 and status2 != 0:
                while True:
                    print('\n')
                    for item in coursedata:
                        myprint('正在监听: ' + str(item['name']))
                        taskActiveList(item['courseid'], item['classid'])
                        sleep(3.7)
                        if status == 2:
                            sleep(60*10)
                    sleep(random.randint(37, 88))
            myprint("任务结束")
            printdata()

        backClassData()


def listenThread():
    myprint("主程序启动")

    child_process = None

    while True:
        current_time = datetime.now().time()
        if debug:
            running = True
        else:
            running = False

        if CLASS_ONE_START <= current_time <= CLASS_ONE_END or CLASS_TWO_START <= current_time <= CLASS_TWO_END or CLASS_THREE_START <= current_time <= CLASS_THREE_END or CLASS_FOUR_START <= current_time <= CLASS_FOUR_END:
            running = True

        if running and child_process is None:
            myprint("监听开始\n")
            child_process = multiprocessing.Process(target=signThread)
            child_process.start()

        if not running and child_process is not None:
            myprint("监听结束\n")
            child_process.terminate()
            child_process.join()
            child_process = None

        sleep(60)


if __name__ == '__main__':
    listenThread()

