# 운영 상태 명세 — DES-02·03

> 작성: 2026-11-08 15:05 KST · CD3 / 디자인 담당 · 기준 커밋 `e166d64f9ad9c9ecd65d73258dd95cd64fb36a51`
> 상태: DEV 구현 계약 초안. JSON/CLI 우선이며 웹 화면은 범위에 포함하지 않는다.
> 관련 흐름·재현 시나리오는 [운영 흐름](OPERATION_FLOW.md), 프로젝트 운영 요구는 [정의서](../PROJECT_DEFINITION.md)를 참조한다.

## 1. 용어와 상태 해석

| 용어 | 정의 |
|---|---|
| offline | 외부 브로커 연결 없이 가짜 브로커·고정/합성 응답으로 실행하는 개발·검증 모드. 실제 계좌 조회나 주문을 하지 않는다. |
| paper | 브로커 모의투자 환경에 명시적으로 연결하는 모드. 실계좌/실전 환경과 자격 증명을 공유하거나 자동 전환하지 않는다. |
| 최신(stale 아님) | 데이터 시각이 설정된 허용 나이 안에 있고, 시간대가 명시되며, 역순 갱신이 감지되지 않은 상태. 임계값은 구현 설정으로 노출한다. |
| 결과 불명(unknown) | 요청을 전송했을 수 있으나 접수·거절 여부를 확정할 응답이나 대사 결과가 없는 상태. 실패로 단정하거나 재전송하지 않는다. |
| 대사(reconciliation) | 로컬 주문·체결 기록과 브로커 조회를 비교해 일치/불일치/미확정을 판정하는 작업. |
| 미체결 | 브로커에서 접수됐지만 아직 체결되지 않은 잔량. 취소 요청 중인 주문도 최종 결과 전까지 별도 표시한다. |
| 새 주문 허용 | 게이트가 현재 신규 주문 전송을 허용하는지 나타내는 판정. 주문 전송 성공이나 수익성 보장을 뜻하지 않는다. |
| 연결 단절 | 브로커 통신이 현재 실패하거나 끊긴 상태. offline에는 연결 실패 대신 `not_applicable`을 쓴다. |

주문 생명주기 상태(예: `CREATED`, `SUBMITTING`, `ACKNOWLEDGED`, `PARTIALLY_FILLED`, `FILLED`, `CANCEL_PENDING`, `CANCELED`, `REJECTED`, `UNKNOWN`)와 전체 시스템 건강 상태는 별도 필드로 둔다. 브로커가 제공하지 않는 최종 상태는 임의로 추론하지 않는다.

## 2. 상태 출력 계약

상태 출력은 단일 시점의 스냅샷으로, 모든 시각은 ISO 8601 오프셋 포함 형식으로 저장한다. 운영자 표시는 Asia/Seoul을 기본으로 한다. 사용할 수 없는 시각은 null이며 생성 시각과 데이터 수신 시각을 혼합하지 않는다.

| 필드 | 형식·필수 | 의미·표시 |
|---|---|---|
| `schema_version` | 문자열, 필수 | 상태 구조 버전 |
| `observed_at` | 시각, 필수 | 이 상태 스냅샷 생성 시각 |
| `run.mode` | `offline` / `paper`, 필수 | 명시한 실행 모드. 누락·알 수 없는 값은 시작 오류 |
| `run.session_id` | 문자열, 필수 | 민감값 없는 실행 세션 식별자 |
| `run.started_at` | 시각, 필수 | 현재 프로세스 시작 시각 |
| `connection.state` | `not_applicable` / `connected` / `degraded` / `disconnected` / `unknown`, 필수 | 현재 paper 통신 상태; offline은 `not_applicable` |
| `connection.last_success_at` | 시각 또는 null, 필수 | 마지막 성공 통신 시각 |
| `market_data.state` | `fresh` / `stale` / `missing` / `error`, 필수 | 마지막 시세 데이터 품질·신선도 상태 |
| `market_data.last_received_at` | 시각 또는 null, 필수 | 마지막 유효 시세 수신 시각 |
| `market_data.max_age_seconds` | 정수, 필수 | stale 판정에 사용한 허용 최대 나이 |
| `account.state` | `fresh` / `stale` / `missing` / `error` / `not_applicable`, 필수 | 계좌·잔고 조회의 품질. offline에서 가짜 계좌가 있으면 fresh 등으로 표기하고 출처 구분 |
| `account.source` | `fake` / `paper_broker` / null, 필수 | 계좌 스냅샷 출처; 민감한 계좌번호 제외 |
| `account.last_fetched_at` | 시각 또는 null, 필수 | 마지막 유효 계좌 조회 시각 |
| `reconciliation.state` | `not_run` / `in_progress` / `matched` / `mismatched` / `unresolved` / `error`, 필수 | 저장 기록과 브로커 상태의 최근 대사 결과 |
| `reconciliation.last_completed_at` | 시각 또는 null, 필수 | 마지막 완료 대사 시각; 진행 중을 완료로 표시하지 않음 |
| `orders.open_count` | 음이 아닌 정수, 필수 | 미체결 또는 취소 최종 결과 대기 건수. `UNKNOWN` 건수는 별도 count 필드 포함 권장 |
| `orders.unknown_count` | 음이 아닌 정수, 필수 | 결과 불명으로 대사 전인 주문 수 |
| `storage.state` | `ok` / `degraded` / `read_only` / `unavailable` / `unknown`, 필수 | 영속 저장 경로의 현재 검사 결과 |
| `storage.last_write_success_at` | 시각 또는 null, 필수 | 마지막 영속 쓰기 성공 시각 |
| `new_orders_allowed` | 불리언, 필수 | 모든 주문 허용 조건의 종합 판정 |
| `stop_reasons` | 문자열 코드 배열, 필수 | 차단 사유 전부. 허용 시 빈 배열. 사람이 읽는 설명은 별도 메시지 필드로 제공 가능 |
| `operator.new_order_stop` | 불리언, 필수 | 운영자가 신규 주문 게이트를 명시적으로 닫았는지 여부 |
| `operator.stop_changed_at` | 시각 또는 null, 필수 | 운영자 중지 상태 변경 시각 |

