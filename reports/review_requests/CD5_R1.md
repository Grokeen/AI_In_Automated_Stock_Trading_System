# CD5 R1 문서 검증 요청

| 항목 | 내용 |
|---|---|
| 담당 / 업무 | CD5 / DOC-01~03 / R1 |
| 상태 | CD1 문서 범위 확인 완료 (2026-11-08 15:04 KST) |
| 기준 커밋 | `e166d64f9ad9c9ecd65d73258dd95cd64fb36a51` |
| 작성 | 2026-11-08 14:49 KST |

## 변경 범위

- `markdown/START_HERE.md`: 신규 작업자 읽기 순서, 현재 구현과 계획의 구분, 작업·검증·인계 방법 작성.
- `markdown/TEAM_STATUS.md`: 확인된 CD1~CD5 배정, OPS 미확인, 업무별 근거와 실제 확인 상태·후속 조치 작성.
- `README.md`: 시작 안내·팀 현황 진입 링크 추가 및 읽기 안내 갱신.
- `UPDATE.md`, `OWERORDER.md`: CD5 R1의 문서 변경과 검증 기록 추가.
- 제출 커밋은 생성하지 않았습니다. 아래 파일 SHA-256이 검토 대상 스냅샷을 식별합니다.

## 자체 검증 환경·방법·결과

- 환경: Windows PowerShell, 공유 작업 경로 `Z:\ProJect\AI_In_Automated_Stock_Trading_System`; 실제 NAS 장비에는 접속·변경하지 않음.
- 모든 변경 문서를 UTF-8로 다시 읽고 코드 펜스 짝과 대체문자 포함 여부를 PowerShell로 점검했습니다.
- Markdown 상대 링크가 가리키는 로컬 대상의 존재 여부를 점검했습니다. 링크 검사 첫 실행에서 루트 문서의 상대 경로를 해석하는 검사 스크립트 오류와 요청서 생성 전 참조를 발견했습니다. 이를 고치고 요청서 생성 후 재검사했으며, 아래 최종 결과와 같이 모든 내부 링크가 확인됐습니다.
- Python 문서검사 스크립트는 이 환경에서 `python` 호출 시 런타임을 시작하지 못하고 `Python`만 출력해 검사 결과를 얻지 못했습니다. Python 검사 통과로 보고하지 않습니다.
- 코드·실행 동작을 바꾸지 않았으므로 애플리케이션 테스트, NAS 테스트, KIS 실통신은 실행하지 않았습니다. 기존 NAS 테스트 9개는 새 기능 검증으로 사용하지 않았습니다.

## 범위·상태 근거와 제한

- CD1의 사용자 직접 지시 확인: 원본 채팅 `hostId=local`, `threadId=01a1b738-4c92-7353-8799-49838aa1eb51`; 지정 턴 `01a1b9ae-22b6-79c2-8310-45a24b7bb8df`, 사용자 메시지 `01a1b9ae-2331-70a1-8fe7-883fb17ce730`를 read_thread로 확인.
- 배정·업무 범위: `markdown/assignments/ROUND_01.md`, `markdown/WORK_ALLOCATION.md`.
- 구현·요구 상태: `markdown/PROJECT_DEFINITION.md`, `markdown/audit/ACCEPTANCE_MATRIX.md`.
- CD4의 초기 조사 기록은 `markdown/research/RES-01_INITIAL_FINDINGS.md`와 기존 UPDATE/OWERORDER 항목에서 확인했습니다. CD4의 R1 요청서, CD2·CD3의 R1 결과물은 이번 문서 확정 시점에 확인되지 않아 산출물 미확인으로 기록했습니다. OPS 배포관리 담당자도 미확인입니다.
- 계좌·키, 실통신, 현재 NAS 환경과 새 매매 서비스 공존, CD1 독립 판정은 미검증입니다.
- 개선 제안: 다음 문서 개정 시 `TEAM_STATUS.md`에 제출 일시·근거 SHA 및 CD1 판정 일시/재현 결과 열을 추가하고, 문서 버전 규칙을 기존 문서에 공통 정의하는 안을 검토할 수 있습니다. 이번에는 요청서·정의서·개발방법·분장표·임무 지시서·감사표를 수정하지 않았습니다.

