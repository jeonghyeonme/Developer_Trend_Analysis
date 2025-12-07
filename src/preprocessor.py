import json
import pandas as pd
import re
import numpy as np

def load_raw_data(file_path='data/raw_jobs.json'):
    """raw_jobs.json 파일을 읽어와 파이썬 객체로 변환"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def flatten_data(raw_data):
    """직무별로 나뉜 데이터를 단일 리스트로 통합"""
    all_jobs = []
    for job_category, jobs in raw_data.items():
        category_name = '백엔드' if '백엔드' in job_category else '프론트엔드' if '프론트엔드' in job_category else '기타'
        for job in jobs:
            job['job_category'] = category_name
            all_jobs.append(job)
    return all_jobs

def extract_tech_stack(text):
    """텍스트에서 주요 기술 스택을 추출하고 표준화"""
    if not isinstance(text, str):
        return []

    tech_keywords = {
        'Python': ['python', '파이썬'], 'Java': ['java', '자바'], 'Spring': ['spring', '스프링'],
        'Spring Boot': ['spring boot', '스프링부트'], 'JPA': ['jpa'], 'JavaScript': ['javascript', 'js'],
        'TypeScript': ['typescript', 'ts'], 'React': ['react', '리액트'], 'Vue.js': ['vue.js', 'vue'],
        'Next.js': ['next.js'], 'Node.js': ['node.js', 'node'], 'SQL': ['sql'], 'MySQL': ['mysql'],
        'PostgreSQL': ['postgresql'], 'MongoDB': ['mongodb'], 'AWS': ['aws', 'amazon web services'],
        'Docker': ['docker', '도커'], 'Kubernetes': ['kubernetes', '쿠버네티스', 'k8s'],
        'Git': ['git', '깃'], 'Linux': ['linux', '리눅스']
    }

    found_stacks = set()
    lower_text = text.lower()
    for standard_name, keywords in tech_keywords.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', lower_text):
                found_stacks.add(standard_name)
                break
    return sorted(list(found_stacks))

def clean_location(text):
    """지역 데이터 정제 (경기도 내 시/군 구분)"""
    if not isinstance(text, str):
        return '기타'

    parts = text.split()
    
    # "경기"로 시작하고 다음 단어가 있을 경우, 다음 단어(시/군)를 사용
    if parts and parts[0] == '경기' and len(parts) > 1:
        # '성남시', '용인시' 등에서 '시' 제거
        return parts[1].replace('시', '').replace('군', '')
    
    # 그 외의 경우, 첫 단어를 사용
    elif parts:
        return parts[0]
        
    return '기타'

def clean_experience(text):
    """경력 데이터 정제"""
    if not isinstance(text, str): return '기타'
    if '신입' in text and '경력' in text: return '신입/경력'
    if '신입' in text: return '신입'
    if '경력' in text: return '경력'
    if '무관' in text: return '무관'
    return '기타'

def main():
    """데이터 전처리 파이프라인 실행"""
    raw_data = load_raw_data()
    jobs = flatten_data(raw_data)
    
    processed_jobs = []
    for job in jobs:
        tech_stack = extract_tech_stack(job.get('details', ''))
        location = clean_location(job.get('location'))
        experience = clean_experience(job.get('experience'))
        
        # Salary processing
        salary_str = job.get('salary', '')
        salary = '회사내규에 따름'
        if salary_str and not ('결정' in salary_str or '내규' in salary_str):
            text_no_comma = salary_str.replace(',', '')
            numbers = re.findall(r'\d+', text_no_comma)

            if numbers:
                period = '월급' if '월급' in salary_str else '연봉'
                min_val = numbers[0]
                salary = f"{period} {min_val}만원"

        processed_job = {
            'title': job.get('title'),
            'company': job.get('company'),
            'job_category': job.get('job_category'),
            'experience': experience,
            'salary': salary,
            'location': location,
            'tech_stack': tech_stack,
        }
        processed_jobs.append(processed_job)

    df = pd.DataFrame(processed_jobs)
    
    print("--- 전처리된 데이터 샘플 (상위 5개) ---")
    print(df[['title', 'salary']].head())

    output_path = 'data/processed_jobs.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n전처리된 데이터가 '{output_path}'에 성공적으로 저장되었습니다.")

if __name__ == '__main__':
    main()
