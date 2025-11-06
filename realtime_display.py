"""
실시간 UI 표시 모듈
터미널에서 실시간으로 시스템 메트릭을 표시합니다.
"""

import sys
import time
from typing import Dict, Any


class RealtimeDisplay:
    """실시간 콘솔 표시 클래스"""

    def __init__(self):
        """초기화"""
        self.last_display_time = 0
        self.display_interval = 1.0  # 1초마다 업데이트

    def clear_screen(self):
        """화면 클리어 (ANSI 이스케이프 시퀀스 사용)"""
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()

    def format_bytes(self, bytes_value: int) -> str:
        """바이트를 읽기 쉬운 형식으로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"

    def create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """진행률 바 생성"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percentage:.1f}%"

    def display_metrics(self, metrics: Dict[str, Any], elapsed_time: float, total_time: float):
        """메트릭 표시"""
        current_time = time.time()
        if current_time - self.last_display_time < self.display_interval:
            return

        self.last_display_time = current_time
        self.clear_screen()

        # 헤더
        print("=" * 80)
        print(" " * 20 + "시스템 리소스 모니터링 시스템")
        print("=" * 80)
        print()

        # 진행 상태
        progress = (elapsed_time / total_time) * 100
        progress_bar = self.create_progress_bar(progress, 50)
        print(f"모니터링 진행: {progress_bar}")
        print(f"경과 시간: {int(elapsed_time)}초 / {int(total_time)}초")
        print()

        # CPU 정보
        print("┌─ CPU 사용률 " + "─" * 65 + "┐")
        cpu_data = metrics.get('cpu', {})
        cpu_percent = cpu_data.get('cpu_percent_total', 0)
        cpu_bar = self.create_progress_bar(cpu_percent, 40)
        print(f"│ 전체: {cpu_bar}")

        # 코어별 사용률
        cpu_percents = cpu_data.get('cpu_percent_per_core', [])
        if cpu_percents:
            print(f"│ 코어별 사용률:")
            for i, percent in enumerate(cpu_percents[:8]):  # 최대 8개 코어만 표시
                mini_bar = self.create_progress_bar(percent, 20)
                print(f"│   Core {i}: {mini_bar}")

        # CPU 온도
        if 'cpu_temp_avg' in cpu_data:
            temp = cpu_data['cpu_temp_avg']
            print(f"│ 평균 온도: {temp:.1f}°C")

        # CPU 주파수
        if 'cpu_freq_current' in cpu_data:
            freq = cpu_data['cpu_freq_current']
            print(f"│ 주파수: {freq:.0f} MHz")

        print("└" + "─" * 78 + "┘")
        print()

        # 메모리 정보
        print("┌─ 메모리 사용량 " + "─" * 61 + "┐")
        memory_data = metrics.get('memory', {})
        memory_percent = memory_data.get('memory_percent', 0)
        memory_bar = self.create_progress_bar(memory_percent, 40)
        memory_used = self.format_bytes(memory_data.get('memory_used', 0))
        memory_total = self.format_bytes(memory_data.get('memory_total', 0))
        print(f"│ RAM: {memory_bar}")
        print(f"│ 사용량: {memory_used} / {memory_total}")

        swap_percent = memory_data.get('swap_percent', 0)
        if swap_percent > 0:
            swap_bar = self.create_progress_bar(swap_percent, 40)
            swap_used = self.format_bytes(memory_data.get('swap_used', 0))
            swap_total = self.format_bytes(memory_data.get('swap_total', 0))
            print(f"│ SWAP: {swap_bar}")
            print(f"│ 사용량: {swap_used} / {swap_total}")
        print("└" + "─" * 78 + "┘")
        print()

        # 디스크 정보
        print("┌─ 디스크 사용량 " + "─" * 61 + "┐")
        disk_data = metrics.get('disk', {})
        disk_usage = disk_data.get('disk_usage', [])
        if disk_usage:
            for disk in disk_usage[:3]:  # 최대 3개 파티션만 표시
                disk_percent = disk.get('percent', 0)
                disk_bar = self.create_progress_bar(disk_percent, 30)
                disk_used = self.format_bytes(disk.get('used', 0))
                disk_total = self.format_bytes(disk.get('total', 0))
                mountpoint = disk.get('mountpoint', 'Unknown')
                print(f"│ {mountpoint}: {disk_bar}")
                print(f"│ {disk_used} / {disk_total}")
        print("└" + "─" * 78 + "┘")
        print()

        # 네트워크 정보
        print("┌─ 네트워크 트래픽 " + "─" * 59 + "┐")
        network_data = metrics.get('network', {})
        bytes_sent = self.format_bytes(network_data.get('bytes_sent', 0))
        bytes_recv = self.format_bytes(network_data.get('bytes_recv', 0))
        connections = network_data.get('connections', 0)
        print(f"│ 전송: {bytes_sent}")
        print(f"│ 수신: {bytes_recv}")
        print(f"│ 연결 수: {connections}")
        print("└" + "─" * 78 + "┘")
        print()

        # 프로세스 정보
        print("┌─ 상위 프로세스 (CPU 기준) " + "─" * 50 + "┐")
        process_data = metrics.get('processes', {})
        top_processes = process_data.get('top_processes', [])[:5]  # 상위 5개
        if top_processes:
            print(f"│ {'PID':<8} {'이름':<25} {'CPU%':<10} {'Memory%':<10} │")
            print(f"│ {'-'*8} {'-'*25} {'-'*10} {'-'*10} │")
            for proc in top_processes:
                pid = proc.get('pid', 0)
                name = proc.get('name', 'Unknown')[:25]
                cpu_p = proc.get('cpu_percent', 0) or 0
                mem_p = proc.get('memory_percent', 0) or 0
                print(f"│ {pid:<8} {name:<25} {cpu_p:<10.1f} {mem_p:<10.1f} │")
        print("└" + "─" * 78 + "┘")
        print()

        # GPU 정보 (가능한 경우)
        gpu_data = metrics.get('gpu', {})
        if gpu_data.get('available'):
            print("┌─ GPU 정보 " + "─" * 66 + "┐")
            if 'gpu_temp_avg' in gpu_data:
                print(f"│ 평균 온도: {gpu_data['gpu_temp_avg']:.1f}°C")
            print("└" + "─" * 78 + "┘")
            print()

        # 배터리 정보 (노트북인 경우)
        battery_data = metrics.get('battery', {})
        if battery_data.get('available'):
            print("┌─ 배터리 정보 " + "─" * 63 + "┐")
            battery_percent = battery_data.get('percent', 0)
            battery_bar = self.create_progress_bar(battery_percent, 40)
            plugged = "충전 중" if battery_data.get('power_plugged') else "배터리 사용 중"
            print(f"│ {battery_bar}")
            print(f"│ 상태: {plugged}")
            print("└" + "─" * 78 + "┘")
            print()

        print("=" * 80)
        sys.stdout.flush()

    def display_completion(self, summary: Dict[str, Any]):
        """완료 메시지 표시"""
        self.clear_screen()
        print("=" * 80)
        print(" " * 25 + "모니터링 완료!")
        print("=" * 80)
        print()
        print(f"총 수집 샘플: {summary.get('total_samples', 0)}개")
        print(f"모니터링 시간: {summary.get('duration_seconds', 0):.1f}초")
        print()
        print("CPU 통계:")
        print(f"  평균: {summary['cpu']['avg']:.1f}%")
        print(f"  최대: {summary['cpu']['max']:.1f}%")
        print(f"  최소: {summary['cpu']['min']:.1f}%")
        print()
        print("메모리 통계:")
        print(f"  평균: {summary['memory']['avg']:.1f}%")
        print(f"  최대: {summary['memory']['max']:.1f}%")
        print(f"  최소: {summary['memory']['min']:.1f}%")
        print()

        if summary.get('cpu_temp'):
            print("CPU 온도 통계:")
            print(f"  평균: {summary['cpu_temp']['avg']:.1f}°C")
            print(f"  최대: {summary['cpu_temp']['max']:.1f}°C")
            print(f"  최소: {summary['cpu_temp']['min']:.1f}°C")
            print()

        print("PDF 보고서를 생성하는 중...")
        print("=" * 80)
        sys.stdout.flush()
