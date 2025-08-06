from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from datetime import datetime
import time

def get_reviews_by_cafe_name(cafe_name: str) -> list[str]:
    """
    - 네이버 지도에서 cafe_name을 검색
    - 장소 페이지에서 리뷰 탭 클릭
    - 리뷰 문자열 리스트 반환
    """

    # Selenium 코드 사용

    # 1. 크롬 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ✅ 브라우저 창 숨김
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920x1080")  # ✅ 창 크기 명시 (최대화 대신)
    #chrome_options.add_argument("--start-maximized")  # 창 최대화
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 감지 회피

    # 2. 드라이버 경로 설정 (만약 PATH에 없다면 직접 지정)
    service = Service("/usr/local/bin/chromedriver")  # 설치한 경로에 따라 수정

    # 3. 크롬 드라이버 실행
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 4. 네이버 지도 열기
    driver.get("https://map.naver.com")

    # ✅ 검색창이 뜰 때까지 기다림
    search_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "input_search"))
    )

    search_box.clear()
    search_box.send_keys(cafe_name)
    search_box.send_keys(Keys.ENTER)

    time.sleep(2)

    # iframe 목록 탐색
    try:
        # 우선 entryIframe이 나타나는지 먼저 3~5초 정도 기다림
        WebDriverWait(driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe"))
        )
        print("[+] entryIframe 진입 완료 (상세 페이지)")
    except:
        try:
            # entryIframe이 없으면 그제서야 searchIframe 진입 시도
            WebDriverWait(driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe"))
            )
            print("[+] searchIframe 진입 완료 (검색 결과 목록)")

            first_place = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.place_bluelink"))
            )
            print("[+] 첫 번째 장소 클릭 시도")
            first_place.click()

            # ✅ 메인 DOM으로 돌아와서 entryIframe 대기
            driver.switch_to.default_content()

            MAX_RETRY = 5
            found = False

            for attempt in range(MAX_RETRY):
                try:
                    driver.switch_to.default_content()
                    WebDriverWait(driver, 3).until(
                        EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe"))
                    )
                    print(f"[+] entryIframe 진입 성공 (시도 {attempt + 1}회)")
                    found = True
                    break
                except:
                    print(f"[*] entryIframe 아직 안뜸... ({attempt + 1}/{MAX_RETRY}) 재시도 중")
                    time.sleep(1)

            if not found:
                print("[!] entryIframe 끝내 진입 실패")
                driver.quit()
                exit()
        except:
            print("[!] entryIframe / searchIframe 둘 다 찾지 못함")
            driver.quit()
            return []

    # ✅ 상세 페이지 로딩 확인
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "place_section_content"))
        )
        print("[+] 장소 상세 페이지 로딩 완료")
    except:
        print("[-] 장소 상세 페이지 로딩 실패")
        driver.quit()
        return []

    # (리뷰 크롤링은 여기서부터!)

    # 1. 리뷰 탭 클릭
    try:
        review_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='review']"))
        )
        review_tab.click()
        print("[+] 리뷰 탭 클릭 완료")
    except Exception as e:
        print("[!] 리뷰 탭 클릭 실패:", e)
        driver.quit()
        return []

    # 1.5. 리뷰 리스트 확장용 더보기 클릭하기
    cnt = 0

    while cnt < 5:
        try:
            more_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "fvwqf"))
            )
            print("[+] 리뷰 더보기 버튼 클릭")
            driver.execute_script("arguments[0].click();", more_btn)  # JS 클릭 우회
            cnt += 1
            time.sleep(1.2)  # 로딩 대기
        except TimeoutException:
            print("[*] 더보기 버튼 없음 → 모든 리뷰 로딩 완료")
            break
        except ElementClickInterceptedException:
            print("[!] 클릭 실패 → 스크롤 시도 후 재시도")
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(0.5)

    # 2. 리뷰 영역 로딩 대기
    try:
        review_blocks = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pui__vn15t2"))  # 리뷰 텍스트 span
        )
        print(f"[+] 리뷰 {len(review_blocks)}개 로딩 완료")
    except Exception as e:
        print("[!] 리뷰 로딩 실패:", e)
        driver.quit()
        return []

    # 3. 리뷰 텍스트 추출
    review_result = []

    for idx, block in enumerate(review_blocks, start=1):
        try:
            a_tag = block.find_element(By.TAG_NAME, "a")
            review_text = a_tag.get_attribute("innerText").strip()
            if review_text:
                review_result.append(review_text)
                print(f"리뷰 {idx}: {review_text}\n")
        except Exception as e:
            print(f"[!] 리뷰 {idx} 파싱 실패: {e}")
            driver.quit()
            return []

    driver.quit()
    return review_result