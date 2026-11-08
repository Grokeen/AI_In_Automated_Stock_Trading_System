# CD2 검증 요청 — DEV-01 / R1

작성: 2026-11-08 15:25 KST — CD2 / 개발 담당  
상태: 보완 완료 · CD1 재검토 대기

## 범위

실행 모드·설정 검증, 공통 데이터 모델, 결정적인 가짜 브로커, 최소 offline 실행 경로를 구현했습니다. 관련 요구사항은 REQ-03·REQ-04이며 전체 요구사항 완료를 뜻하지 않습니다.

기준 커밋은 `e166d64f9ad9c9ecd65d73258dd95cd64fb36a51`입니다. 공유 폴더의 `.git`은 유효한 Git 저장소가 아니므로 커밋은 만들지 않았고, 아래 검토 파일의 SHA-256을 제출합니다.

변경 파일:

- `trading/__init__.py`
- `trading/models.py`
- `trading/config.py`
- `trading/broker.py`
- `trading/main.py`
- `trading/README.md`
- `tests/test_trading_dev01.py` (신규)

## 계약과 동작

- 모드는 CLI의 `--mode` 또는 `TRADER_MODE`로 명시해야 합니다. 생략 시 실행을 거부합니다. 명시한 `offline`은 외부 통신·키 없이 `fake` 브로커만 허용하며 샘플 가격·시각·주문 ID는 고정되어 재현 가능합니다.
- `paper`는 `kis-paper`와 계좌 ID·App Key·App Secret을 요구하며 누락·브로커 불일치에서 닫힌 방식으로 실패합니다. CLI는 사용자 비밀정보를 출력하지 않고 종료 코드 2를 반환합니다.
- `live`는 지원 모드로 받아들이지 않습니다. 어떤 설정 실패도 모드 자동 전환을 일으키지 않습니다.
- 가격·금액은 `Decimal`, 수량은 양의 정수, 계좌·종목·주문 식별값은 문자열로 계약했습니다. 오류 코드는 `SYMBOL_UNKNOWN`, `INVALID_IDENTIFIER`, `INVALID_ORDER`, `DUPLICATE_CLIENT_ORDER_ID`입니다.
- 다음 DEV 작업은 `Broker` Protocol의 `get_quote`·`submit_order`를 구현하고 공통 모델을 이어 쓸 수 있습니다.

## 자체 검증

환경: Windows 11 개발 PC, Python 3.14.8 (`uv python find` 경로), 로컬 작업 폴더. NAS의 Raspberry Pi/armhf 환경에서는 실행하지 않았습니다.

| 명령 | 실제 결과 |
|---|---|
| `python -m unittest discover -s tests -p 'test_trading_dev01.py' -v` | 신규 테스트 7개 통과. 모드 누락, paper 전송 미지원, 잘못된 direction·bool 수량·비 Decimal/NaN/무한대/비양수 가격 거부 포함 |
| `python -m unittest discover -s tests -v` | 전체 16개 OK, 기존 Linux 전용 배포 테스트 2개 skip. 기존 운영 도구 9개가 매매 기능 검증에 포함된다고 계산하지 않음 |
| `python -m trading.main --mode offline` | JSON 시세·가짜 주문 결과 출력, 코드 0 |
| `python -m trading.main` | 모드 선택 필수 오류, 코드 2 |
| `python -m trading.main --mode paper` | `paper mode missing required credentials: TRADER_ACCOUNT_ID, TRADER_APP_KEY, TRADER_APP_SECRET`, 코드 2 |
| `python -m compileall -q trading tests/test_trading_dev01.py` | 성공 |

## 제한·미검증

KIS HTTP/인증/모의 서버는 구현하지 않았고 API 실통신은 검증하지 않았습니다. paper에 유효한 인증정보가 있을 때의 전송 경로는 아직 미지원입니다. NAS의 Python 버전·armhf 호환성, 운영 배포, 영속 주문·위험 한도도 이 업무 범위에서 검증하지 않았습니다. 샘플 계좌 ID는 fake 요청용 문자열이며 실계좌 정보가 아닙니다.

## CD1 재현 방법

저장소 루트에서 `python -m unittest discover -s tests -p 'test_trading_dev01.py' -v`, `python -m trading.main --mode offline`, `python -m trading.main`, `python -m trading.main --mode paper`, `python -m compileall -q trading tests/test_trading_dev01.py`를 실행합니다. 모드 생략 및 paper 자격증명 누락 모두 종료 코드 2가 예상 결과입니다. 테스트에는 유효한 가짜 paper 설정을 실행해 미지원 전송 오류로 닫히는 회귀 검사도 포함합니다.

## 제출 파일 SHA-256

```text
388BCDD9A40BCCD5C069B7DED539F4175085A870BFD06B047064813A7EDFEDC6  trading/__init__.py
24B6AB013997BD55853AEE9AFFC9FA2AAC047EBE182C1EC0D80629007F19BD25  trading/broker.py
AE31300DD5F4A7C819592ACF1F51DA24647A81BF3D9D8A55201BF1A35CBF1ED2  trading/config.py
1E310C91FBC59AE3A9347400BA071E55BF6C1A7868E655816B2E4C5F2D43F59A  trading/main.py
5EECCC2ACF636025E9C152430327ADCF275E6036789D92E5EED0EEAEE0F80DC4  trading/models.py
3612364DBABE24805DB4230F84F535096A1BD593684C71BF48383AFA39D0F4E4  trading/README.md
951ED35C1533DC66B871221A54CF4F5F20A9BB61588C0667851D5C63C21EAE27  tests/test_trading_dev01.py
```

## CD1 보완 요청 반영

CD1이 모드 생략 시 offline 자동 선택되는 점을 지적했습니다. `Settings.from_env`는 `TRADER_MODE`가 없으면 `ConfigError`를 내고, CLI는 `--mode`를 필수 인자로 받도록 수정했습니다. 회귀 테스트는 환경 설정과 CLI 양쪽의 모드 누락을 확인하며, 명시적 offline은 키 없이 통과합니다. 유효한 가짜 paper 설정을 `run()`에 전달하면 paper 전송이 미구현임을 명시하고 실패하는 경로도 테스트합니다. 보완 검증에서 신규 7개 통과, 전체 16개 OK(기존 Linux 전용 2개 skip), compileall 성공을 확인했습니다.

재검토 요청: 모드 명시 요구, paper 미지원 경로, 갱신된 테스트·SHA-256을 확인해 주세요.

## CD1 추가 경계 입력 요청 반영

`FakeBroker.submit_order`가 Side enum 외 방향과 bool 수량을 승인하던 문제를 수정했습니다. 이제 방향은 `Side`, 수량은 bool을 제외한 양의 int, 가격은 유한하고 양수인 `Decimal`이어야 합니다. 잘못된 경계 입력은 비교 예외 대신 `BrokerError(code="INVALID_ORDER")`로 거부합니다. 문자열 direction, bool 수량, float 가격, NaN, Infinity, 0·음수 가격과 0 수량 회귀 사례를 추가했습니다. 재검증은 신규 7개 통과, 전체 16개 OK(기존 Linux 전용 2개 skip), compileall 성공입니다. 상단 제출 해시는 이번 보완 후 파일 기준으로 갱신했습니다.

재재검토 요청: FakeBroker 주문 입력 검증과 경계 테스트, 최신 SHA-256을 확인해 주세요.
