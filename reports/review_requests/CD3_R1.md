# CD3 R1 검증 요청

- 담당자 / 업무 ID: CD3 / DES-01~03 / R1 (디자인 담당)
- 관련 요구사항: REQ-05 시세 유효성, REQ-07 결과 불명·복구, REQ-08 새 주문 차단, REQ-09 운영 상태
- 기준 커밋: `e166d64f9ad9c9ecd65d73258dd95cd64fb36a51`
- 제출 커밋: 없음. 공유 저장소에 유효한 Git 메타데이터가 없어 본인 커밋을 만들지 않았음.
- 상태: CD1 검토 완료 (CD1 판정 전달 확인)
- 작성: 2026-11-08 14:50 KST · CD3 / 디자인 담당

## 변경 파일과 SHA-256

| 파일 | 변경 내용 | SHA-256 |
|---|---|---|
| `markdown/design/OPERATION_FLOW.md` | 모드 선택·연결·초기 조회·대사·운영 상태·중지/복구 흐름, DEV 입력/출력, OF-01~OF-11 재현 시나리오 | `29919A16A7FB7F6E6FA9714E2F1C527C4187CFE92F384FB316859A681912534F` |
| `markdown/design/STATUS_SPEC.md` | 상태 필드 계약, 용어·상태값, 게이트·차단 사유, 정지/취소/청산 조작 경계, OF 시나리오와 연결 | `55CE330257BBD365E35A4223598677C799169D58CE43D74FB8C15E0B2C9D55D1` |

## 자체 검증

- 환경: Windows PowerShell, 공유 작업 폴더 `Z:\ProJect\AI_In_Automated_Stock_Trading_System`. 온라인 브로커·NAS 실기는 사용하지 않음.
- 명령: `Get-FileHash -Algorithm SHA256 markdown/design/OPERATION_FLOW.md,markdown/design/STATUS_SPEC.md`
  - 결과: 두 파일 SHA-256 생성 완료(위 표).
- 명령: `rg -n '\]\([^)]*\)' markdown/design/OPERATION_FLOW.md markdown/design/STATUS_SPEC.md`
  - 결과: 문서 내 관련 링크 5개를 확인. 모두 상대 경로이며 각 목적 파일을 확인할 수 있음.
- 명령: `rg -n 'offline|paper|마지막|새 주문 중지|미체결 취소|보유 청산|결과 불명|저장' markdown/design/OPERATION_FLOW.md markdown/design/STATUS_SPEC.md`
  - 결과: 모드 구분, 시세·계좌·대사 시각, 미체결 수, 결과 불명, 저장 오류, 세 조작의 독립 의미와 기대 동작을 확인.
- 의미 교차 확인: OPERATION_FLOW OF-01~OF-11과 STATUS_SPEC의 필드·상태·시나리오 참조를 대조. stale·단절·결과 불명·복구·저장 실패 모두 신규 주문을 차단하며, 새 주문 중지·미체결 취소·보유 청산은 상호 자동 연계되지 않음.
- Git 메타데이터 확인: `git status --short -- markdown/design/OPERATION_FLOW.md markdown/design/STATUS_SPEC.md` 실행 결과 `fatal: not a git repository`. 지정된 미완성 `.git`/`config.lock`은 건드리지 않았고, 유효한 격리 Git checkout도 준비하지 못해 커밋은 제출하지 않음. 해시로 검토 요청.

## 실패·미지원·미검증 및 남은 문제

- 문서는 개발 인계용 설계이며 매매 상태 구현이나 동작 테스트 결과가 아님.
- KIS paper 연결·인증, NAS Python/armhf 호환성, NAS 실기, 실제 주문·취소·청산은 미검증. 실계좌 주문과 NAS 배포는 수행하지 않음.
- stale 판정 허용 시간, 위험 한도의 상세 필드, 운영자의 취소/청산 추가 승인 방식은 DEV 구현·요구 합의 시 확정할 설정/계약이다. 필수 조건의 불확실성은 주문 차단으로 정의했음.
- 상태 필드가 DEV의 공통 모델과 맞는지 구현 인계 후 교차 확인이 필요함.
- 기존 NAS 운영 도구의 테스트 9개는 실행하지 않았으며 이 제출의 검증으로 계산하지 않음.

## CD1 재현 방법

1. 기준 커밋의 작업 트리에서 위 두 파일을 열어 본 요청서의 표와 대조한다.
2. PowerShell에서 `Get-FileHash -Algorithm SHA256 markdown/design/OPERATION_FLOW.md,markdown/design/STATUS_SPEC.md` 실행 후 해시를 비교한다.
3. 링크·핵심 필드·조작 경계를 확인한다: `rg -n '\]\([^)]*\)|new_orders_allowed|stop_reasons|last_received_at|last_fetched_at|last_completed_at|open_count|unknown_count|last_write_success_at|새 주문 중지|미체결 취소|보유 청산|OF-0[1-9]|OF-1[01]' markdown/design/OPERATION_FLOW.md markdown/design/STATUS_SPEC.md`.
4. OF-01~OF-11의 입력 조건별 표시와 게이트 결과가 STATUS_SPEC와 일치하는지 확인한다.

요청 판정 범위: 문서 링크·상태 필드 누락·용어 의미 일관성·재현 시나리오가 DES-01~03 기준을 충족하는지 독립 검토 부탁드립니다.


## CD1 검토 결과

2026-11-08: CD1이 자체 메시지로 문서 SHA를 확인했고, 흐름·상태 필드·OF-01~OF-11 및 중지/취소/청산 구분이 설계 범위에 적합하다고 판정했다. 이 판정은 설계 검토 완료이며 구현 완성을 의미하지 않는다. 후속 DEV 구현에서 명시 실행 모드 계약, 공통 모델 및 실제 주문 게이트와 대조해야 한다. CD1 안내상 판정 기록 경로는 `reports/reviews/CD3_R1_REVIEW.md`이나 현재 공유 작업 폴더에서는 해당 파일을 찾지 못해, 여기에는 전달받은 판정 요지를 기록한다.
