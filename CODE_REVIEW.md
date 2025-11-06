# 시스템 리소스 모니터링 시스템 - 코드 리뷰 보고서

**리뷰 날짜**: 2025-11-06
**리뷰 대상**: 전체 프로젝트 코드베이스
**리뷰 초점**: 보안 취약점, 코드 품질, 성능, 유지보수성

---

## 🔴 심각한 보안 문제점 (Critical Security Issues)

### 1. 파일 경로 인젝션 취약점 (Path Traversal)
**위치**: `pdf_generator.py:22-29`

```python
def __init__(self, filename: str = "system_report.pdf"):
    self.filename = filename
    self.doc = SimpleDocTemplate(filename, ...)
```

**문제점**:
- 사용자가 제공한 파일명을 검증 없이 그대로 사용
- Path Traversal 공격 가능: `PDFReportGenerator("../../etc/passwd")`
- 시스템의 임의 경로에 파일 쓰기 가능
- 기존 시스템 파일 덮어쓰기 위험

**영향도**: 🔴 **Critical** - 시스템 파일 손상, 권한 상승 가능

**권장 사항**:
- 파일명에서 경로 구분자 제거 (`os.path.basename()` 사용)
- 출력 디렉토리 화이트리스트 지정
- 절대 경로 사용 금지
- 파일명 정규화 및 검증

---

### 2. 민감한 시스템 정보 노출
**위치**: `system_monitor.py:139-161`

```python
def get_process_info(self) -> Dict[str, Any]:
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        pinfo = proc.info
        processes.append({
            'pid': pinfo['pid'],
            'name': pinfo['name'],  # ← 프로세스 이름 노출
            ...
        })
```

**문제점**:
- 실행 중인 모든 프로세스 정보 수집 및 PDF로 출력
- 보안 소프트웨어, 관리 도구 실행 여부 노출
- 시스템 구성 및 취약점 파악에 악용 가능
- 네트워크 연결 정보도 수집 (`psutil.net_connections()`)

**영향도**: 🟠 **High** - 정보 유출, 프라이버시 침해

**권장 사항**:
- 프로세스 정보 수집 시 권한 확인
- 민감한 프로세스 필터링 (예: 시스템 프로세스, 보안 도구)
- 네트워크 연결 정보 수집 제한 또는 익명화
- 사용자 동의 필요

---

### 3. 예외 처리에서 정보 누출
**위치**: `monitor.py:142-144`

```python
except Exception as e:
    print(f"  ✗ PDF 보고서 생성 실패: {e}")
    import traceback
    traceback.print_exc()  # ← 전체 스택 트레이스 출력
```

**문제점**:
- 상세한 에러 메시지와 스택 트레이스 노출
- 시스템 경로, 파일 구조, 내부 구현 정보 유출
- 공격자가 시스템 구조 파악 가능

**영향도**: 🟡 **Medium** - 정보 수집, 공격 표면 확대

**권장 사항**:
- 프로덕션 환경에서 상세 에러 메시지 숨김
- 로그 파일에만 상세 정보 기록
- 사용자에게는 일반적인 에러 메시지만 표시
- 디버그 모드와 프로덕션 모드 분리

---

### 4. 권한 없는 시스템 정보 접근
**위치**: `system_monitor.py:75-112`

```python
def get_disk_info(self) -> Dict[str, Any]:
    disk_partitions = psutil.disk_partitions()
    for partition in disk_partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_usage_data.append({
                'device': partition.device,      # ← 장치 정보
                'mountpoint': partition.mountpoint,  # ← 마운트 포인트
                'fstype': partition.fstype,      # ← 파일시스템 타입
            })
```

**문제점**:
- 모든 마운트된 파티션 정보 수집
- 외부 드라이브, 네트워크 공유 등 민감한 경로 노출
- 시스템 구조 파악 가능

**영향도**: 🟡 **Medium** - 정보 수집

**권장 사항**:
- 수집할 파티션 화이트리스트 지정
- 네트워크 드라이브 제외
- 민감한 마운트 포인트 필터링

---

### 5. 네트워크 감사 흔적 노출
**위치**: `system_monitor.py:114-137`

```python
def get_network_info(self) -> Dict[str, Any]:
    net_connections = len(psutil.net_connections())  # ← 모든 연결 수집
    net_io_per_nic = psutil.net_io_counters(pernic=True)  # ← 인터페이스별 통계
```

**문제점**:
- 활성 네트워크 연결 정보 수집
- 외부 통신 패턴 노출
- 보안 모니터링 우회 가능성

**영향도**: 🟡 **Medium** - 프라이버시 침해, 감사 추적 방해

**권장 사항**:
- 연결 정보 수집 최소화
- IP 주소 및 포트 정보 제외
- 통계 정보만 수집

---

## 🟠 코드 품질 문제점 (Code Quality Issues)

### 6. Race Condition - 동시성 제어 부족
**위치**: `data_collector.py:25-40`

