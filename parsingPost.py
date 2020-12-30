from selenium import webdriver
from time import sleep
import datetime
import time
from pyfcm import FCMNotification

APIKEY = "Your API KEY"
SITE_URL = "The site URL you want"
DRIVE_LOCATION = "The location of the drive you downloaded"
XPATH = 'The XPATH where the title of the post is located'

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
    
    data_message = {
        "body": "공지 알림",
        "title": title
    }

    # newPost 토픽을 구독한 사용자에게만 알림 전송
    result = push_service.notify_topic_subscribers(topic_name="newPost", data_message=data_message)

    # 토큰 값을 지정해서 한 기기에만 푸시알림을 보낼거면 이걸로
    # result = push_service.single_device_data_message(registration_id=registration_id, data_message=data_message)
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
            sleep(1)

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
    sleep(60 * 60)
