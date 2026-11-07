# 개발 기록

## 2026-11-08 03:22 KST

- SSH로 Raspberry Pi 4 NAS를 점검했습니다. RAM 약 4GB, OMV 6.4.9, 32비트 armhf 사용자 환경, Docker memory cgroup 비활성을 확인했습니다.
- 공유 저장장치의 100%·97% 사용률과 RAM 기반 `/var/log`의 journal 약 808MiB 누적을 확인했습니다.
- `nas/healthcheck.py`: 읽기 전용 상태 수집, 저장공간·메모리·온도·NAS 서비스·NTP 점검, 원자적 상태 파일 저장을 추가했습니다.
- `nas/apply.py`: 동시 설치 방지 잠금, 기존 설정 보관, journal 압축 및 SHA-256 검증, systemd 검증, folder2ram 동기화, 오류 시 설정 복원을 추가했습니다.
- `deploy/60-nas-trading.conf`: journal 용량과 보관 기간 제한을 추가했습니다.
- `deploy/nas-healthcheck.service`, `deploy/nas-healthcheck.timer`: 5분 주기 상태 점검을 추가했습니다.
- `deploy/nas-trading.slice`, `deploy/nas-trader.service`: 향후 매매 프로세스의 CPU 예산과 비활성 실행 템플릿을 추가했습니다.
- `tests/test_healthcheck.py`: 장비 상태 판정과 상태 파일 손상 방지 테스트를 추가했습니다.
- `.gitignore`, `README.md`, `OWERORDER.md`: 인증정보 제외 규칙, 적용·검증·복구 방법, 작업 보고를 작성했습니다.
- 기존 NAS 데이터, 공유 설정, 기존 Docker 컨테이너와 부팅 설정은 변경하지 않습니다.
- 초기 작업 폴더의 `.git`은 HEAD가 없는 미완성 상태이며 `config.lock`이 존재합니다. 다른 작업자의 잠금일 수 있으므로 수정하지 않았습니다. GitHub 대상 저장소는 사용자 답변을 기다립니다.

## 2026-11-08 03:29 KST

- 사용자 지정 GitHub 대상 `Grokeen/AI_In_Automated_Stock_Trading_System`을 확인했습니다. 기존 main에는 프로젝트 소개 README만 존재하여 소개를 보존하고 운영 문서를 추가했습니다.
- 최초 journal 정리 명령의 일시 실패로 설정 자동 복원이 실행됐습니다. 원본 journal 98개는 SHA-256 검증을 마친 보관본에 남아 있습니다.
- `nas/apply.py`: journal 대몬 동기화 후 정리하며, 실패 시 한 번 재시도하고 반복 실패는 계속 오류로 처리하도록 보완했습니다. 오류 출력의 끝부분을 보존하고 미설치 타이머 조회의 불필요한 오류 출력을 줄였습니다.
- `tests/test_apply.py`: 일시 실패 복구와 지속 실패 시 중단을 검증하는 회귀 테스트 2개를 추가했습니다.
- NAS에서 테스트 총 9개, Python 컴파일, systemd 설정 검증을 통과했습니다. Windows에서는 상태 점검 테스트 7개 통과, Linux 전용 테스트 2개는 의도대로 제외됐습니다.
- 운영 설정을 NAS에 적용했습니다. 최종 manifest는 `/var/backups/nas-trading-maintenance/20261108T032750+0900/manifest.json`입니다.
- 활성 journal 808→32MiB, `/var/log` 812→36MiB, 가용 메모리 2692→3460MiB를 확인했습니다. folder2ram 디스크 보관본도 37MiB로 동기화됐습니다.
- 기존 Samba·OMV 엔진·nginx·Docker 서비스 정상, 5분 주기 점검 정상 종료, 재적용 시 변경 0건을 확인했습니다.
- 임시 프로세스로 CPU 한 코어 한도, 태스크 64개 한도, 프로세스별 가상 주소공간 768MiB 한도의 커널 실효값을 확인했습니다.
- `reports/nas-validation-20261108.json`: 비밀정보와 로그 원문을 제외한 장비·배포·검증 결과를 추가했습니다.
- `README.md`, `OWERORDER.md`: 운영 결과, 과거 로그 보관본, 미해결 항목을 보완했습니다.
- GitHub에는 지정한 소스·문서·검증 결과만 반영합니다. 미완성 로컬 `.git`과 잠금은 유지하고 별도 Git 메타데이터에서 기존 main을 이어서 커밋합니다. 강제 푸시는 사용하지 않습니다.
- 남은 항목: 증권사 선택 및 API 구현, 공간이 부족한 공유 디스크의 데이터 정리, 필요 시 memory cgroup 활성화와 OS 유지보수 계획입니다. 기존 `systemd-networkd-wait-online` 실패 상태도 확인했으며 네트워크 설정은 변경하지 않았습니다.

## 2026-11-08 03:31 KST

- GitHub 연결 도구의 Git tree 생성 요청이 쓰기 권한 오류 403으로 거절되어, PC의 기존 Git 인증을 사용하는 경로로 전환했습니다. 대상 저장소와 검증한 소스 범위는 동일합니다.
- `.gitattributes`: Windows의 Git 설정에 영향을 받지 않도록 텍스트 파일의 LF 줄바꿈을 고정했습니다. Linux 운영 파일의 내용과 Git 보관본이 일치하도록 했습니다.

## 2026-11-08 03:33 KST

- GitHub main에 운영 소스 커밋 `99aa8a2549be663fd07bd2fbfb67bf5eb38e7b00`을 정상 반영했습니다. 원격 브랜치 SHA와 로컬 커밋 SHA가 일치함을 확인했습니다.
- `OWERORDER.md`, `reports/nas-validation-20261108.json`: GitHub 반영 완료 상태와 운영 소스 커밋을 기록했습니다.