최소 차단 코드: `MODE_INVALID`, `CONFIG_INVALID`, `RISK_LIMITS_MISSING`, `BROKER_DISCONNECTED`, `STALE_MARKET_DATA`, `STALE_ACCOUNT`, `RECONCILIATION_REQUIRED`, `UNKNOWN_ORDER`, `STORAGE_UNAVAILABLE`, `OPERATOR_STOPPED`. 여러 원인이 있으면 하나만 고르지 말고 모두 기록한다. 구현이 더 세분화하면 이 목록과 호환되는 코드를 추가한다.

## 3. 정상·장애 표시와 게이트 규칙

| 조건 | 사용자에게 보여줄 핵심 정보 | `new_orders_allowed` |
|---|---|---|
| offline 정상 | offline / 외부 연결 해당 없음 / 가짜 데이터 출처와 최신 시각 / 대사·저장·미체결 | 위험 한도·데이터·저장 등 모든 조건 통과 시에만 true; offline 결과를 paper 거래로 혼동하지 않음 |
| paper 정상 | 모의 환경 연결 / 시세·계좌·대사 각 성공 시각 / 미체결 건수 | 모든 필수 조건 통과 시 true |
| 시세 지연·누락 | 마지막 유효 시각, 경과 시간, stale 기준 | false, `STALE_MARKET_DATA` 또는 누락 코드 |
| 브로커 지연·단절 | 연결 상태, 마지막 성공 통신 시각, 재시도 상태 | false; 조회는 제한된 재시도·백오프 |
| 계좌 지연·오류 | 마지막 계좌 조회 시각·출처 | false, `STALE_ACCOUNT` |
| 주문 결과 불명·대사 필요 | 내부 주문 ID, 알고 있는 브로커 주문 ID, 마지막 조회·대사 시각, 확인할 조치 | false, `UNKNOWN_ORDER` / `RECONCILIATION_REQUIRED` |
| 저장 지연·쓰기 실패 | 저장소 상태·마지막 성공 쓰기 시각·오류 코드 | false, `STORAGE_UNAVAILABLE`; 주문 전송 뒤 실패는 unknown 복구 절차 |
| 중지 상태 | 신규 주문 중지 시각과 다른 활성 차단 이유 | false, `OPERATOR_STOPPED`; 기존 주문·보유는 변경하지 않음 |

`true`는 판정 시점의 게이트 결과다. 주문 전송 직전 다시 검사해야 하며 데이터가 바뀌거나 저장에 실패하면 차단한다. 재연결만으로 오래된 시세·계좌가 신선해지지 않는다. 대사 실패는 자동 해제하지 않는다.

## 4. 조작 용어의 경계

- **새 주문 중지**: 신규 주문 요청을 거부하도록 게이트를 닫고 원인·시각을 영속 기록한다. 이미 접수된 미체결 주문 취소나 보유 종목 매도는 수행하지 않는다.
- **미체결 취소**: 지정 주문 또는 운영자가 확인한 미체결 전체에 취소 요청을 보낸다. 요청 접수와 최종 취소 확정을 분리해 표시하고, 체결된 수량을 되돌리지 않는다.
- **보유 청산**: 선택한 보유 수량을 줄이거나 매도하는 거래 행위다. 새 주문 중지·통신 단절·저장 실패의 자동 결과로 실행하지 않는다. 별도 승인·한도 검증·연결·저장 가능 여부가 필요하다.

이 세 조작은 서로 다른 요청과 이벤트로 기록한다. 단일 `stop`/`emergency` 값만으로 취소·청산 의미를 암묵 결정하지 않는다.

## 5. DEV 구현 확인 시나리오 연결

세부 입력·기대 출력은 [운영 흐름의 OF-01~OF-11](OPERATION_FLOW.md#3-재현-가능한-확인-시나리오)을 사용한다. 특히 상태 JSON에서 다음을 직접 확인한다.

- OF-01/02: 모드, 연결 상태, 시세·계좌·대사 시각, `open_count=0`, 출처가 모드에 맞는지.
- OF-03/04: stale/단절 상태, 마지막 성공 시각 보존, 신규 주문 false 및 해당 사유 코드.
- OF-05/07: `unknown_count`, 주문 ID, 대사 결과·시각, 재전송 차단 지속.
- OF-06: 대사 결과 확정 후에만 게이트 재평가.
- OF-08: 저장 상태와 마지막 쓰기 시각, 영속화 실패 시 전송 차단/복구 상태.
- OF-09/10: 신규 중지·미체결 취소·보유 청산이 각각 별도 상태·이벤트이며 자동 연계되지 않는지.

이 문서와 [운영 흐름](OPERATION_FLOW.md)은 DES 설계 산출물이다. 구현 결과의 요구사항 충족 판정은 CD1 감사에서 별도로 수행한다.
