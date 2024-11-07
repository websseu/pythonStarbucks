from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
import re
import json

# 현재 날짜를 문자열로 저장
current_date = datetime.now().strftime("%Y-%m-%d")

location_name_mapping = {
    "강남구": "gangnamgu",
    "강동구": "gangdonggu",
    "강북구": "gangbukgu",
    "강서구": "gangseogu",
    "관악구": "gwanakgu",
    "광진구": "gwangjingu",
    "구로구": "gurogu",
    "금천구": "geumcheongu",
    "노원구": "nowongu",
    "도봉구": "dobonggu",
    "동대문구": "dongdaemungu",
    "동작구": "dongjakgu",
    "마포구": "mapogu",
    "서대문구": "seodaemungu",
    "서초구": "seochogu",
    "성동구": "seongdonggu",
    "성북구": "seongbukgu",
    "송파구": "songpagu",
    "양천구": "yangcheongu",
    "영등포구": "yeongdeungpogu",
    "용산구": "yongsangu",
    "은평구": "eunpyeonggu",
    "종로구": "jongnogu",
    "중구": "junggu",
    "중랑구": "jungnanggu"
}

# location 폴더 생성
base_folder_path = "details"
os.makedirs(base_folder_path, exist_ok=True)

# 웹드라이버 설정 및 페이지 로드
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage") 
options.add_argument("--disable-gpu")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")
options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 2,  # 위치 권한 차단
    "profile.default_content_setting_values.notifications": 2  # 알림 차단
})
browser = webdriver.Chrome(options=options)
browser.get("https://www.starbucks.co.kr/store/store_map.do?disp=locale")

# 웹드라이버 설정(로컬)
# browser = webdriver.Chrome()
# browser.get("https://www.starbucks.co.kr/store/store_map.do?disp=locale")

try:
    # 페이지가 완전히 로드될 때까지 대기
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "store_map_layer_cont"))
    )
    print("페이지가 완전히 로드되었습니다.")
    time.sleep(5)

    # 서울을 클릭
    try:
        location_button = browser.find_element(By.CSS_SELECTOR, f".sido_arae_box li:nth-child(1) a")
        location_name_kor = location_button.text  # 한글 지역명
        location_button.click()
        print(f"{location_name_kor} 버튼을 클릭했습니다.")
        time.sleep(5)
    except NoSuchElementException:
        print("전체 버튼을 찾을 수 없습니다.")

    # 전체 버튼 클릭
    try:
        all_button = browser.find_element(By.CSS_SELECTOR, ".gugun_arae_box li:nth-child(1) a")
        all_button.click()
        print("전체 버튼을 클릭했습니다.")
        time.sleep(5)
    except NoSuchElementException:
        print("전체 버튼을 찾을 수 없습니다.")
    
    # 리스트 목록을 클릭
    try:
        list_button = browser.find_element(By.CSS_SELECTOR, ".quickSearchResultBoxSidoGugun li:nth-child(1)")
        list_button.click()
        print("리스트 버튼을 클릭했습니다.")
        time.sleep(5)
    except NoSuchElementException:
        print("리스트 버튼을 찾을 수 없습니다.")
    
    # 상세 정보 보기 버튼 클릭
    try:
        list_button = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop_inner .btn_marker_detail")
        list_button.click()
        print("상세 정보 보기 버튼을 클릭했습니다.")
        time.sleep(5)
    except NoSuchElementException:
        print("상세 정보 보기 버튼을 찾을 수 없습니다.")

except TimeoutException:
    print("페이지 로드 실패")

finally:
    browser.quit()