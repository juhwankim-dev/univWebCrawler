from selenium import webdriver
from time import sleep
import datetime
import time
from pyfcm import FCMNotification

APIKEY = ""
TOKEN = ""
SITE_URL = ""
DRIVE_LOCATION = ""
XPATH = ''

# 파이어베이스 콘솔에서 얻어 온 API키를 넣어 줌
push_service = FCMNotification(api_key=APIKEY)

##
options = webdriver.ChromeOptions()
options.add_argument('headless')
chrome_options=options
driver = webdriver.Chrome(DRIVE_LOCATION, chrome_options=options)
driver.get(SITE_URL)
driver.implicitly_wait(time_to_wait=5)

element = driver.find_element_by_xpath(XPATH)
lastPostNum = element.text # 가장 최근에 올라온 게시물의 번호
driver.close()
##

def sendMessage(title):
    registration_id = TOKEN

    data_message = {
        "body": "테스트 알림입니다.",
        "title": title
    }

    # data payload만 보내야 안드로이드 앱에서 백그라운드/포그라운드 두가지 상황에서 onMessageReceived()가 실행됨
    result = push_service.single_device_data_message(registration_id=registration_id, data_message=data_message)
    print(result)

def activateBot(lastPostNum) :
    driver = webdriver.Chrome(DRIVE_LOCATION, chrome_options=options)
    driver.get(SITE_URL)
    driver.implicitly_wait(time_to_wait=5)

    element = driver.find_element_by_xpath(XPATH)
    nowPostNum = element.text

    # 로그 남기기
    nowTime = now.strftime("%H:%M:%S")
    print("Log: ", nowTime, "에 크롤링을 실행하였습니다.")
    newPost = int(nowPostNum) - int(lastPostNum)
    print("nowPostNum: ", nowPostNum, " lastPostNum: ", lastPostNum, " newPost: ", newPost)

    if(newPost > 0):
        element = driver.find_elements_by_class_name("list_title")
        post_list_now = element

        for i in range (newPost):
            print(post_list_now[i+1].text)
            sendMessage(post_list_now[i+1].text)
            sleep(2)

    print("--------------------------------------------")
    driver.close()
    return nowPostNum

while(True):
    print("크롤러가 웹 페이지를 감시중입니다.")
    now = datetime.datetime.now()
    print("현재 날짜: ", now.isoformat())
    nowTime = now.strftime("%H:%M:%S")
    print("현재 시각: ", nowTime)
    nowHour = now.strftime("%H")
    print("--------------------------------------------")

    lastPostNum = activateBot(lastPostNum)
    # 1시간에 1번씩 검사
    sleep(60 * 1)



