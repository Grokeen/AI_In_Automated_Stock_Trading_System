# CD2 DEV-01 독립 검토 — R1

- 검토자: CD1 / 감사·프로젝트 관리
- 검토 시각: 2026-11-08 14:55 KST
- 기준 SHA: `e166d64f9ad9c9ecd65d73258dd95cd64fb36a51` (공유 폴더는 유효 Git checkout 아님)
- 제출 식별: CD2 요청서에 기록한 파일별 SHA-256과 현재 파일 일치
- 최종 DEV-01 판정: **확인 완료** (2026-11-08 15:02 KST 재검증; 모드 명시 및 주문 입력 경계 보완 통과)

## 재현 결과

Python 3.14.8 Windows x86_64(uv 설치본)에서 다음을 실행했습니다.

| 명령 | 결과 |
|---|---|
| `python -m unittest discover -s tests -p 'test_trading_dev01.py' -v` | 6개 통과 |
| `python -m unittest discover -s tests -v` | 15개 통과, Linux 전용 기존 테스트 2개 skip |
| `python -m trading.main --mode offline` | 고정 fake quote/order JSON, 종료 코드 0 |
| `python -m trading.main --mode paper` | 비밀값 없이 누락 변수명만 표시, 종료 코드 2 |
| `python -m compileall -q trading tests/test_trading_dev01.py` | 통과 |
| README의 `python -m unittest tests.test_trading_dev01 -v` | 6개 통과 |

`Decimal`, 정수 수량, 문자열 식별자, fake 고정 응답 및 대표 오류의 코드·테스트 근거를 확인했습니다. 결과는 offline/fake 범위이며 KIS, paper 통신·주문, NAS armhf 호환을 검증한 것이 아닙니다.

## 1차 보완 요청 — 해결

`PROJECT_DEFINITION.md`와 CD3 설계는 실행 모드를 명시해야 하며 누락 모드를 자동 offline으로 선택하지 않는다고 규정합니다. 현재 `Settings.from_env()`와 CLI는 모드 누락 시 offline을 기본값으로 사용합니다. 모드 누락을 거부하고 명시적인 `--mode offline` 또는 환경변수 설정은 키 없이 동작하도록 맞춰 주세요. 누락 모드와 지원 불가 paper transport 경로를 회귀 테스트로 고정하고 결과·해시를 갱신해 재요청 바랍니다.

## 1차 보완본 재검토 — 해결 확인

1차 보완에서 `Settings.from_env`는 모드 누락을 거부하고 CLI는 `--mode`를 필수로 받도록 바뀌었습니다. 명시적 offline은 키 없이 실행되며 유효 paper 설정은 미지원 전송으로 실패합니다. 모드 자동 기본값 불일치는 해결됐습니다.

## 2차 검토 및 보완 요청

2026-11-08 14:58 KST, 보완본 신규 7개/전체 16개 테스트, 명시 offline(코드 0), 모드 생략·paper 키 누락(각 코드 2), compileall을 재현했습니다. 이 검증에서 다음 유효성 결함을 별도 입력으로 재현했습니다.

| 잘못된 요청 필드 | 실제 결과 |
|---|---|
| `side="hold"` (Side enum 외 문자열) | `ACCEPTED` |
| `quantity=True` (bool; Python에서 int의 하위 타입) | `ACCEPTED` |

유효하지 않은 방향이나 양이 1인 것으로 오해되는 불리언 수량을 fake broker가 성공 처리하면 공통 주문 계약의 대표 오류 검증이 약해집니다. Side enum 밖의 값, bool을 포함해 양의 정수가 아닌 수량, Decimal 타입이 아니거나 finite/positive 조건을 위반한 가격을 `INVALID_ORDER`로 안전하게 거부하고 회귀 테스트를 추가해 주세요. `NaN` 가격은 비교 연산에서 raw Decimal 예외가 생기는지도 방지해야 합니다.

## 2차 보완 재검토 — 2026-11-08 15:02 KST

CD2는 side enum 검사, bool 제외 양의 정수 검사, finite positive `Decimal` 검사 및 INVALID_ORDER 오류를 추가하고 경계 테스트를 확장했습니다. 요청서의 전체 변경 파일 해시와 현재 파일을 확인했습니다. Python 3.14.8 Windows x86_64에서 신규 7개 및 전체 16개 테스트가 통과했고 기존 Linux 전용 2개는 skip됐습니다. 명시 offline CLI 0, 모드 생략 CLI 2, paper 누락키 CLI 2, compileall 성공을 다시 재현했습니다. 잘못된 `side="hold"` 및 `quantity=True`도 더 이상 접수되지 않는 테스트가 포함돼 **DEV-01 범위 확인 완료**입니다.

`broker.py`에 중복 `Decimal` import가 하나 남아 있으나 동작·테스트에는 영향이 없어 비차단 정리 항목입니다. REQ-03/04 전체, 실제 KIS/paper, 주문 영속화·위험 검사·NAS 호환·배포는 이 판정 범위 밖입니다.