```python
class DataCollector:
    def __init__(self, interval: float = 1.0):
        self.data_history: List[Dict[str, Any]] = []  # ← 공유 리소스
        self.is_collecting = False

    def _collect_loop(self):
        while self.is_collecting:  # ← 스레드에서 실행
            metrics = self.monitor.get_all_metrics()
            self.data_history.append(metrics)  # ← 동기화 없는 접근
```

**문제점**:
- `data_history` 리스트에 여러 스레드가 동시 접근
- `is_collecting` 플래그도 동기화 없이 접근
- 데이터 손상 또는 레이스 컨디션 발생 가능
- Python GIL로 부분적으로 보호되지만 완전하지 않음

**영향도**: 🟠 **High** - 데이터 무결성 손상, 크래시

**권장 사항**:
- `threading.Lock()` 사용하여 리스트 접근 동기화
- `is_collecting`을 `threading.Event()`로 변경
- `queue.Queue()`를 사용한 스레드 안전 큐 도입
- 또는 `collections.deque` 사용

---

### 7. 메모리 누수 위험 - 무제한 데이터 수집
**위치**: `data_collector.py:35-37`

```python
def _collect_loop(self):
    while self.is_collecting:
        metrics = self.monitor.get_all_metrics()
        self.data_history.append(metrics)  # ← 메모리 제한 없음
```

**문제점**:
- 5분간 약 300개 샘플 수집 (1초 간격)
- 각 샘플은 CPU 코어별 데이터, 프로세스 리스트 등 포함
- 장시간 실행 시 메모리 소진 가능
- OOM(Out Of Memory) 발생 위험

**영향도**: 🟠 **High** - 시스템 불안정, 크래시

**권장 사항**:
- 최대 샘플 수 제한 설정
- 순환 버퍼(Circular Buffer) 사용
- 오래된 데이터 자동 삭제
- 메모리 사용량 모니터링

---

### 8. 블로킹 I/O로 인한 성능 저하
**위치**: `system_monitor.py:23-30`

```python
def get_cpu_info(self) -> Dict[str, Any]:
    cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)  # ← 0.1초 대기
    cpu_freq = psutil.cpu_freq()

    data = {
        'timestamp': datetime.now(),
        'cpu_percent_total': psutil.cpu_percent(interval=0.1),  # ← 또 0.1초 대기
```

**문제점**:
- `cpu_percent()` 함수를 두 번 호출하여 총 0.2초 블로킹
- 1초 수집 간격에서 20% 시간 낭비
- 다른 메트릭 수집에 영향

**영향도**: 🟡 **Medium** - 성능 저하

**권장 사항**:
- 첫 번째 호출 결과 재사용
- Per-core CPU 사용률에서 평균 계산
- 비블로킹 방식 고려

---

### 9. 리소스 정리 불완전
**위치**: `data_collector.py:55-65`

```python
def stop_collection(self):
    self.is_collecting = False
    if self.collection_thread:
        self.collection_thread.join(timeout=2.0)  # ← 2초 후 포기
```

**문제점**:
- 스레드 종료 실패 시 처리 없음
- Daemon 스레드로 설정되어 있어 강제 종료됨
- 진행 중인 작업 손실 가능

**영향도**: 🟡 **Medium** - 데이터 손실, 리소스 누수

**권장 사항**:
- 스레드 종료 확인 및 로그 기록
- 타임아웃 증가 또는 재시도
- Graceful shutdown 구현

---

### 10. 광범위한 예외 처리
**위치**: `data_collector.py:38-39`, `monitor.py` 전반

```python
except Exception as e:  # ← 모든 예외 catch
    print(f"Error collecting data: {e}")
```

**문제점**:
- 구체적이지 않은 예외 처리
- `KeyboardInterrupt`, `SystemExit` 등도 catch 가능
- 실제 문제 원인 파악 어려움
- 디버깅 곤란

**영향도**: 🟡 **Medium** - 유지보수성 저하

**권장 사항**:
- 구체적인 예외 타입 지정
- `KeyboardInterrupt`, `SystemExit`는 제외
- 로깅 레벨 구분 (ERROR, WARNING, INFO)
- 재시도 로직 추가

---

## 🟡 설계 및 아키텍처 문제점

### 11. 설정 하드코딩
**위치**: `monitor.py:19-20`

```python
MONITORING_DURATION = 300  # 5분 = 300초
COLLECTION_INTERVAL = 1.0  # 1초마다 수집
```

**문제점**:
- 모든 설정이 코드에 하드코딩
- 사용자 커스터마이징 불가
- 설정 변경 시 코드 수정 필요

**권장 사항**:
- 설정 파일 도입 (YAML, JSON, INI)
- 환경 변수 지원
- 커맨드 라인 인자 추가

---

### 12. 로깅 시스템 부재
**위치**: 전체 코드베이스

```python
print(f"Data collection started at {self.start_time}")  # ← print 사용
print("Already collecting data")
```

**문제점**:
- `print()` 문만 사용
- 로그 레벨 구분 없음
- 파일 로깅 불가
- 프로덕션 환경에 부적합

**권장 사항**:
- Python `logging` 모듈 사용
- 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR)
- 로그 파일 저장 및 로테이션
- 구조화된 로깅

