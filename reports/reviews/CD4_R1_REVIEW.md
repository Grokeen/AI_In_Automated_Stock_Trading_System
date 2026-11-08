# CD4 RES-01~02 독립 검토 — R1

- 검토자: CD1 / 감사·프로젝트 관리
- 검토 시각: 2026-11-08 14:55 KST
- 제출 식별: CD4 요청서 및 산출물의 SHA-256과 현재 파일 일치
- 상태: **조사·실험 계획 범위 확인 완료 · 계정 조건은 구현 전 재확인**

## 공식 자료 확인

2026-11-08에 주요 공식 출처를 열어 문서의 주요 주장을 대조했습니다.

- [KIS API 구조](https://apiportal.koreainvestment.com/apiservice-summary)는 REST/WebSocket, 모의·실전 도메인, REST TLS 1.2/1.3, App Key/Secret 인증, 주문·계좌·시세 범주를 안내합니다. [KIS 공식 Python 예제 README](https://github.com/koreainvestment/open-trading-api/blob/main/README.md)는 Python 3.11 이상을 명시합니다.
- [키움 REST API 소개·유량](https://openapi.kiwoom.com/intro)는 국내 실전 주문/조회 각 초당 5회, 국내 모의투자 TR별 초당 1회 및 계좌별 세션 조건을 안내합니다. [키움 이용 안내](https://openapi.kiwoom.com/intro/serviceInfo)는 API 신청·허용 IP·별도 실전/모의 키 조건을 설명하고, [모의투자 안내](https://openapi.kiwoom.com/intro/mockInvestInfo)는 국내 모의 매매·계좌 조회가 KRX로 제한됨을 확인해 줍니다.
- [KRX 거래시간 안내](https://global.krx.co.kr/contents/GLB/06/0602/0602020204/GLB0602020204T1.jsp)의 정규장 09:00~15:30은 전략 문서 설명과 일치합니다.

문서는 KIS의 단일 호출 한도·고정 수수료를 추정하지 않고, 개인 계좌 조건·사용권·장비 호환을 미확인으로 남겼습니다. 전략 문서는 20/60 이동평균을 파이프라인 예시로만 제시하며 백테스트나 수익 결과를 주장하지 않고, 비용·슬리피지·생존편향·데이터 누출·표본 외 검증 조건을 명시합니다.

## 한계와 판정

Git 메타데이터가 없어 기준 SHA와 diff를 확인하지 못했습니다. CD4가 지적한 ROUND_01/ACCEPTANCE_MATRIX 경로 미발견은 현재 프로젝트의 `markdown/` 접두 경로와 작업 디렉터리 기준 차이입니다.

RES-01/02 문서 조사·실험계획 범위는 확인 완료입니다. 실제 계좌별 한도·비용, KIS paper 통신, 데이터 사용권, NAS armhf, 백테스트 성과는 검증되지 않았고 문서도 이를 확인했다고 주장하지 않습니다. API 조건은 구현 직전 공식 자료와 계좌별 화면에서 다시 확인해야 합니다.
