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
DRIVE_LOCATION = '/app/.chromedriver/bin/chromedriver' # 크롬 드라이버 설치 위치
CHROME_LOCATION = '/app/.apt/usr/bin/google-chrome' # 크롬 실행파일 설치 위치
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
options.binary_location = CHROME_LOCATION
chrome_options = options

def importSubscribedKeyword():
    keywords = []
    dir = db.reference().child("keywords")
    snapshot = dir.get()
    for key, value in snapshot.items():
        # 키워드 조회하는 김에 구독자 수가 1이하 인거 삭제
        if(int(value) < 1):
            db.reference().child("keywords").child(key).delete()
            print("[", key, "]", "가 삭제되었습니다: ", value)

        else:
            keywords.append(key)

    return keywords

def sendMessage(title, keyword, url):
    data_message = {
        "url": url,
        "title": title
    }

    # 한글은 키워드로 설정할 수 없다. 한영변환.
    keyword = myInko.ko2en(keyword)
    # 구독한 사용자에게만 알림 전송
    result = push_service.notify_topic_subscribers(topic_name=keyword, data_message=data_message)
    print("\n", result)

def activateBot(lastPostNum) :
    print("-----------------------------------------------")
    driver = webdriver.Chrome(DRIVE_LOCATION, options=options)
    while (True):
        try:
            driver.get(SITE_URL)
            driver.implicitly_wait(time_to_wait=5)
            break;
        except:
            now = datetime.datetime.now()
            print("TIMED_OUT_ERROR(Occurrence Time): " + now.isoformat())

    keywords = importSubscribedKeyword()

    element = driver.find_element_by_xpath(XPATH)
    nowPostNum = element.text
    newPost = int(nowPostNum) - int(lastPostNum)
    now = datetime.datetime.now()
    print("Date: " + now.isoformat())
    print("nowPostNum: " + nowPostNum)
    print("lastPostNum: " + lastPostNum)
    print("newPost: " + str(newPost))

    index = 1
    path1 = '//*[@id="boardList"]/tbody/tr['
    path2 = ']/td[1]/span'

    if (newPost > 0):
        # 공지사항 게시물이 몇개인지 알아낸다 (건너 뛰기 위해서)
        while (True):
            fullPath = path1 + str(index) + path2
            try:
                postNumber = driver.find_element_by_xpath(fullPath).text
                if (postNumber == '[공지]'):
                    index = index + 1
            except:
                break

        # 키워드를 포함하는 게시물이 있는지 검사한다.
        for i in range(newPost):
            path1 = '//*[@id="boardList"]/tbody/tr['
            path2 = ']/td[2]/a'
            fullPath = path1 + str(index + i) + path2
            post = driver.find_element_by_xpath(fullPath)
            print("[" + post.text + "]")
            for keyword in keywords:
                if keyword in post.text:
                    print(keyword, end=", ")
                    sendMessage(post.text, keyword, post.get_attribute("href"))
    print("-----------------------------------------------")

    return nowPostNum

dir = db.reference().child("lastPostNum")
snapshot = dir.get() # 가장 최근에 올라온 게시물 번호
for key, value in snapshot.items():
    lastPostNum = value

nowPostNum = activateBot(lastPostNum) # 크롤러 봇 실행
if(nowPostNum != lastPostNum): # 새로 올라온 게시물이 있다면 업데이트
    dir.update({"lastPostNum": nowPostNum})