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


    # 페이지 소스를 BeautifulSoup을 사용하여 저장
    html_source_updated = browser.page_source
    soup = BeautifulSoup(html_source_updated, 'html.parser')

    # 점포 정보
    store_name = soup.find("h6").text.strip()
    store_address_full = soup.select_one(".shopArea_info dd").get_text(separator="\n").strip()
    store_address = store_address_full.split("\n")[0].strip()
    store_desc = soup.find(class_="asm_stitle").p.text.strip()
    store_phone = soup.find("dt", string="전화번호").find_next_sibling("dd").text.strip()
    store_parking = soup.find("dt", string="주차정보").find_next_sibling("dd").text.strip()
    store_directions = soup.find("dt", string="오시는 길").find_next_sibling("dd").text.strip()

    # 서비스 이미지 URL 리스트 추출
    service_section = soup.find("dt", string="서비스").find_next_sibling("dd")
    store_services = [
        f"https:{img['src']}" for img in service_section.find_all("img")
    ]

    # 위치 및 시설 이미지 URL 리스트 추출
    facility_section = soup.find("dt", string="위치 및 시설").find_next_sibling("dd")
    store_facilities = [
        f"https:{img['src']}" for img in facility_section.find_all("img")
    ]

    # 이미지 URL 리스트 추출
    image_urls = [
        f"https:{img['src']}" for img in soup.select(".shopArea_left .s_img li img")
    ]

    # data-type="C" 영업시간 보기
    # data-type="R" 리저브존 영업시간 보기
    # data-type="O" Delivers 영업시간 보기
    # data-type="D" Drive Thru 영업시간 보기
    # data-type="P" 펫 존 영업시간 보기
    # data-type="W" Walk-Thru 영업시간 보기

    # 영업 시간 처리
    store_hours = []
    hours_sections = soup.select(".date_time dl")
    for dl in hours_sections:
        dt_tags = dl.select("dt")
        dd_tags = dl.select("dd")
        store_hours.extend([
            ' '.join(f"{dt.text} {dd.text}".split()) for dt, dd in zip(dt_tags, dd_tags)
        ])
    
    # 추출한 정보를 저장
    details_data = {
        "name": store_name,
        "address": store_address,
        "phone": store_phone,
        "description": store_desc,
        "parking": store_parking,
        "directions": store_directions,
        "services": store_services,
        "facilities": store_facilities,
        "image_urls": image_urls,
        "hours": store_hours, 
    }

    # seoul 폴더 안에 JSON 파일 저장
    output_file_path = os.path.join(base_folder_path, f"seoul_{current_date}.json")
    with open(output_file_path, "w", encoding="utf-8") as json_file:
        json.dump(details_data, json_file, ensure_ascii=False, indent=4)

    print(f"데이터가 {output_file_path}에 저장되었습니다.")

except TimeoutException:
    print("페이지 로드 실패")

finally:
    browser.quit()