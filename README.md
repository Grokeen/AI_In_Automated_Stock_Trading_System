# AI_In_Automated_Stock_Trading_System

AI 모델을 활용한 주식 자동매매 시스템입니다.

## 개발 인계 문서

- [프로젝트 요청서](markdown/PROJECT_REQUEST.md): 목표, 사용자 요청과 설계 가정, 개발 범위, 단계별 산출물과 완료 기준.
- [프로젝트 정의서](markdown/PROJECT_DEFINITION.md): 현재 구현, NAS 환경, 제안 구조, 모듈·주문 복구 계약, 작업 분해와 검증·배포 방법.
- [역할별 업무 분장표](markdown/WORK_ALLOCATION.md): 배포관리·디자인·개발·감사·연구·문서의 담당 범위, 산출물, 검토·인계 순서와 첫 작업 지시.
- [개발 방법 정의서](markdown/DEVELOPMENT_METHOD.md): 작은 기능 단위 반복 개발, 인터페이스 설계, offline→paper→NAS 검증, 테스트·Git·배포·완료 기준.

다음 작업자는 위 네 문서와 최근 `UPDATE.md`를 먼저 확인하고 맡은 역할의 업무부터 진행합니다. 한국투자증권 KIS는 우선 연동 후보이며 계좌·API 키 준비 여부와 실제 연동은 미확인입니다.

## Raspberry Pi NAS 운영 환경

2026-11-08 03:22 KST 작성. 기존 OpenMediaVault NAS를 유지하면서 가벼운 주식 자동매매를 함께 실행하기 위한 운영 도구입니다.

현재 포함된 것은 NAS 상태 점검, 시스템 로그 용량 제한, 향후 매매 프로그램을 위한 systemd 실행 설정입니다. 증권사 API와 매매 전략은 아직 구현하지 않았습니다.

## 확인한 장비

- Raspberry Pi 4, RAM 약 4GB, OpenMediaVault 6.4.9.
- 커널 aarch64, 사용자 환경 armhf/32비트. 커널 정보만 보고 Python 패키지나 컨테이너 아키텍처를 선택하면 안 됩니다.
- Docker 24.0.4, cgroup v2. CPU 제한은 사용 가능하지만 memory 컨트롤러는 비활성입니다.
- 루트 파일시스템은 ext4이며 약 25GB 여유. 공유 저장장치 중 두 개는 100%, 97% 사용 중입니다.
- 개발 폴더 Z:는 NAS의 KYRNAS1 공유입니다. 이 폴더에 작성한 소스가 이미 NAS에서도 보이므로 별도 복제하지 않고, 검증 후 운영 파일만 설치합니다.

## 적용 항목

- `deploy/60-nas-trading.conf`: RAM에 올라오는 journal을 128MiB 이내, 파일당 16MiB, 최대 14일 보관하도록 제한합니다. 활성 파일 때문에 순간적으로 한도를 초과할 수 있습니다.
- `nas/apply.py`: 변경 전 journal을 root 전용 `/var/backups/nas-trading-maintenance/`에 압축 보관하고 모든 보관 파일의 SHA-256을 검증합니다. 설정을 설치한 뒤 folder2ram의 디스크 보관본도 동기화합니다.
- `nas/healthcheck.py`: 저장공간, 가용 메모리, 온도, NAS 서비스, 시각 동기화를 점검합니다. 매 5분 실행하며 최근 결과 한 개만 `/var/lib/nas-healthcheck/status.json`에 저장합니다. 외부 알림 전송 기능은 없습니다.
- `deploy/nas-trading.slice`: 향후 매매 프로세스 전체에 CPU 한 코어 상당의 사용량과 최대 64개 태스크를 배정합니다. 4코어 장비의 전체 CPU 용량 중 약 25%입니다.
- `deploy/nas-trader.service`: 향후 `/opt/nas-trader/main.py` 실행용 템플릿입니다. 자동 시작하지 않으며 현재 매매 프로그램은 없습니다.

`LimitAS=768M`은 **각 프로세스의 가상 주소공간 제한**입니다. 여러 프로세스가 사용하는 실제 메모리의 합계를 제한하지 않습니다. Docker의 `mem_limit`이나 systemd의 `MemoryMax`를 통한 전체 메모리 제한을 사용하려면 memory cgroup 활성화와 별도 검증이 필요합니다. 이번 작업은 부팅 설정을 변경하거나 재부팅하지 않습니다.

