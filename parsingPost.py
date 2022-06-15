from collections import OrderedDict
from time import sleep
from bs4 import BeautifulSoup as bs

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
REQUEST_URL = "http://www.anyang.ac.kr/bbs/board.do?menuId=23&bsIdx=61&bcIdx=0"

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

def sendErrorMessage(message):
    sendMessage(datetime.datetime.now().isoformat() + ", " + message, "모니터링키워드", " ")

def activateBot():
    baseUrl = "https://www.anyang.ac.kr/main/communication/notice.do"

    now = datetime.datetime.now()
    print("Date: " + now.isoformat())

    try:
        response = requests.get(REQUEST_URL)
        soup = bs(response.text, "html.parser")
    except Exception as e:
        sendErrorMessage("HTTP 요청 실패")
        return

    headerSize = 0
    for i in range(30):
        try:
            soup.select(".b-notice>a[href]")[i]['href']
            headerSize = headerSize + 1
        except:
            print(str(i) + "번째에서 header for문 종료")
            break

    titles = []
    noticeIndexes = []
    webLink = []
    print("header size: str(headerSize)")
    for i in range(headerSize, 30):
        try:
            notice = soup.select("div.b-title-box>a[href]")
            link = notice[i]['href']
            title = notice[i].text.strip()

            if(link.find("articleNo") == -1):
                sendErrorMessage("공지 리스트 api 주소 확인 필요")
                return

            # articleNo의 'a'에 해당하는 인덱스에 "articleNo=" 문자열의 길이인 10을 더한다.
            startIndex = link.find("articleNo") + 10
            endIndex = link.find('&', startIndex)

            titles.append(title)
            noticeIndexes.append(link[startIndex:endIndex])
            webLink.append(link)
            print(link + " / " + title)
        except:
            print(str(i) + "번째에서 공지사항 for문 종료")
            break

    keywords = importSubscribedKeyword()
    newNoticeIndexes = ""
    lastestIndex = previousPostNumber[2:previousPostNumber.find(',', 2)]
    print("noticeIndexes:")
    print(noticeIndexes)
    for i in range(len(noticeIndexes)):
        try:
            newNoticeIndexes = newNoticeIndexes + ", " + noticeIndexes[i]
            if not noticeIndexes[i] in previousPostNumber and int(noticeIndexes[i]) > int(
                    lastestIndex):  # 최근 10개 게시물중 이 번호가 아닌게 있으면 = 새로운 게시물이면
                print("title: " + titles[i])
                print("contain keyword:", end=" ")

                for keyword in keywords:
                    if keyword in titles[i]:
                        print(keyword, end=", ")
                        sendMessage(titles[i], "모니터링키워드", baseUrl + webLink[i])
                print()
        except:
            sendErrorMessage("noticeIndexes 에러")
            return previousPostNumber

    return newNoticeIndexes

def takeSomeRest():
    rand_value = random.randint(1, 10)
    sleep(rand_value)

now = datetime.datetime.today().weekday()
time = datetime.datetime.now().strftime('%H')
if 0 <= now <= 4 and 9 <= int(time) <= 19: # 월~금, 9시~7시 사이에만 작동
    print("-----------------------------------------------")
    previousPostNumber = importPreviousPost()
    newNoticeIndexes = activateBot()
    if newNoticeIndexes is not None and newNoticeIndexes != "" and previousPostNumber != newNoticeIndexes:
        dir = db.reference().child("previousPosts")
        dir.update({"previousPosts": newNoticeIndexes})
        print("\n" + "newPost: " + newNoticeIndexes)
    print("-----------------------------------------------")
