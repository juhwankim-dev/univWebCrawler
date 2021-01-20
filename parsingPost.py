from collections import OrderedDict

from selenium import webdriver
import datetime
from pyfcm import FCMNotification
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import inko
myInko = inko.Inko()
import os
import json

# Firebase database 인증을 위해 ... json 파일을 heroku에 업로드할 수 없기 때문
cred_json = OrderedDict()
cred_json["type"] = os.environ["type"]
cred_json["project_id"] = os.environ["project_id"]
cred_json["private_key_id"] = os.environ["private_key_id"]
cred_json["private_key"] = os.environ["private_key"]
cred_json["client_email"] = os.environ["client_email"]
cred_json["client_id"] = os.environ["client_id"]
cred_json["auth_uri"] = os.environ["auth_uri"]
cred_json["token_uri"] = os.environ["token_uri"]
cred_json["auth_provider_x509_cert_url"] = os.environ["auth_provider_x509_cert_url"]
cred_json["client_x509_cert_url"] = os.environ["client_x509_cert_url"]
JSON = json.dumps(cred_json)
JSON = json.loads(JSON)

# 링크, 키값 등
APIKEY = os.environ["APIKEY"]
DRIVE_LOCATION = '/app/.chromedriver/bin/chromedriver'
SITE_URL = "http://www.anyang.ac.kr/bbs/board.do?menuId=23&bsIdx=61&bcIdx=20"
XPATH = '//*[@id="boardList"]/tbody/tr[6]/td[1]' # 가장 최근에 올라온 게시글의 번호

#
cred = credentials.Certificate(JSON)
firebase_admin.initialize_app(cred,{
    'databaseURL' : os.environ["databaseURL"]
})

# 파이어베이스 콘솔에서 얻어 온 API키를 넣어 줌
push_service = FCMNotification(api_key=APIKEY)

#초기 셋팅
options = webdriver.ChromeOptions()
options.add_argument('headless')
chrome_options = options

def importSubscribedKeyword():
    keywords = []
    dir = db.reference().child("keywords")
    snapshot = dir.get()
    for key, value in snapshot.items():
        keywords.append(key)

    return keywords

def sendMessage(title, keyword):
    data_message = {
        "body": "공지 알림",
        "title": title
    }

    # 한글은 키워드로 설정할 수 없다. 한영변환.
    keyword = myInko.ko2en(keyword)
    # 구독한 사용자에게만 알림 전송
    result = push_service.notify_topic_subscribers(topic_name=keyword, data_message=data_message)
    print(result)

def activateBot(lastPostNum) :
    driver = webdriver.Chrome(DRIVE_LOCATION, options=options)
    while (True):
        try:
            driver.get(SITE_URL)
            driver.implicitly_wait(time_to_wait=5)
            break;
        except:
            now = datetime.datetime.now()
            print(now.isoformat())

    keywords = importSubscribedKeyword()

    element = driver.find_element_by_xpath(XPATH)
    nowPostNum = element.text
    newPost = int(nowPostNum) - int(lastPostNum)

    if(newPost > 0):
        for i in range (newPost):
            path1 = '//*[@id="boardList"]/tbody/tr['
            path2 = ']/td[2]/a'
            fullPath = path1 + str(i+5) + path2
            post = driver.find_element_by_xpath(fullPath)
            for keyword in keywords:
                if keyword in post.text:
                    sendMessage(post.text, keyword)

    return nowPostNum

dir = db.reference().child("lastPostNum")
lastPostNum = dir.get() # 가장 최근에 올라온 게시물 번호

# update lastPostNum
nowPostNum = activateBot(lastPostNum)
dir.update({"lastPostNum": nowPostNum})