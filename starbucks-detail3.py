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

# details 폴더 생성
base_folder_path = os.path.join("details")
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

# 웹드라이버 설정(로컬)
# browser = webdriver.Chrome()
# wait = WebDriverWait(browser, 10)
# time.sleep(10)

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
        
        except NoSuchElementException:
            print(f"{location_name_eng} 버튼을 찾을 수 없습니다.")
        
        # 전체 버튼 클릭
        try:
            all_button = browser.find_element(By.CSS_SELECTOR, ".gugun_arae_box li:nth-child(1) a")
            all_button.click()
            print("전체 버튼을 클릭했습니다.")
            time.sleep(3)

        except NoSuchElementException:
            print("전체 버튼을 찾을 수 없습니다.")
        
        # 전체 점포 리스트 가져오기
        stores = browser.find_elements(By.CSS_SELECTOR, ".quickSearchResultBoxSidoGugun .quickResultLstCon")

        # 모든 점포 데이터를 저장할 리스트
        store_data_list = []

        # 모든 점포에 대해 순차적으로 작업
        for index, store in enumerate(stores):
            browser.execute_script("arguments[0].click();", store)
            time.sleep(3)

            # 점포 이름과 주소 추출
            store_name = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop header").text.strip()
            store_address = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop .addr").text.strip()

            # "상세 정보 보기" 버튼 클릭
            detail_button = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop .btn_marker_detail")
            browser.execute_script("arguments[0].click();", detail_button)
            time.sleep(5) 
            print(f"상세 정보 보기 버튼을 클릭했습니다. ({index + 1}/{len(stores)})")

            # 상세 정보 페이지의 HTML 가져오기
            detail_page_html = browser.page_source
            soup = BeautifulSoup(detail_page_html, 'html.parser')

            # 각종 정보 추출
            store_description = soup.select_one(".shopArea_pop01 .asm_stitle p").text.strip() if soup.select_one(".shopArea_pop01 .asm_stitle p") else ""
            store_parking_info = soup.find("dt", string="주차정보").find_next_sibling("dd").text.strip() if soup.find("dt", string="주차정보") else ""
            store_directions = soup.find("dt", string="오시는 길").find_next_sibling("dd").text.strip() if soup.find("dt", string="오시는 길") else ""
            store_phone = soup.find("dt", string="전화번호").find_next_sibling("dd").text.strip() if soup.find("dt", string="전화번호") else ""

            # 서비스 이미지 URL 리스트 추출
            service_section = soup.find("dt", string="서비스")
            store_services = [
                f"https:{img['src']}" for img in service_section.find_next_sibling("dd").find_all("img")
            ] if service_section and service_section.find_next_sibling("dd") else []

            # 위치 및 시설 이미지 URL 리스트 추출
            facility_section = soup.find("dt", string="위치 및 시설")
            store_facilities = [
                f"https:{img['src']}" for img in facility_section.find_next_sibling("dd").find_all("img")
            ] if facility_section and facility_section.find_next_sibling("dd") else []

            # 이미지 URL 리스트 추출
            image_urls = [
                f"https:{img['src']}" for img in soup.select(".shopArea_left .s_img li img")
            ]

            # 영업 시간 추출
            store_hours = []
            hours_sections = soup.select(".date_time dl")
            for dl in hours_sections:
                dt_tags = dl.select("dt")
                dd_tags = dl.select("dd")
                store_hours.extend([
                    ' '.join(f"{dt.text} {dd.text}".split()) for dt, dd in zip(dt_tags, dd_tags)
                ])

            # JSON 데이터 생성
            store_data = {
                "number": index + 1, 
                "name": store_name,
                "description": store_description,
                "address": store_address,
                "parking": store_parking_info,
                "directions": store_directions,
                "phone": store_phone,
                "services": store_services,
                "facilities": store_facilities,
                "images": image_urls,
                "hours": store_hours, 
            }
            store_data_list.append(store_data)

            # 상세 정보 창 닫기
            close_button = browser.find_element(By.CSS_SELECTOR, ".btn_pop_close .isStoreViewClosePop")
            browser.execute_script("arguments[0].click();", close_button)
            time.sleep(2)

        # 최종 JSON 구조 정의
        final_data = {
            "location": location_name_eng,
            "count": len(store_data_list),
            "date": current_date,
            "item": store_data
        }

        # details 폴더에 영문 이름으로 폴더 생성
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
            localSearch.click()
            print("지역 검색 버튼을 클릭했습니다.")
            time.sleep(3)
        except Exception as e:
            print("지역 검색 버튼을 클릭하는 데 실패했습니다:", e)
            browser.quit()
            exit()

except TimeoutException:
    print("페이지 로드 실패")
    
finally:
    # 브라우저 종료
    browser.quit()
