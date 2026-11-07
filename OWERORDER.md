# 작업 보고

2026-11-08 03:22 KST

라즈베리파이 4 NAS의 자동매매 병행 운영을 위한 운영 도구를 작성했습니다. 장비에 가용 메모리는 있으나, RAM 기반 로그 누적과 공유 디스크 두 개의 공간 부족을 확인했습니다.

이번 변경은 로그의 검증된 보관본을 남기고 활성 로그 용량을 줄이며, 5분 주기 상태 점검과 향후 매매 프로그램의 CPU 사용 한도를 준비합니다. 매매 프로그램은 아직 없으며 증권사 API 연결과 실제 주문 실행은 포함하지 않습니다.

검증 명령은 `python3 -m unittest discover -s tests -v`, `python3 -m compileall -q nas tests`, `sudo python3 nas/apply.py --check`입니다. 배포 후 `sudo cat /var/lib/nas-healthcheck/status.json`, `sudo journalctl --disk-usage`, `systemctl is-active smbd nginx docker openmediavault-engined`로 결과를 확인합니다.

전체 메모리 강제 제한에는 memory cgroup 활성화가 필요합니다. 현 설정의 768MiB 한도는 프로세스별 가상 주소공간 한도입니다. 공간이 부족한 두 공유 디스크는 데이터 정리가 필요하며 이번 작업에서 사용자 파일을 이동·삭제하지 않습니다.

GitHub 반영은 대상 저장소 확인 후 진행합니다. 배포·검증 결과는 작업 완료 후 아래에 추가합니다.

## 완료 보고 — 2026-11-08 03:29 KST

운영 설정을 NAS에 적용하고 테스트 9개, Python 컴파일, systemd 설정과 실제 자원 제한을 검증했습니다. 재적용 시 변경 0건을 확인했습니다.

시스템 journal을 808MiB에서 32MiB로 줄였고 가용 메모리는 2692MiB에서 3460MiB로 증가했습니다. 전체 과거 journal 98개는 root 전용 보관본에 압축 저장하고 SHA-256으로 검증했습니다. folder2ram의 디스크 사본도 동기화했습니다.

Samba, OMV 엔진, nginx, Docker는 모두 정상입니다. 5분 주기 상태 점검을 활성화했고, 향후 자동매매 작업에 적용할 CPU 한 코어·태스크 64개·프로세스별 가상 주소공간 768MiB 제한의 실제 동작을 확인했습니다.

배포한 소스와 검증 결과를 사용자 지정 GitHub 저장소 `Grokeen/AI_In_Automated_Stock_Trading_System`의 main에 반영했습니다. 운영 소스 커밋은 `99aa8a2`이며 원격 브랜치에서 확인했습니다. 비밀정보, 로그 원문, 압축 보관본은 포함하지 않았습니다.

증권사 API와 실제 매매 코드는 아직 구현하지 않았습니다. 저장공간 부족 디스크 2개와 비활성 memory cgroup은 남아 있으며, 현 점검 결과의 `critical`은 저장공간 부족을 정확히 표시한 것입니다. 기존 부팅 시 네트워크 대기 서비스의 실패 상태도 후속 점검 대상으로 기록했습니다.
