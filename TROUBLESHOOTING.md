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