---

### 13. 입력 검증 부족
**위치**: `data_collector.py:16-22`, `pdf_generator.py:22`

```python
def __init__(self, interval: float = 1.0):
    self.interval = interval  # ← 검증 없음
```

**문제점**:
- 음수 또는 0 값 허용
- 너무 작은 interval로 시스템 과부하 가능
- 파일명 특수 문자 검증 없음

**권장 사항**:
- 입력값 범위 검증
- 최소/최대값 설정
- 타입 체크 강화
- 예외 발생 시 명확한 에러 메시지

---

### 14. 에러 복구 메커니즘 부재
**위치**: `monitor.py:86-133`

```python
try:
    graphs['overview'] = visualizer.create_combined_overview(summary, timestamps)
    print("  ✓ 통합 개요 그래프 생성 완료")
except Exception as e:
    print(f"  ✗ 통합 개요 그래프 생성 실패: {e}")
    graphs['overview'] = None  # ← 실패 시 None만 할당
```

**문제점**:
- 그래프 생성 실패 시 재시도 없음
- 부분 실패 시 전체 보고서 손상 가능
- 사용자에게 복구 옵션 제공 안 함

**권장 사항**:
- 재시도 로직 추가 (exponential backoff)
- 부분 성공 허용 (일부 그래프만으로 PDF 생성)
- 사용자에게 선택권 제공

---

### 15. matplotlib 리소스 관리
**위치**: `visualizer.py` 전반

```python
fig, ax = plt.subplots(figsize=self.figure_size)
# ... 그래프 생성 ...
plt.close(fig)  # ← 명시적 close
```

**문제점**:
- 예외 발생 시 figure 정리 안 됨
- 메모리 누수 가능성
- 컨텍스트 관리자 미사용

**권장 사항**:
- `with plt.figure()` 컨텍스트 관리자 사용
- try-finally로 확실한 정리
- figure 수 모니터링

---

## 🔵 개선 권장 사항 (Recommendations)

### 16. 타입 안전성 부족
**위치**: 전체 코드베이스

```python
def get_latest_data(self) -> Dict[str, Any]:  # ← Any 타입 사용
    if not self.data_history:
        return {}  # ← 빈 dict 반환
```

**문제점**:
- `Any` 타입 남용으로 타입 체크 무력화
- None 반환 가능성 체크 부족
- 빈 dict와 None 혼용

**권장 사항**:
- TypedDict 또는 dataclass 사용
- Optional 타입 명시
- 타입 힌트 강화

---

### 17. 테스트 코드 부재
**현황**: 단위 테스트, 통합 테스트 없음

**권장 사항**:
- pytest를 사용한 단위 테스트 작성
- 모킹(Mocking)을 통한 psutil 테스트
- 통합 테스트 시나리오 작성
- CI/CD 파이프라인 구축

---

### 18. 문서화 부족
**현황**:
- Docstring은 있으나 간단함
- API 문서 없음
- 사용 예제 부족

**권장 사항**:
- Sphinx를 사용한 API 문서 생성
- README에 상세 사용법 추가
- 예제 코드 추가
- 트러블슈팅 가이드 작성

---

## 📊 우선순위 요약

### 🔴 즉시 수정 필요 (Critical)
1. **파일 경로 인젝션** - 시스템 보안 위험
2. **동시성 제어** - 데이터 무결성 문제

### 🟠 조속히 수정 필요 (High)
3. **민감 정보 노출** - 프라이버시 침해
4. **메모리 누수** - 시스템 안정성
5. **예외 정보 누출** - 보안 정보 유출

### 🟡 개선 권장 (Medium)
6. 블로킹 I/O 최적화
7. 리소스 정리 강화
8. 구체적 예외 처리
9. 로깅 시스템 도입

### 🔵 장기 개선 (Low)
10. 설정 파일 도입
11. 타입 안전성 강화
12. 테스트 코드 작성
13. 문서화 강화

---

## 💡 전체 보안 등급

**현재 보안 등급**: ⚠️ **C (취약)**

**주요 위험 요소**:
- 파일 시스템 접근 제어 부족
- 민감한 시스템 정보 무제한 수집
- 입력 검증 미흡
- 에러 메시지 정보 누출

**권장 보안 등급**: 🛡️ **B+ (양호)** (개선 후)

---

## 📝 결론

본 시스템은 기능적으로는 잘 작동하나, **보안**, **동시성**, **리소스 관리** 측면에서 심각한 문제가 있습니다.

특히:
1. **파일 경로 인젝션**은 즉시 수정이 필요한 치명적 취약점
2. **동시성 제어 부족**은 데이터 손상 가능성
3. **민감 정보 노출**은 프라이버시 침해 위험

프로덕션 환경에 배포하기 전에 **최소한 Critical 및 High 등급 문제**는 반드시 해결해야 합니다.

---

**리뷰어**: Claude Code Review System
**리뷰 버전**: v1.0
**다음 리뷰 권장 시점**: 주요 수정 사항 반영 후
