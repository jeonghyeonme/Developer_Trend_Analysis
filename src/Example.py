import numpy as np
import pandas as pd
import requests
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome()
driver.get('https://www.saramin.co.kr/zf_user/')
main_window = driver.current_window_handle

main_window = driver.current_window_handle # 메인 창 선택
# 로그인 버튼 누르기
login_btn = driver.find_element(By.XPATH, '//*[@id="section_contents"]/div/div[4]/a')
login_btn.click()
# 난 카카오로긴이라 카카오 로그인 선택
kakao_login = driver.find_element(By.XPATH, '//*[@id="wrap_social_login"]/li[2]/a/span')
kakao_login.click()

for handle in driver.window_handles: # 로그인하는 창으로 읻동
    if handle != main_window:
        driver.switch_to.window(handle)
        break
        
# id, password 입력
keyword = driver.find_element(By.XPATH,'//*[@id="loginId--1"]')
keyword.send_keys('***@naver.com') # id

keyword = driver.find_element(By.XPATH,'//*[@id="password--2"]')
keyword.send_keys('***') # password

# 로그인 버튼 클릭
driver.find_element(By.XPATH,'//*[@id="mainContent"]/div/div/form/div[4]/button[1]').click()

# 메인 페이지 이동
driver.switch_to.window(main_window)

# 검색창 클릭
time.sleep(2)
keyword = driver.find_element(By.XPATH,'//*[@id="btn_search"]/span[2]')
keyword.click()

# 데이터 분석 키워드 입력
keyword = driver.find_element(By.XPATH,'//*[@id="ipt_keyword_recruit"]')
keyword.send_keys('데이터분석')

# 키워드 검색 클릭
driver.find_element(By.XPATH,'//*[@id="btn_search_recruit"]').click()

# 경력 선택
time.sleep(3)
driver.find_element(By.XPATH,'//*[@id="sp_main_wrapper"]/div[1]/div[1]/button').click()
driver.find_element(By.XPATH,'//*[@id="sp_main_wrapper"]/div[1]/div[1]/div/div[1]/div[1]/label').click()
driver.find_element(By.XPATH,'//*[@id="sp_main_wrapper"]/div[1]/div[1]/div/div[1]/div[3]/label').click()


# 학력 선택
driver.find_element(By.XPATH,'//*[@id="sp_main_wrapper"]/div[1]/div[2]/button').click()
driver.find_element(By.XPATH,'//*[@id="btn_check_edu_0"]').click()
driver.find_element(By.XPATH,'//*[@id="btn_check_edu_3"]').click()
driver.find_element(By.XPATH,'//*[@id="sp_main_wrapper"]/div[1]/div[2]/div/div[1]/div/label').click()
driver.find_element(By.XPATH,'//*[@id="sp_main_wrapper"]/div[1]/div[2]/div/div[3]/button[2]').click()

# 검색 누르기
driver.find_element(By.XPATH,'//*[@id="search_btn"]').click()

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

recruit_df = pd.DataFrame(columns=['기업명', '직무명', '근무지', '경력', '학력', '근무형태', '마감일', '지원방법', '채용링크'])
# 1 page부터 10 page 수집
for i in range(1, 11):
    original_window = driver.current_window_handle
    # 1 페이지의 공고가 40개 들어있음
    for j in range(1, 41):
        # 공고에 데이터 분석이 들어있는 데이터만 수집
        try: a = driver.find_element(By.XPATH, '//*[@id="recruit_info_list"]/div[1]/div[{}]/div[1]/h2/a/span'.format(j))
        except: a = driver.find_element(By.XPATH, '//*[@id="recruit_info_list"]/div[1]/div[{}]/div[2]/h2/a/span'.format(j))
        
        keyword = a.text
        if '데이터 분석' in keyword or '데이터분석' in keyword or '분석' in keyword:
            try:
                driver.find_element(By.XPATH, '//*[@id="recruit_info_list"]/div[1]/div[{}]/div[2]/h2/a/span'.format(j)).click()
            except StaleElementReferenceException:
                print("StaleElementReferenceException 발생. 요소를 다시 조회합니다.")
                # 요소 재조회 후 클릭
                time.sleep(3)
                driver.find_element(By.XPATH, '//*[@id="recruit_info_list"]/div[1]/div[{}]/div[2]/h2/a/span'.format(j)).click()
            except NoSuchElementException:
                time.sleep(3)
                driver.find_element(By.XPATH, '//*[@id="recruit_info_list"]/div[1]/div[{}]/div[1]/h2/a/span'.format(j)).click()
            
            last_tab = driver.window_handles[-1]
            driver.switch_to.window(window_name=last_tab)
            time.sleep(1)

          
            try: 
                page = driver.find_element(By.XPATH, '//*[@id="content"]/div[3]/section[1]/div[1]').text
            except:
                time.sleep(5)
                try:
                    page = driver.find_element(By.XPATH, '//*[@id="content"]/div[3]/section[1]/div[1]').text
                except:
                    print('오류발생: ', a.text)
                    pass
            page = page.split('\n')
            
            if page[page.index('관심기업')-1] != '취업축하금 50만원':
                company_name = page[page.index('관심기업')-1]
            else: company_name = page[page.index('관심기업')-2]
            try:
                job_name = driver.find_element(By.XPATH,'//*[@id="content"]/div[3]/section[1]/div[1]/div[1]/div[1]/h1').text
            except: job_name = None
            career = page[page.index('경력')+1]
            education = page[page.index('학력')+1]
            employment_type = page[page.index('근무형태')+1]
            
            
            period_method = driver.find_element(By.XPATH,'//*[@id="content"]/div[3]/section[1]/div[1]').text
            li = period_method.split('\n')
            
            if '마감일' in li:
                deadline = li[li.index('마감일') + 1]
            else: deadline = '채용시 마감'
           
            if '지원방법' in li:
                apply_method = li[li.index('지원방법') + 1]
            else: apply_method = '지원 마감'
            
            try: location = li[li.index('기업주소') + 1]
            except: location = page[page.index('근무지역')+1]
            link = driver.current_url
            
            new_row = {
                '기업명': company_name,
                '직무명': job_name,
                '근무지': location,
                '경력': career,
                '학력': education,
                '근무형태': employment_type,
                '마감일': deadline,
                '지원방법': apply_method,
                '채용링크': link
            }
            new_row_df = pd.DataFrame([new_row])

            recruit_df = pd.concat([recruit_df, new_row_df])
            
            driver.close()  # 현재 탭 닫기

            # 첫 번째 탭으로 다시 전환
            driver.switch_to.window(original_window)
       
             # 스크롤 내리기
            driver.execute_script("window.scrollBy(0, 155);")
    driver.find_element(By.XPATH, '//*[@id="recruit_info_list"]/div[2]/div/a[{}]'.format(i)).click()
        
