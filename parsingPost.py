from selenium import webdriver
from time import sleep
import datetime
from pyfcm import FCMNotification
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import inko
myInko = inko.Inko()
import os

# 링크, 키값 등
APIKEY = os.environ["APIKEY"]
JSON_LOCATION = os.environ["JSON_LOCATION"]
SITE_URL = "http://www.anyang.ac.kr/bbs/board.do?menuId=23&bsIdx=61&bcIdx=20"
DRIVE_LOCATION = "C:\chromedriver\chromedriver.exe"
XPATH = '//*[@id="boardList"]/tbody/tr[6]/td[1]' # 가장 최근에 올라온 게시글의 번호

#
cred = credentials.Certificate(JSON_LOCATION)
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://pushnotification-6e716-default-rtdb.firebaseio.com/'
})

# 파이어베이스 콘솔에서 얻어 온 API키를 넣어 줌
push_service = FCMNotification(api_key=APIKEY)

numberFile = open('lastPostNum.txt', mode='wt', encoding='utf-8')
Log = open('Log.txt', mode='at', encoding='utf-8')

#초기 셋팅
options = webdriver.ChromeOptions()
options.add_argument('headless')
chrome_options = options
driver = webdriver.Chrome(DRIVE_LOCATION, options=options)
while(True):
    try:
        driver.get(SITE_URL)
        driver.implicitly_wait(time_to_wait=5)
        break;
    except:
        now = datetime.datetime.now()
        Log.write("TIMED_OUT_ERROR(Occurrence Time): " + now.isoformat() + "\n")

element = driver.find_element_by_xpath(XPATH)
lastPostNum = element.text  # 가장 최근에 올라온 게시물의 번호

numberFile.write(lastPostNum)
numberFile.close()
Log.close()
driver.close()

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

def activateBot(Log) :
    driver = webdriver.Chrome(DRIVE_LOCATION, options=options)
    while (True):
        try:
            driver.get(SITE_URL)
            driver.implicitly_wait(time_to_wait=5)
            break;
        except:
            now = datetime.datetime.now()
            Log.write("TIMED_OUT_ERROR(Occurrence Time): " + now.isoformat() + "\n")

    numberFile = open('lastPostNum.txt', mode='rt', encoding='utf-8')
    lastPostNum = numberFile.read()
    numberFile.close()

    keywords = importSubscribedKeyword()

    element = driver.find_element_by_xpath(XPATH)
    nowPostNum = element.text
    newPost = int(nowPostNum) - int(lastPostNum)

    # 로그 남기기
    now = datetime.datetime.now()
    Log.write("\nDate: " + now.isoformat() + "\n")
    Log.write("nowPostNum: " + nowPostNum + "\n")
    Log.write("lastPostNum: " + lastPostNum + "\n")
    Log.write("newPost: " + str(newPost))

    if(newPost > 0):
        for i in range (newPost):
            path1 = '//*[@id="boardList"]/tbody/tr['
            path2 = ']/td[2]/a'
            fullPath = path1 + str(i+5) + path2
            post = driver.find_element_by_xpath(fullPath)
            Log.write("\n" + post.text + "\n")
            for keyword in keywords:
                if keyword in post.text:
                    Log.write(keyword + ", ")
                    sendMessage(post.text, keyword)

    Log.write("\n--------------------------------------------")
    driver.close()
    return nowPostNum

    #nowTime = now.strftime("%H:%M:%S")
    #Log.write(("현재 시각: ", nowTime))
    #nowHour = now.strftime("%H")

while(True):
    Log = open('Log.txt', mode='at', encoding='utf-8')
    lastPostNum = activateBot(Log)
    numberFile = open('lastPostNum.txt', mode='wt', encoding='utf-8')
    numberFile.write(lastPostNum)
    numberFile.close()
    Log.close()
    # 1시간에 1번씩 검사
    sleep(60 * 60)