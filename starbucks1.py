from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import os
import time

# 현재 날짜를 문자열로 저장
current_date = datetime.now().strftime("%Y-%m-%d")

# location 폴더 생성
base_folder = "location"
os.makedirs(base_folder, exist_ok=True)

# 웹드라이버 설정 및 페이지 로드
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-infobars")
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

    # 페이지 소스를 HTML 파일로 저장
    html_file_path = os.path.join(base_folder, f"starbucks_map_{current_date}.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(browser.page_source)
        print(f"페이지 소스가 '{html_file_path}' 파일에 저장되었습니다.")

except TimeoutException:
    print("페이지 로드 실패")
finally:
    # 브라우저 종료
    browser.quit()
