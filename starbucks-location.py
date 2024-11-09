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

# 한글 지역명과 영문 지역명 매핑
location_name_mapping = {
    "서울": "seoul",
    "부산": "busan",
    "대구": "daegu",
    "인천": "incheon",
    "광주": "gwangju",
    "대전": "daejeon",
    "울산": "ulsan",
    "경기": "gyeonggi",
    "강원": "gangwon",
    "충북": "chungbuk",
    "충남": "chungnam",
    "전북": "jeolbuk",
    "전남": "jeolnam",
    "경북": "gyeongbuk",
    "경남": "gyeongnam",
    "제주": "jeju"
}

# location 폴더 생성
base_folder_path = "location"
os.makedirs(base_folder_path, exist_ok=True)

# 웹드라이버 설정 및 페이지 로드
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")  # 메모리 부족 문제 방지
options.add_argument("--disable-gpu")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")  # 알림 비활성화
options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 2,  # 위치 권한 차단
    "profile.default_content_setting_values.notifications": 2  # 알림 차단
})
browser = webdriver.Chrome(options=options)

try:
    browser.get("https://www.starbucks.co.kr/store/store_map.do?disp=locale")

    # 페이지가 완전히 로드될 때까지 대기
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "store_map_layer_cont"))
    )
    print("페이지가 완전히 로드되었습니다.")
    time.sleep(5)

    # 16개 지역을 순회하며 데이터 수집
    for i in range(1, 17):  # 1부터 16까지 순회

        try:
            location_button = browser.find_element(By.CSS_SELECTOR, f".sido_arae_box li:nth-child({i}) a")
            location_name_kor = location_button.text  # 한글 지역명
            location_button.click()
            print(f"{location_name_kor} 버튼을 클릭했습니다.")
            
            # 한글 지역명을 영문으로 변환
            location_name_eng = location_name_mapping.get(location_name_kor, location_name_kor)  # 매핑되지 않은 경우 원래 이름 사용
            time.sleep(3)

            # 전체 버튼 클릭
            try:
                all_button = browser.find_element(By.CSS_SELECTOR, ".gugun_arae_box li:nth-child(1) a")
                browser.execute_script("arguments[0].click();", all_button)
                print("전체 버튼을 클릭했습니다.")
                time.sleep(3)

                # .quickSearchResultBoxSidoGugun 안에 있는 요소들이 나타날 때까지 대기
                WebDriverWait(browser, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".quickSearchResultBoxSidoGugun li strong"))
                )

                # 페이지 소스를 BeautifulSoup을 사용하여 저장
                html_source_updated = browser.page_source
                soup = BeautifulSoup(html_source_updated, 'html.parser')

                # 전체 데이터를 저장할 변수
                store_data = []

                # 데이터 수집
                stores = soup.select(".quickSearchResultBoxSidoGugun li.quickResultLstCon")

                for store in stores:
                    # 이름, 주소, 위도, 경도 추출
                    name = store.get("data-name")
                    address = store.select_one(".result_details").text.strip() if store.select_one(".result_details") else None
                    
                    # 주소에서 전화번호 형식을 제거
                    if address:
                        address = re.sub(r'\d{4}-\d{4}', '', address).strip()  # 전화번호 패턴 제거
                    
                    latitude = store.get("data-lat")
                    longitude = store.get("data-long")

                    # 수집된 정보를 딕셔너리에 저장
                    store_data.append({
                        "name": name,
                        "address": address,
                        "latitude": latitude,
                        "longitude": longitude
                    })

                # 최종 JSON 구조 정의
                final_data = {
                    "location": location_name_eng,
                    "count": len(store_data),
                    "date": current_date,
                    "item": store_data
                }

                # location 폴더에 영문 이름으로 폴더 생성
                location_folder_path = os.path.join(base_folder_path, location_name_eng)
                os.makedirs(location_folder_path, exist_ok=True)

                # 데이터 저장
                file_name = f"{location_folder_path}/{location_name_eng}_{current_date}.json"
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(final_data, f, ensure_ascii=False, indent=4)
                    print(f"{location_name_eng} 데이터가 '{file_name}' 파일에 저장되었습니다.")
                
                # "지역 검색" 버튼 클릭
                try:
                    localSearch = browser.find_element(By.CSS_SELECTOR, "#container > div > form > fieldset > div > section > article.find_store_cont > article > header.loca_search > h3 > a")
                    browser.execute_script("arguments[0].click();", localSearch)
                    print("지역 검색 버튼을 클릭했습니다.")
                    time.sleep(3)
                except Exception as e:
                    print("지역 검색 버튼을 클릭하는 데 실패했습니다:", e)
                    browser.quit()
                    exit()

            except NoSuchElementException:
                print("전체 버튼을 찾을 수 없습니다.")

        except NoSuchElementException:
            print(f"{location_name_eng} 버튼을 찾을 수 없습니다.")

except TimeoutException:
    print("페이지 로드 실패")
    
finally:
    # 브라우저 종료
    browser.quit()
