from collections import OrderedDict
from time import sleep

import datetime
from pyfcm import FCMNotification
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import inko
myInko = inko.Inko()
import os
import json
import random
import requests

# Firebase database 인증을 위해 ... json 파일을 heroku에 업로드할 수 없기 때문
cred_json = OrderedDict()
cred_json["type"] = os.environ["type"]
cred_json["project_id"] = os.environ["project_id"]
cred_json["private_key_id"] = os.environ["private_key_id"]
cred_json["private_key"] = os.environ["private_key"].replace('\\n', '\n')
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
SITE_URL = "http://www.anyang.ac.kr/bbs/board.do?menuId=23&bsIdx=61&bcIdx=0"

#
cred = credentials.Certificate(JSON)
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ["databaseURL"]
})

# 파이어베이스 콘솔에서 얻어 온 API키를 넣어 줌
push_service = FCMNotification(api_key=APIKEY)

def importSubscribedKeyword():
    keywords = []
    dir = db.reference().child("keywords")
    snapshot = dir.get()
    for key, value in snapshot.items():
        # 키워드 조회하는 김에 구독자 수가 1이하 인거 삭제
        if int(value) < 1:
            db.reference().child("keywords").child(key).delete()
            print("[", key, "]", "가 삭제되었습니다: ", value)

        else:
            keywords.append(key)

    return keywords

def importPreviousPost():
    dir = db.reference().child("previousPosts")
    snapshot = dir.get()
    for key, value in snapshot.items():
        return value

def sendMessage(title, keyword, url):
    data_message = {
        "url": url,
        "title": title
    }

    # 한글은 키워드로 설정할 수 없다. 한영변환.
    keyword = myInko.ko2en(keyword)
    # 구독한 사용자에게만 알림 전송
    push_service.notify_topic_subscribers(topic_name=keyword, data_message=data_message)

def activateBot() :
    baseUrl = "http://www.anyang.ac.kr/bbs/boardView.do?bsIdx=61&menuId=23&bcIdx=20&bIdx="
    datas = {"menuId": "23", "bsIdx": "61", "bcIdx": "0", "page": "1"}

    now = datetime.datetime.now()
    print("Date: " + now.isoformat())
    response = requests.post("http://www.anyang.ac.kr/bbs/ajax/boardList.do", data=datas)

    responseJson = response.json()
    resultList = responseJson["resultList"]

    keywords = importSubscribedKeyword()
    subject = []
    bidx = []

    # POST 요청 보내서 값 받아오기
    for notice in resultList:
        subject.append(notice["SUBJECT"])
        bidx.append(notice["B_IDX"])

    newPostNumber = ""
    for i in range(10):
        newPostNumber = newPostNumber + ", " + bidx[i]
        if not bidx[i] in previousPostNumber:  # 최근 10개 게시물중 이 번호가 아닌게 있으면 = 새로운 게시물이면
            print("title: [" + subject[i] + "]")
            print("contain keyword:", end=" ")

            for keyword in keywords:
                if keyword in subject[i]:
                    print(keyword, end=", ")
                    sendMessage(subject[i], keyword, baseUrl + bidx[i])
            print()

    return newPostNumber

def takeSomeRest():
    rand_value = random.randint(1, 10)
    sleep(rand_value)

now = datetime.datetime.today().weekday()
time = datetime.datetime.now().strftime('%H')
if 0 <= now <= 4 and 9 <= int(time) <= 18: # 월~금, 9시~6시 사이에만 작동
    print("-----------------------------------------------")
    previousPostNumber = importPreviousPost()
    newPostNumber = activateBot()
    if previousPostNumber != newPostNumber:
        dir = db.reference().child("previousPosts")
        dir.update({"previousPosts": newPostNumber})
        print("\n" + "newPost: " + newPostNumber)
    print("-----------------------------------------------")
