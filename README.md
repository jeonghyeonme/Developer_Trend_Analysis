# 신입 개발자 기술 트렌드 분석

## 1. 프로젝트 개요

이 프로젝트는 **사람인(Saramin)** 사이트의 신입 개발자 채용 공고 데이터를 수집하고 분석하여, 현재 채용 시장에서 요구하는 주요 기술 스택과 역량 트렌드를 파악하는 것을 목표로 합니다.

Python 기반의 웹 크롤러를 통해 데이터를 수집하고, 정제 및 분석 과정을 거쳐 신입 개발자 구직자에게 유용한 인사이트를 제공하고자 합니다.

## 2. 주요 기능 및 분석 내용

- **데이터 수집:**
  - 사람인 사이트에서 '신입 백엔드', '신입 프론트엔드' 등 직무별 채용 공고 데이터를 크롤링합니다.
  - 수집된 데이터는 JSON 파일 및 MongoDB에 저장됩니다.
- **핵심 기술 스택 분석 (정량 분석):**
  - 채용 공고의 자격 요건 및 우대 사항을 분석하여 가장 많이 언급되는 Top 10 기술 스택을 추출합니다.
  - 함께 자주 사용되는 기술 조합(예: Spring Boot + JPA)을 분석합니다.
- **잠재 역량 분석 (정성 분석):**
  - '협업', '성장', '커뮤니케이션' 등 우대사항에 나타난 소프트 스킬 키워드를 분석합니다.
- **시각화:**
  - 분석된 데이터를 Matplotlib, Seaborn 등의 라이브러리를 활용하여 그래프와 차트로 시각화합니다.

## 3. 기술 스택

- **데이터 수집 (Crawling):**
  - `Python`
  - `requests`
  - `BeautifulSoup`
- **데이터 처리 및 분석 (Analysis):**
  - `Pandas`
  - `NumPy`
- **데이터 시각화 (Visualization):**
  - `Matplotlib`
  - `Seaborn`
- **데이터베이스 (Database):**
  - `MongoDB`

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

**4. 데이터 수집 실행:**
```bash
python src/crawler.py
```

**5. 데이터 분석 실행:**
```bash
jupyter notebook notebooks/analysis.ipynb
```

## 5. 디렉토리 구조 (예상)

```
Developer-Trend-Analysis/
├── src/                  # 소스 코드 디렉토리
│   ├── crawler.py        # 사람인 크롤러
│   └── preprocessor.py   # 데이터 전처리기
├── data/                 # 수집된 데이터 저장
│   └── raw_jobs.json
├── notebooks/            # 데이터 분석용 Jupyter Notebook
│   └── analysis.ipynb
├── requirements.txt      # 프로젝트 의존성 라이브러리 목록
└── README.md             # 프로젝트 개요
```

*이 README는 프로젝트 진행 상황에 따라 업데이트될 예정입니다.*
