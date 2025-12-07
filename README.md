# 신입 개발자 기술 트렌드 분석

## 1. 프로젝트 개요

이 프로젝트는 **사람인(Saramin)** 웹사이트에서 신입 개발자 채용 공고 데이터를 직접 크롤링하여 수집하고 분석합니다. 이를 통해 현재 채용 시장에서 요구하는 주요 기술 스택과 역량 트렌드를 파악하고, 신입 개발자 구직자에게 유용한 인사이트를 제공하는 것을 목표로 합니다.

## 2. 주요 기능 및 분석 내용

- **데이터 수집**: `requests`와 `Selenium`을 활용하여 사람인 웹사이트에서 신입 개발자 채용 공고를 수집합니다.
- **데이터 전처리**: 수집된 원본 데이터를 정제하여 (`경기도` → `성남`, `분당` 등) 상세 분석이 가능한 형태로 가공합니다.
- **심층 분석 및 시각화**:
  - **전체 기술 수요 분석**: 모든 공고를 대상으로 가장 많이 요구되는 Top 15 기술 스택을 시각화합니다.
  - **직무별 기술 채택률 비교**: 백엔드와 프론트엔드 직무 내에서 각 기술이 차지하는 중요도(%)를 대칭형 막대그래프로 비교합니다.
  - **주요 기술 조합 분석**: Top 15 기술들이 서로 어떻게 조합되어 사용되는지 **히트맵(Heatmap)**으로 시각화하여 기술 생태계를 보여줍니다.
  - **경력 요구사항별 기술 비교**: '신입'과 '신입/경력' 공고 간의 기술 요구사항 차이를 분석합니다.
  - **기술별 연봉 분포**: 급여가 명시된 공고에 한해, 주요 기술 스택별 연봉의 전체 분포를 **박스 플롯(Box Plot)**으로 비교 분석합니다.
  - **지역별 공고 분포**: 대한민국 지도 위에 지역별 공고 수를 표현하는 **산점도 지도**를 시각화합니다.

## 3. 기술 스택

- **데이터 수집 (Crawling):**
  - `Python`, `requests`, `BeautifulSoup`, `Selenium`, `webdriver-manager`
- **데이터 처리 및 분석 (Analysis):**
  - `Python`, `Pandas`, `NumPy`
- **데이터 시각화 (Visualization):**
  - `Matplotlib`, `Seaborn`, `networkx`

## 4. 설치 및 실행 방법

**1. 저장소 복제:**
```bash
git clone https://github.com/your-username/Developer-Trend-Analysis.git
cd Developer-Trend-Analysis
```

**2. 가상 환경 생성 및 활성화:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. 필요 라이브러리 설치:**
```bash
pip install -r requirements.txt
```

**4. 프로젝트 실행 순서:**

   **a. 데이터 수집 실행:**
   ```bash
   # src/crawler.py 상단의 MAX_PAGES, QUERIES 값을 조절하여 크롤링할 페이지 수 및 검색어 설정
   python src/crawler.py
   ```

   **b. 데이터 전처리 실행:**
   ```bash
   python src/preprocessor.py
   ```

   **c. 데이터 분석 실행:**
   ```bash
   # Jupyter 환경에서 notebooks/analysis.ipynb 파일을 엽니다.
   jupyter notebook notebooks/analysis.ipynb
   ```

## 5. 디렉토리 구조

```
Developer-Trend-Analysis/
├── src/                  # 소스 코드 디렉토리
│   ├── crawler.py        # 데이터 수집기
│   └── preprocessor.py   # 데이터 전처리기
├── data/                 # 데이터 저장 디렉토리
│   ├── raw_jobs.json
│   └── processed_jobs.csv
├── notebooks/            # 데이터 분석용 Jupyter Notebook
│   └── analysis.ipynb
├── requirements.txt      # 프로젝트 의존성 라이브러리 목록
├── README.md             # 프로젝트 개요 (현재 문서)
└── TROUBLESHOOTING.md    # 개발 과정 트러블슈팅 기록
```

## 6. 분석 보고서

상세 분석 결과는 아래 보고서 파일에서 확인하실 수 있습니다.

- [신입 개발자 기술 트렌드 분석 보고서.pdf](./reports/신입%20개발자%20기술%20트렌드%20분석%20보고서.pdf)