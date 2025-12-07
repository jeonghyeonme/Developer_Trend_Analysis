# 사람인 크롤러 개발 트러블슈팅

이 문서는 사람인(Saramin) 웹 크롤러를 개발하는 과정에서 발생했던 주요 기술적 문제와 해결 과정을 기록합니다.

## 1. 상세 정보 수집 불가 (동적 컨텐츠 로딩)

- **문제**: `requests`와 `BeautifulSoup`만 사용했을 때, 채용 공고의 제목과 회사명 등 목록에 보이는 정보는 수집되지만, 정작 중요한 직무 상세 내용(자격 요건, 우대 사항 등)이 수집되지 않고 비어있는 현상 발생.
- **원인**: 대상 웹페이지가 초기 HTML 로딩 후, JavaScript를 통해 동적으로 상세 내용을 렌더링하는 방식으로 작동. `requests`는 JavaScript를 실행하지 않으므로 동적으로 생성된 컨텐츠에 접근할 수 없었음.
- **해결**: 실제 브라우저 환경을 제어하여 JavaScript를 실행시킬 수 있는 `Selenium`을 도입. `requests`로 목록 페이지를 빠르게 가져온 뒤, 각 상세 페이지는 `Selenium`으로 접속하여 최종 렌더링된 HTML 소스를 기반으로 데이터를 추출하는 하이브리드 방식으로 변경하여 문제 해결.

## 2. `<iframe>` 내부 컨텐츠 수집 문제

- **문제**: `Selenium`을 도입했음에도 불구하고, 여전히 직무 상세 내용(`details`)이 수집되지 않음.
- **원인**: 브라우저 개발자 도구를 통해 HTML 구조를 심층 분석한 결과, 직무 상세 내용이 부모 페이지가 아닌 별도의 `<iframe>` 태그 내에 로드되고 있었음. `<iframe>`은 독립적인 문서로 취급되므로, 부모 페이지의 HTML 소스만으로는 내부 컨텐츠에 접근할 수 없음.
- **해결**: 
  1. `Selenium`으로 부모 페이지에 접속한 뒤, `BeautifulSoup`으로 `#iframe_content_0` 선택자를 사용하여 `<iframe>` 요소를 찾음.
  2. 해당 요소의 `src` 속성에서 실제 컨텐츠가 담긴 URL을 추출.
  3. 추출한 `iframe`의 URL로 다시 `requests`를 통해 접속하여 내부 HTML을 가져온 뒤, `body` 태그의 전체 텍스트를 파싱하여 최종 `details` 정보를 얻음.

## 3. Selenium 브라우저 예기치 않게 종료 (`no such window`)

- **문제**: 스크립트 실행 중 `selenium.common.exceptions.NoSuchWindowException: Message: no such window: target window already closed` 오류가 발생하며 크롤러가 멈춤.
- **원인**: 웹사이트의 자동화 탐지 시스템이나, 광고 팝업 등 예기치 않은 이벤트로 인해 Selenium이 제어하던 브라우저 세션이 불안정해지거나 강제 종료됨.
- **해결**: 실제 UI를 렌더링하지 않고 백그라운드에서 실행되는 **헤드리스 모드(Headless Mode)** 로 `Selenium`을 실행. 아래와 같은 안정성 관련 옵션을 추가하여 드라이버의 실행 안정성을 높여 문제 해결.
  ```python
  options = Options()
  options.add_argument("--headless")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--disable-gpu")
  ```

## 4. 동적으로 변하는 CSS 선택자 문제

- **문제**: 브라우저에서 복사한 CSS 선택자를 코드에 적용했음에도 특정 공고에서는 데이터를 찾지 못하고 실패하는 현상 발생.
- **원인**: 제공된 선택자 (`section.jview.jview-0-52059894`) 내에 포함된 숫자 `52059894`가 각 공고마다 변하는 동적 ID 값이었음. 이로 인해 해당 ID를 가진 특정 공고 외에는 선택자가 일치하지 않음.
- **해결**: 동적 ID 부분을 제거하고, `[class^="jview"]` 와 같이 클래스 이름이 특정 문자열로 "시작하는" 모든 요소를 찾는 **CSS 속성 선택자(Attribute Selector)** 를 사용하여 어떤 공고에서든 일관되게 적용될 수 있는 안정적인 선택자로 변경.

## 5. 상대 경로 URL 처리 오류

- **문제**: `<iframe>`의 `src` 속성에서 추출한 URL로 `requests` 요청 시 `Invalid URL ... No scheme supplied` 오류 발생.
- **원인**: `src` 속성의 값이 `https://...` 로 시작하는 전체 URL이 아닌, `/zf_user/jobs/...` 와 같은 상대 경로(relative path)였음. `requests`는 전체 URL이 없으면 요청을 보낼 수 없음.
- **해결**: `urllib.parse.urljoin` 함수를 사용하거나, `startswith('http')`를 확인하는 조건문을 추가하여, 상대 경로일 경우 앞에 기본 URL(`https://www.saramin.co.kr`)을 붙여주어 항상 유효한 전체 URL로 요청을 보내도록 수정.

