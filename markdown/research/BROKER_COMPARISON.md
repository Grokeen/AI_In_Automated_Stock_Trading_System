# RES-01 증권사 비교 — 국내 주식 모의 개발

- 조사일: 2026-11-08 (KST)
- 범위: KIS 우선 후보와 키움 REST API 대안, 국내 현물주식·paper 개발
- 상태: 공식 공개 자료 확인. 사용자 계좌·신청 상태 및 NAS 실기 통신은 미확인.
- 기준 커밋: 라운드 지시 기준 `e166d64f9ad9c9ecd65d73258dd95cd64fb36a51` (이 작업 폴더는 Git 저장소가 아니어서 HEAD 대조 불가)

## 비교와 근거

| 주제 | KIS Open API | 키움 REST API | 개발 영향 |
|---|---|---|---|
| API/기능 | REST OAuth 토큰과 WebSocket 접속키를 제공한다. 국내 주식 주문·정정·취소, 잔고·체결 조회와 현재가·호가·체결 WebSocket 범주가 공식 요약에 있다. [KIS API 구조](https://apiportal.koreainvestment.com/apiservice-summary) | 포털 가이드에서 OAuth, 국내주식 계좌·시세·주문·차트·실시간시세 범주를 제공한다. [키움 API 가이드](https://openapi.kiwoom.com/guide/apiguide) | 내부 공통 인터페이스를 먼저 만들고 증권사 필드와 오류는 어댑터 안에서 변환한다. 실시간 데이터·주문 유형은 개별 API 가이드로 다시 확인한다. |
| 환경 | 실전 REST `openapi.koreainvestment.com:9443`, 모의 REST `openapivts.koreainvestment.com:29443`; WebSocket 실전·모의 도메인이 별도이며 TLS 1.2/1.3 지원. [KIS API 구조](https://apiportal.koreainvestment.com/apiservice-summary) | 실전 `api.kiwoom.com`, 모의 `mockapi.kiwoom.com`; 모의 API 가이드는 KRX만 지원한다고 표시한다. [키움 API 가이드](https://openapi.kiwoom.com/guide/apiguide) | paper/live 서버 주소를 설정으로 분리하고 환경 이름과 자격증명 환경이 맞지 않으면 호출 전 차단한다. |
| 신청·키·계좌 | 한국투자 계좌 및 ID 연결 후 홈페이지/앱에서 Open API 신청이 필요하다. API 인증은 App Key·App Secret, REST 토큰, WebSocket approval key를 쓴다. 실전·모의 앱키와 계좌는 구분한다. [이용 안내](https://apiportal.koreainvestment.com/about-howto), [공식 Python 예제](https://github.com/koreainvestment/open-trading-api) | 계좌와 HTS ID 연결, API 사용 신청이 요구된다. App Key 발급 전에 허용 IP 등록을 요구하며 실전·모의 키를 별도 관리한다. [서비스 안내](https://openapi.kiwoom.com/intro/serviceInfo) | 개인 신청·ID 연계·모의계좌 발급은 문서 조사로 확인할 수 없다. 사용자 계좌가 이미 준비됐다고 전제하지 않는다. |
| 호출 한도 | 포털은 2026-03-20 신규 고객 제한 공지 및 2026-04-20 기준 REST/WebSocket 유량 안내를 게시하지만, 공지와 API 종류·고객 조건별 확인이 필요하다. 이 조사에서 모든 국내주식 API에 적용할 단일 최신 수치를 확정하지 않았다. [공지 목록](https://apiportal.koreainvestment.com/community/10000000-0000-0011-0000-000000000001) | 현재 서비스 안내는 국내 실전 주문 TR·조회 TR 각각 토큰당 초당 5회, 모의투자는 국내 TR별 초당 1회, 세션당 실시간 시세 200종목, 단일 세션을 안내한다. 포털은 변경될 수 있음을 밝힌다. [키움 서비스 안내](https://openapi.kiwoom.com/intro) | 증권사/계정/API별 rate limit을 설정 가능한 어댑터 정책으로 두고, 제한 응답·재시도 지연을 처리한다. KIS 수치 확정은 구현 직전 공지와 계정 화면 확인 뒤로 둔다. |
| 비용 | API 이용료와 계좌의 위탁 수수료·유관기관 비용·세금은 구분해야 한다. 포털 이벤트 공지는 특정 기간·조건의 혜택일 수 있어 기본 요율로 일반화하지 않는다. 적용 요율은 개인 계좌의 현재 거래 안내/약정 화면에서 확인해야 한다. [KIS 이벤트 공지](https://apiportal.koreainvestment.com/community/10000000-0000-0011-0000-000000000004), [국내주식 수수료 안내](https://securities.koreainvestment.com/main/customer/guide/_static/TF04ad010000.jsp) | API 이용 안내는 HTS와 동일한 수수료율을 적용한다고 설명한다. 실제 계좌 약정·이벤트 조건이 적용된 요율은 사용자 화면에서 확인해야 한다. [키움 서비스 안내](https://openapi.kiwoom.com/intro) | 고정 수수료 숫자를 코드 기본값으로 넣지 않는다. 실험 설정에 매수·매도 수수료, 세금·거래비용 항목을 분리해 기록하고 계좌 확인 전에는 값이 가정임을 표시한다. |
| 시세·종목 데이터 | REST 기본/분석 시세 및 WebSocket 체결·호가·예상체결 등 문서 범주를 제공한다. 주문·시세 대상 종목 마스터 파일을 제공하고 매일 업데이트 시각을 안내한다. [KIS API 구조](https://apiportal.koreainvestment.com/apiservice-summary) | 국내 실시간 시세 WebSocket과 시세·차트 API가 가이드에 있다. 모의 환경은 거래·계좌 조회 KRX 한정이지만 편의상 NXT 시세도 제공한다고 모의투자 안내에 명시한다. [모의투자 안내](https://openapi.kiwoom.com/intro/mockInvestInfo), [실시간 가이드](https://openapi.kiwoom.com/m/guide/apiguide/14/00) | 시세 제공 범위와 모의 주문 가능 거래소를 혼동하지 않는다. 종목 마스터·거래소·수신시각·거래소시각을 데이터에 보존한다. |
| NAS / Python | 공식 GitHub 저장소의 최신 README는 Python 3.11 이상을 요구한다. [KIS 공식 Python 예제](https://github.com/koreainvestment/open-trading-api) | 공개 REST 포털은 API HTTP 계약을 제시하지만 조사한 소개·가이드에서는 32비트 ARM용 공식 Python SDK 요구조건을 확인하지 못했다. | 기존 장비 기록은 armhf/32비트 사용자 환경이며 실제 Python은 재확인 대상이다. 양 증권사 모두 원본 SDK의 호환성을 가정하지 말고 표준 라이브러리 또는 최소 HTTP 의존성으로 작은 어댑터를 별도 검증해야 한다. KIS의 샘플 전체는 장비 Python과 불일치할 수 있다. |

## 권고

KIS를 기존 우선 후보로 유지한다. REST와 WebSocket, 모의 서버, 공식 종목 마스터 자료가 있어 요구 범위와 맞지만 사용자 키 발급이나 NAS 호환성이 확인된 것은 아니다. DEV는 먼저 offline/paper 환경 구분, 공통 데이터 계약, fake broker를 구현하고, 이후 계좌 준비 시 모의 인증·조회부터 연결한다. KIS의 세부 API 호출 한도와 계좌 비용은 연결 전에 최신 공지 및 계좌별 약정을 확인해야 한다.

키움은 공식 REST API와 모의투자를 갖춘 대안이다. 다만 허용 IP 등록 및 모의 KRX 한정 조건이 있다. NAS 공인 IP를 고정·등록할 수 있는지와 필요한 NXT 거래가 paper에 꼭 필요한지 OPS/사용자와 확인한 뒤 비교를 갱신한다.

## 확인 필요

- 사용자의 증권사 계좌, HTS ID 연결, API 서비스 신청, 모의계좌·키 발급 상태.
- NAS 외부 IP의 고정 여부와 키움 허용 IP 등록 가능성.
- 실제 NAS의 Python 버전·armhf 패키지/TLS 인증서 호환성.
- 개인 계좌의 수수료 약정 및 진행 중인 이벤트의 적용 대상·기간.
- paper에서 필요한 거래소와 API별 최근 호출 한도, 모의 데이터의 과거 구간·재배포 사용권.

이 문서는 공개 공식 자료의 사실과 구현 권고를 구분한다. 계좌 실측, 실제 수수료 조회, API 통신 검증은 하지 않았다.
