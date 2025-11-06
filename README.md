# 시스템 리소스 모니터링 시스템

실시간으로 시스템 리소스를 모니터링하고 PDF 보고서를 생성하는 시스템입니다.

## 기능

- CPU 사용률 및 온도 모니터링
- GPU 온도 모니터링 (가능한 경우)
- 메모리 사용량 추적
- 디스크 사용량 및 I/O 추적
- 네트워크 트래픽 모니터링
- 실시간 UI 표시
- PDF 보고서 생성

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

```bash
python monitor.py
```

프로그램은 5분 동안 실행되며, 완료 후 `system_report.pdf` 파일이 생성됩니다.
