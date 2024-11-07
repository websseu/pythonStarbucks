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
import json

# 현재 날짜를 문자열로 저장
current_date = datetime.now().strftime("%Y-%m-%d")

# location 폴더 생성
base_folder_path = os.path.join("details", "seoul")
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
# wait = WebDriverWait(browser, 10)
# browser.get("https://www.starbucks.co.kr/store/store_map.do")
# time.sleep(10)

# 클릭 및 이동
browser.find_element(By.CSS_SELECTOR, "#container > div > form > fieldset > div > section > article.find_store_cont > article > header.loca_search > h3 > a").click()
time.sleep(5) # 지역검색
browser.find_element(By.CSS_SELECTOR, ".loca_step1_cont .sido_arae_box li:nth-child(9)").click()
time.sleep(5) # 시도 선택
browser.find_element(By.CSS_SELECTOR, "#mCSB_2_container > ul > li:nth-child(1) > a").click()
time.sleep(5) # 전체 선택

# 전체 점포 리스트 가져오기
stores = browser.find_elements(By.CSS_SELECTOR, ".quickSearchResultBoxSidoGugun .quickResultLstCon")
store_data_list = []

# 점포를 하나씩 클릭
for store in stores:
    # 점포 타이틀을 클릭 
    browser.execute_script("arguments[0].click();", store)
    time.sleep(5)

    # 점포 이름과 주소 추출
    store_name = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop header").text.strip()
    store_address = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop .addr").text.strip()

    # 점포 상세 정보 클릭
    detail_button = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop .btn_marker_detail")
    browser.execute_script("arguments[0].click();", detail_button)
    time.sleep(5) 

    # 상세 정보 페이지의 HTML 가져오기
    detail_page_html = browser.page_source
    soup = BeautifulSoup(detail_page_html, 'html.parser')

    # 필요한 정보 가져오기
    operation_hours = extract_info_by_label(soup, "영업시간 보기", "영업시간 정보 없음")
    image_urls = ['https:' + img['src'] if not img['src'].startswith(('http:', 'https:')) else img['src'] for img in soup.select('.s_img img')]
    phone_number = extract_info_by_label(soup, "전화번호")
    parking_info = extract_info_by_label(soup, "주차정보")
    directions = extract_info_by_label(soup, "오시는 길")
    description = soup.select_one('.asm_stitle p').get_text(strip=True) if soup.select_one('.asm_stitle p') else "설명 없음"
    type_images = extract_images_by_label(soup, "타입")
    service_images = extract_images_by_label(soup, "서비스")

    # 추출한 정보를 저장
    store_info = {
        "name": store_name,
        "address": store_address,
        "image_urls": image_urls,
        "operation_hours": operation_hours,
        "phone_number": phone_number,
        "parking_info": parking_info,
        "directions": directions,
        "description": description,
        "type_images": type_images,
        "service_images": service_images
    }

    # 전체 점포 리스트에 추가
    store_data_list.append(store_info)

    # 점포 상세 정보 닫기 버튼
    detail_button = browser.find_element(By.CSS_SELECTOR, ".btn_pop_close a")
    browser.execute_script("arguments[0].click();", detail_button)
    time.sleep(5) 

# 결과 출력
for store_info in store_data_list:
    print(store_info)

# JSON 파일 구조화
today = datetime.now().strftime('%Y%m%d')
final_data = {
    "kind": "한국스타벅스",
    "data": today,
    "etag": f"we820403{today}",
    "location": "강원도",
    "count": len(store_data_list),
    "item": store_data_list
}

# JSON 파일로 저장
filename = f'starbucks_gangwon_detail_{today}.json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)

print(f'JSON 파일 저장 완료: {filename}')

# 브라우저 닫기
browser.quit()