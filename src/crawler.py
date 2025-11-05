import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import quote, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 설정 --- #
# 분석할 검색어 목록
QUERIES = ["신입 백엔드 개발자"]
# 각 검색어당 크롤링할 페이지 수 (이 값을 수정하여 페이지 수 조절)
MAX_PAGES = 1
# 결과 저장 파일 경로
OUTPUT_FILE = "C:/Users/parad/Developer-Trend-Analysis/data/raw_jobs.json"
# 사람인 기본 URL
SARAMIN_BASE_URL = "https://www.saramin.co.kr"


def fetch_page(url):
    """
    주어진 URL의 HTML을 가져옵니다.

    Args:
        url (str): 가져올 페이지의 URL

    Returns:
        str: 페이지의 HTML 내용. 실패 시 None.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"페이지 요청 중 오류 발생: {e}")
        return None

def parse_job_links(html):
    """
    검색 결과 페이지 HTML에서 채용 공고 상세 페이지 링크 목록을 추출합니다.

    Args:
        html (str): 검색 결과 페이지의 HTML

    Returns:
        list: 채용 공고 상세 페이지 URL 문자열의 리스트
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    items = soup.find_all('div', class_='item_recruit')
    for item in items:
        link_tag = item.find('a', class_='data_layer')
        if link_tag and 'href' in link_tag.attrs:
            # urljoin을 사용하여 상대 경로와 절대 경로 모두 안전하게 처리
            full_link = urljoin(SARAMIN_BASE_URL, link_tag['href'])
            links.append(full_link)
    return list(set(links)) # 중복 링크 제거

def scrape_job_details(driver, url):
    """
    Selenium을 사용하여 채용 공고 상세 정보를 스크래핑합니다.

    Args:
        driver: Selenium WebDriver 인스턴스
        url (str): 스크래핑할 채용 공고 상세 페이지 URL

    Returns:
        dict: 스크래핑된 채용 공고 상세 정보. 실패 시 None.
    """
    try:
        driver.get(url)
        time.sleep(3) # 동적 컨텐츠 로딩 대기
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # --- 기본 정보 추출 ---
        title = soup.select_one('section[class^="jview"] h1').get_text(strip=True) if soup.select_one('section[class^="jview"] h1') else 'N/A'
        company = soup.select_one('section[class^="jview"] a.company').get_text(strip=True) if soup.select_one('section[class^="jview"] a.company') else 'N/A'
        
        # --- 요약 정보(경력, 학력 등) 추출 ---
        summary_info = {
            'experience': 'N/A', 'education': 'N/A', 'employment_type': 'N/A',
            'salary': 'N/A', 'location': 'N/A'
        }
        summary_section = soup.select_one('section[class^="jview"] div.jv_cont.jv_summary')
        if summary_section:
            for dl in summary_section.find_all('dl'):
                dt = dl.find('dt')
                dd = dl.find('dd')
                if dt and dd:
                    key = dt.get_text(strip=True)
                    value = dd.get_text(strip=True)
                    if key == '경력': summary_info['experience'] = value
                    elif key == '학력': summary_info['education'] = value
                    elif key == '근무형태': summary_info['employment_type'] = value
                    elif key == '급여': summary_info['salary'] = value
                    elif key == '근무지역': summary_info['location'] = value

        # --- 상세 내용(iframe) 추출 ---
        details = 'N/A'
        try:
            iframe = soup.select_one('#iframe_content_0')
            if iframe and 'src' in iframe.attrs:
                iframe_url = urljoin(SARAMIN_BASE_URL, iframe['src'])
                iframe_html = fetch_page(iframe_url)
                if iframe_html:
                    iframe_soup = BeautifulSoup(iframe_html, 'html.parser')
                    details = iframe_soup.find('body').get_text("\n", strip=True)
        except Exception as iframe_e:
            print(f"    iframe 처리 중 오류 발생: {iframe_e}")

        # --- 최종 데이터 조합 (details를 마지막으로) ---
        job_details = {
            'title': title,
            'company': company,
            'experience': summary_info['experience'],
            'education': summary_info['education'],
            'employment_type': summary_info['employment_type'],
            'salary': summary_info['salary'],
            'location': summary_info['location'],
            'url': url,
            'details': details
        }
        return job_details

    except Exception as e:
        print(f"상세 페이지({url}) 스크래핑 중 오류 발생: {e}")
        return None

def main():
    """
    사람인 사이트에서 신입 개발자 채용 정보를 크롤링하는 메인 함수
    """
    # Selenium WebDriver 설정
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"WebDriver 설정 중 오류 발생: {e}")
        return

    # 최종 데이터를 검색어별로 그룹화하여 저장할 딕셔너리
    all_jobs_by_query = {}

    # 설정된 검색어 목록 순회
    for query in QUERIES:
        print(f"\n'{query}'에 대한 채용 공고 크롤링 시작...")
        # 현재 쿼리에 대한 채용 공고를 저장할 리스트 초기화
        all_jobs_by_query[query] = []
        
        # 설정된 페이지 수만큼 순회
        for page in range(1, MAX_PAGES + 1):
            print(f"  - 목록 페이지 {page}/{MAX_PAGES} 크롤링 중...")
            encoded_query = quote(query)
            search_url = f"{SARAMIN_BASE_URL}/zf_user/search?searchType=search&searchword={encoded_query}&recruitPage={page}"
            
            list_html = fetch_page(search_url)
            if not list_html:
                continue

            job_links = parse_job_links(list_html)
            if not job_links:
                print(f"    페이지 {page}에서 더 이상 채용 공고를 찾을 수 없습니다.")
                break

            for link in job_links:
                print(f"    - 상세 페이지 크롤링: {link}")
                job_details = scrape_job_details(driver, link)
                if job_details:
                    # 현재 쿼리에 해당하는 리스트에 상세 정보 추가
                    all_jobs_by_query[query].append(job_details)
                time.sleep(1) # 서버 부하 방지
    
    driver.quit()

    # --- 결과 저장 ---
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_jobs_by_query, f, ensure_ascii=False, indent=4)
    
    total_jobs_count = sum(len(jobs) for jobs in all_jobs_by_query.values())
    if not total_jobs_count:
        print("\n수집된 채용 공고가 없습니다. CSS 선택자 또는 웹사이트 구조 변경을 확인해주세요.")
    else:
        print(f"\n총 {total_jobs_count}개의 채용 공고를 '{OUTPUT_FILE}'에 저장했습니다.")

if __name__ == "__main__":
    main()
