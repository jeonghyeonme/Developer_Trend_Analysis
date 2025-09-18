import pandas as pd

def preprocess_data(raw_data):
    """
    크롤링된 원시 데이터를 정제하고 분석 가능한 형태로 전처리하는 함수
    """
    # TODO: 데이터 전처리 로직 구현
    print("데이터 전처리기 실행됨")
    return raw_data

if __name__ == "__main__":
    # 예시 데이터
    sample_data = {"title": "신입 백엔드 개발자", "skills": "Java, Spring, JPA"}
    processed_data = preprocess_data(sample_data)
    print(processed_data)