---

# 데이터 분석 및 환경설정 트러블슈팅

## 6. `ModuleNotFoundError: No module named '...'`

- **문제**: `pandas` 또는 `networkx` 라이브러리를 `import`하는 코드 실행 시, 해당 모듈을 찾을 수 없다는 오류 발생.
- **원인**: 프로젝트를 실행하는 Python 환경에 해당 라이브러리가 설치되어 있지 않음. `requirements.txt`에 명시되어 있더라도, 별도로 설치해주어야 함. 또한, 터미널의 `pip`가 사용하는 Python 환경과 Jupyter Notebook 커널이 사용하는 Python 환경이 다를 경우, 터미널에만 라이브러리가 설치되고 노트북에서는 인식하지 못하는 문제가 발생할 수 있음.
- **해결**:
  1. **올바른 환경에 설치**: `!pip install networkx` 와 같이, Jupyter Notebook 셀 안에서 `!`를 붙여 직접 라이브러리를 설치하는 것이 가장 확실함.
  2. **의존성 파일 관리**: `requirements.txt` 파일에도 새로 추가한 라이브러리 이름을 기록하여 프로젝트 의존성을 최신 상태로 유지.

## 7. `PermissionError: [Errno 13] Permission denied`

- **문제**: `preprocessor.py` 실행 중, `processed_jobs.csv` 파일을 저장하는 단계에서 권한 오류가 발생하며 실패.
- **원인**: `processed_jobs.csv` 파일이 Microsoft Excel, LibreOffice Calc 등 다른 프로그램에서 열려 있었음. 이 경우, 운영체제가 파일에 대한 쓰기 잠금(write lock)을 설정하여 다른 프로세스(Python 스크립트)가 해당 파일을 수정할 수 없게 됨.
- **해결**: 파일을 열고 있는 모든 프로그램을 종료한 후, 스크립트를 다시 실행하여 정상적으로 파일 쓰기 완료.

## 8. VS Code 내 Jupyter Notebook, 외부 변경사항 미반영

- **문제**: CLI 환경에서 `ipynb` 노트북 파일을 수정했음에도, VS Code에서 열려 있는 노트북 탭에는 변경사항이 전혀 반영되지 않는 현상 발생.
- **원인**: VS Code의 Jupyter 확장 프로그램이 실행 중인 커널(세션)의 메모리에 노트북 상태를 캐싱하고 있음. 이로 인해 외부 편집기가 디스크의 파일을 직접 수정해도, 열려있는 UI는 메모리의 이전 상태를 계속 보여줌.
- **해결**:
  - **방법 1 (가장 확실):** VS Code에서 `Ctrl + Shift + P`로 커맨드 팔레트를 열고, `Developer: Reload Window` 명령을 실행하여 VS Code 창 전체를 새로고침.
  - **방법 2:** 노트북 상단 툴바의 원형 화살표(↻) 아이콘, 즉 **'커널 다시 시작(Restart Kernel)'**을 실행.
  - **방법 3 (최후의 수단):** VS Code 에디터를 완전히 종료했다가 다시 실행.

## 9. `ipynb` 파일 손상 (JSON Syntax Error)

- **문제**: 수정한 노트북 파일을 열 때 `SyntaxError: Bad escaped character` 또는 `Bad control character in string literal` 와 같은 JSON 파싱 오류가 발생하며 파일이 열리지 않음.
- **원인**: `ipynb` 파일은 본질적으로 특정 구조를 가진 JSON 파일임. CLI 환경에서 `write_file` 도구를 사용하여 프로그래밍 방식으로 이 JSON 구조를 생성할 때, 코드 내의 특정 문자(정규식의 `\`, 제어 문자 `\n` 등)가 JSON 표준에 맞게 이스케이프(escape) 처리되지 않아 파일 전체의 구조가 손상됨.
- **해결**:
  1. `write_file`을 통한 자동 수정을 여러 번 시도했으나, 복잡한 노트북 구조로 인해 계속 실패.
  2. 근본적인 해결책으로, **자동 파일 수정을 포기**.
  3. 대신, 모든 분석 코드가 포함된 **단일 Python 스크립트**를 사용자에게 제공하고, 사용자가 직접 손상된 노트북 파일의 내용을 지운 뒤 전체를 복사/붙여넣기하는 수동 방식으로 최종 해결. 이는 자동화 도구의 한계가 명확할 때 가장 신뢰할 수 있는 방법임.