## CD1 재현 방법

1. 저장소 루트에서 `markdown/START_HERE.md`, `markdown/TEAM_STATUS.md`, `README.md`, `UPDATE.md`, `OWERORDER.md`를 UTF-8로 엽니다.
2. 상대 링크의 실제 파일 존재, 코드 펜스 짝, 읽기 순서, 구현/계획 구분, CD1~CD5 및 OPS 배정 상태를 확인합니다.
3. 원본 근거 문서와 비교해 표의 상태가 실제 제출물·판정 범위를 넘지 않는지 확인합니다.
4. PowerShell에서 다음을 실행해 링크·구문을 재검사하고, 아래 SHA-256과 비교합니다.

```powershell
$paths = @('README.md','UPDATE.md','OWERORDER.md','markdown/START_HERE.md','markdown/TEAM_STATUS.md')
foreach ($p in $paths) {
  $t = Get-Content -LiteralPath $p -Raw -Encoding UTF8
  if (($t.Split('```').Count - 1) % 2 -ne 0) { throw "Unclosed code fence: $p" }
  if ($t.Contains([char]0xFFFD)) { throw "Bad UTF-8: $p" }
  foreach ($m in [regex]::Matches($t, '\[[^\]]+\]\(([^)]+)\)')) {
    $dest = $m.Groups[1].Value
    if ($dest -match '^[a-zA-Z][a-zA-Z0-9+.-]*:' -or $dest.StartsWith('#')) { continue }
    $target = ($dest -split '#')[0]
    $base = Split-Path $p
    if ([string]::IsNullOrEmpty($base)) { $full = $target } else { $full = Join-Path $base $target }
    if (-not (Test-Path -LiteralPath $full)) { throw "Broken link: $p -> $dest" }
  }
}
Get-FileHash -Algorithm SHA256 -LiteralPath $paths
```
## 제출 파일 SHA-256

최종 검증 후 아래 파일을 SHA-256으로 식별했습니다.

| 파일 | SHA-256 |
|---|---|
| `README.md` | `C23D9FFE44AC49E7E1BA4294FD5B9D296DFA86040171A4A7768B7EFB65C15ED7` |
| `UPDATE.md` | `FBFD625D2B21609FAD3479CE6A401433B51D8E000D62ABE20B85636139763C8C` |
| `OWERORDER.md` | `2CAFF4566DD51D8A59E46DA23844EC472481D967FFA3564A359CDE34158E0A8C` |
| `markdown/START_HERE.md` | `0FF6FC55407D07FD9908D736EE06005C8A36DF91F4A25B651A79145D20C27B19` |
| `markdown/TEAM_STATUS.md` | `7CBA542ADC7EF2F64F1D9CB4630A680968E1523FCC91C5AF8225CFF101F75DB3` |

요청 판정 범위: 문서 내용의 사실 상태 구분, 링크·UTF-8·Markdown 구문, 인계 재현성. 본 요청은 문서 자체 검토를 요청하며 매매 기능·NAS 호환·배포의 승인 판정을 요청하지 않습니다.







## CD1 최종 판정 — 2026-11-08 15:04 KST

CD1은 요청서 해시 `857D06D07618F096B482FEBA0BE56AAB3E34D6FE42F4E785FCF81F93A67F1CF6` 및 표의 문서 해시를 확인하고 UTF-8·코드 펜스·42개 내부 링크, 상태 구분·인계 설명을 재검토해 DOC-01~03 문서 범위 확인 완료를 판정했습니다. 자체검증 결과와 독립검토 결과는 UPDATE.md, OWERORDER.md 및 TEAM_STATUS.md에서 분리했습니다. 이번 판정은 문서 작업 범위에 한정됩니다.


## CD1 최종 재확인 — 2026-11-08 15:08 KST

CD1의 최종 재확인 기록은 `reports/reviews/CD5_R1_REVIEW.md`입니다. DOC-01~03 문서 인계 범위 확인 완료를 재확정했으며, 요청서의 해시 표는 이 최종 공통 기록 갱신 후의 본문 문서 SHA-256을 가리킵니다.

