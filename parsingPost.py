from collections import OrderedDict
from time import sleep

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
import random

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
DRIVE_LOCATION = '/app/.chromedriver/bin/chromedriver'  # 크롬 드라이버 설치 위치
CHROME_LOCATION = '/app/.apt/usr/bin/google-chrome'  # 크롬 실행파일 설치 위치
SITE_URL = "http://www.anyang.ac.kr/bbs/board.do?menuId=23&bsIdx=61&bcIdx=0"

#
cred = credentials.Certificate(JSON)
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ["databaseURL"]
})

# 파이어베이스 콘솔에서 얻어 온 API키를 넣어 줌
push_service = FCMNotification(api_key=APIKEY)

# 초기 셋팅
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
# UserAgent값을 바꿔줍시다! (headless 감지를 피하기 위해)
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
options.add_argument("lang=ko_KR")  # 한국어!
options.binary_location = CHROME_LOCATION
chrome_options = options

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


def activateBot(lastPostNum):
    print("-----------------------------------------------")
    driver = webdriver.Chrome(DRIVE_LOCATION, options=options)
    driver.get('about:blank')
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")

    count = 0
    while (True):
        takeSomeRest()
        try:
            driver.get(SITE_URL)
            driver.implicitly_wait(time_to_wait=5)
            takeSomeRest()
            html = driver.find_element_by_xpath('//*[@id="boardList"]/tbody')
            break;
        except:
            count = count + 1
            now = datetime.datetime.now()
            print("TIMED_OUT_ERROR(Occurrence Time): " + now.isoformat())
            if count == 5:
                sendMessage("Timeout error", "모니터링키워드", " ")
                print("The error message sent to developer")
                break;

    # 게시물 번호 가져오기
    for index in range(1, 10):
        try:
            path = 'tr[' + str(index) + ']/td[1]/span'
            html.find_element_by_xpath(path).text
        except:
            path = 'tr[' + str(index) + ']/td[1]'
            nowPostNum = html.find_element_by_xpath(path).text
            break

    newPost = int(nowPostNum) - int(lastPostNum)
    now = datetime.datetime.now()
    print("index: ", index)
    print("Date: " + now.isoformat())
    print("nowPostNum: " + nowPostNum)
    print("lastPostNum: " + lastPostNum)
    print("newPost: " + str(newPost))

    if newPost > 10 or newPost < 0:
        sendMessage("newPost error: " + str(newPost), "모니터링키워드", " ")
        return nowPostNum

    if newPost > 0:
        keywords = importSubscribedKeyword()

        # 키워드를 포함하는 게시물이 있는지 검사한다.
        for i in range(newPost):
            path = 'tr[' + str(index) + ']/td[2]/a'
            index = index + 1
            try:
                post = html.find_element_by_xpath(path).text
                href = html.find_element_by_xpath(path).get_attribute("href")
            except:
                sendMessage("path error", "모니터링키워드", " ")
                break

            print("[" + post + "]")
            for keyword in keywords:
                if keyword in post:
                    print(keyword, end=", ")
                    sendMessage(post, keyword, href)
    print("-----------------------------------------------")

    return nowPostNum

def takeSomeRest():
    rand_value = random.randint(1, 10)
    sleep(rand_value)

dir = db.reference().child("lastPostNum")
snapshot = dir.get()  # 가장 최근에 올라온 게시물 번호
for key, value in snapshot.items():
    lastPostNum = value

updateNum = activateBot(lastPostNum) # 크롤러 봇 실행
if abs(int(updateNum) - int(lastPostNum)) > 10: # 갑자기 너무 많은 공지가 올라온다면
    sendMessage("postNum error", "모니터링키워드", " ")
elif updateNum != lastPostNum: # 새로 올라온 게시물이 있다면 업데이트
    dir.update({"lastPostNum": updateNum})