## 검증 및 배포

NAS에서 프로젝트 폴더로 이동한 뒤 실행합니다. 추가 Python 패키지는 필요하지 않습니다.

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q nas tests
sudo python3 nas/apply.py --check
sudo python3 nas/apply.py --apply
sudo systemctl status nas-healthcheck.timer --no-pager
sudo cat /var/lib/nas-healthcheck/status.json
sudo journalctl --disk-usage
```

상태 파일의 `critical`은 저장공간 부족 같은 장비 상태를 뜻합니다. 점검 작업 자체가 실패했다는 뜻은 아닙니다. 사용자 파일은 삭제하거나 이동하지 않습니다.

## 향후 증권사 연결

REST API를 지원하는 증권사를 선택한 뒤 ARM 사용자 환경에서 실행 가능한 Python 의존성을 검증합니다. 매매 코드는 `/opt/nas-trader/main.py`, 실행 중 데이터는 `/var/lib/nas-trader`를 사용합니다. 인증정보는 Git에 저장하지 않고 root 전용 `/etc/nas-trader/trader.env`에서 전달할 수 있습니다.

모의투자, 주문·체결 상태 복구, 중복 주문 방지와 손실 한도를 구현하고 검증한 뒤 매매 서비스를 활성화해야 합니다. 대규모 AI 학습과 백테스트는 별도 PC에서 수행하는 구성을 권장합니다.

## 실제 적용 결과

2026-11-08 03:29 KST 기준, NAS에서 테스트 9개와 Python 컴파일 검증을 통과했습니다. 재적용 시 변경 0건도 확인했습니다.

| 항목 | 적용 전 | 적용 후 |
|---|---:|---:|
| 활성 journal | 808MiB | 32MiB |
| `/var/log` RAM 사용 | 812MiB | 36MiB |
| 가용 메모리 | 2692MiB | 3460MiB |

Samba, OMV 엔진, nginx, Docker가 모두 정상 동작하며 상태 점검 타이머가 활성화되었습니다. 임시 테스트 프로세스로 CPU cgroup의 `cpu.max=100000 100000`, `pids.max=64`, 프로세스 주소공간 한도 805306368바이트를 확인했습니다. 실제 매매 서비스는 비활성입니다.

전체 과거 로그 98개의 검증된 보관본은 `/var/backups/nas-trading-maintenance/20261108T032602+0900/archived-journals.tar.gz`입니다. 최초 적용의 정리 명령이 실패해 설정이 복원되었지만 이 보관본은 유효합니다. 최종 성공한 배포 manifest는 `/var/backups/nas-trading-maintenance/20261108T032750+0900/manifest.json`입니다. 세부 검증 결과는 `reports/nas-validation-20261108.json`에 기록했습니다.

## 되돌리기

배포 결과의 `manifest.json`에 변경 전 파일 위치가 기록됩니다. `files`의 값이 경로인 항목은 보관 파일을 원래 위치로 복원합니다. 값이 `null`인 항목은 이번에 추가한 파일이므로 해당 파일만 제거합니다. 점검 타이머를 먼저 중지한 뒤 파일을 복원하고 `systemctl daemon-reload`, `systemctl restart systemd-journald`를 실행합니다.

옛 journal은 `archived-journals.tar.gz`에 별도 보관됩니다. RAM에 전부 복원하지 않고 임시 디스크 폴더에 압축을 푼 뒤 `journalctl --directory=<압축을 푼 journal의 machine-id 폴더>`로 조회할 수 있습니다. 보관본과 실제 로그는 GitHub에 올리지 않습니다.

## 공식 참고 자료

- [systemd journal 용량·보관 설정](https://www.freedesktop.org/software/systemd/man/249/journald.conf.html)
- [systemd CPU 및 cgroup 자원 제어](https://www.freedesktop.org/software/systemd/man/251/systemd.resource-control.html)
- [systemd 프로세스별 실행 제한](https://www.freedesktop.org/software/systemd/man/249/systemd.exec.html)
