# CD4 R1 검토 요청

- 역할 / 업무 ID: RES / RES-01, RES-02
- 담당: CD4
- 상태: 자체 검토 완료 · CD1 검토 대기
- 기준 커밋: `e166d64f9ad9c9ecd65d73258dd95cd64fb36a51` (라운드 지시 기준). 로컬 경로에서 `git rev-parse HEAD`가 “not a git repository”로 실패해 체크아웃 기준과의 동일성은 확인하지 못함.
- 제출 커밋: 없음. 공유/원격 Git 메타데이터를 건드리지 않았음.

## 변경 파일 및 SHA-256

| 파일 | SHA-256 |
|---|---|
| `markdown/research/BROKER_COMPARISON.md` | `68B1C4A72F54F700C0C11E32B5F7F631ADCA685480450BF9D6DC56BE64D6F83E` |
| `markdown/research/STRATEGY_RESEARCH.md` | `6D4CDF7FFCDC762B8B06F6E9C3DF4678B981C095809D6B766F37C141B07C89A9` |
| `reports/review_requests/CD4_R1.md` | 681514901EE976EF02266B66105F1507AFC5291169331A5BD8DF3A4FEF30C7A5 |

## 결과 요약

- KIS 공식 API 구조, 신청, 샘플 Python 요구조건, 유량 공지, 비용 안내를 대조하고 키움 REST API의 IP 등록·모의투자·호출 제한·지원 기능과 비교했습니다.
- 고정 수수료율이나 KIS 전체 API에 적용할 단일 유량 한도를 임의로 확정하지 않았습니다. 계좌/공지 확인이 필요한 항목은 명시했습니다.
- KRX 거래 세션 사실과 분리해 20/60 일봉 교차를 테스트 파이프라인용 예시로 제안하고, 데이터 입력·체결 가정·비용 민감도·표본 외 절차·편향 점검을 기록했습니다.
- 실거래 제안, 수익 보장, 개인 투자금·손실 한도 결정은 포함하지 않았습니다.

## 자체 검증

- 환경: Windows PowerShell, 프로젝트 공유 경로 `Z:\ProJect\AI_In_Automated_Stock_Trading_System`, 2026-11-08 KST. API 호출·계좌 인증·NAS 접속 없음.
- 명령: `Get-Content -Raw -Encoding utf8 <file>`로 UTF-8 읽기; `([regex]::Matches($text,'```')).Count % 2`로 fence 짝 확인; `Get-FileHash -Algorithm SHA256 <file>`로 제출 해시 계산.
- 결과: 두 문서 UTF-8 읽기 성공, 코드 fence는 각각 0쌍(짝수), 해시 산출 완료. 두 문서의 주요 공식 링크를 조사 중 직접 검색/열람해 주장에 대응시킴. 전략 문서의 KRX 세션 및 KIS API 요약 링크도 출처로 연결함.
- 링크별 주장은 표/문단의 동일 행 또는 문장 끝에 해당 공식 링크를 배치했습니다. 현재 외부 페이지는 계정별 세부 조건·공지가 바뀔 수 있어 구현 직전 재확인이 필요합니다.

## 미검증·미해결

- `assignments/ROUND_01.md`와 `audit/ACCEPTANCE_MATRIX.md`는 지시된 경로에 존재하지 않아 읽지 못했습니다. 유사 경로 `markdown/assignments/ROUND_01.md`, `markdown/audit/ACCEPTANCE_MATRIX.md`가 존재할 수도 있으나 임무 범위 파일로 수정하지 않았습니다.
- 사용자 계좌/키/HTS ID 상태, KIS 계정별 최신 호출 유량·수수료, 데이터 제공·사용권, NAS 실제 Python/armhf와 TLS 호환성 미확인.
- 전략 백테스트·시세 조회·paper 모의 통신 및 성능 검증 미실시. 수치 성과 결론 없음.
- README/UPDATE/OWERORDER는 CD5 취합 영역이므로 이번 라운드에서 수정하지 않았습니다.

## CD1 재현 방법

1. `markdown/research/BROKER_COMPARISON.md`와 `markdown/research/STRATEGY_RESEARCH.md`를 UTF-8로 읽습니다.
2. 공식 링크를 열어 비교표의 API 서버·인증·요율/유량 및 전략 문서의 거래 세션 사실을 확인합니다.
3. 위 SHA-256을 `Get-FileHash -Algorithm SHA256 <path>`로 재산출합니다.
4. 판정 시 계좌 조건과 미확인 환경 조건을 분리하고, 숫자 한도·요율의 확정 근거가 충분한지 확인합니다.

다음 역할: CD1 독립 검토. 후속 구현은 DEV 담당자가 RES-01 조건을 DEV-02 어댑터와 DEV-04 검증 가정에 반영하고, 계좌 조건 확보 후 paper 조회를 확인합니다.

