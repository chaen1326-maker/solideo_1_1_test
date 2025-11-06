"""
데이터 수집 및 저장 모듈
시스템 메트릭을 주기적으로 수집하고 저장합니다.
"""

import time
import threading
from typing import List, Dict, Any
from datetime import datetime
from system_monitor import SystemMonitor


class DataCollector:
    """데이터 수집 및 저장 클래스"""

    def __init__(self, interval: float = 1.0):
        """
        데이터 수집기 초기화

        Args:
            interval: 수집 간격 (초)
        """
        self.interval = interval
        self.monitor = SystemMonitor()
        self.data_history: List[Dict[str, Any]] = []
        self.is_collecting = False
        self.collection_thread = None
        self.start_time = None
        self.end_time = None

    def _collect_loop(self):
        """데이터 수집 루프 (별도 스레드에서 실행)"""
        while self.is_collecting:
            try:
                metrics = self.monitor.get_all_metrics()
                self.data_history.append(metrics)
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error collecting data: {e}")

    def start_collection(self):
        """데이터 수집 시작"""
        if self.is_collecting:
            print("Already collecting data")
            return

        self.is_collecting = True
        self.start_time = datetime.now()
        self.data_history = []

        self.collection_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.collection_thread.start()
        print(f"Data collection started at {self.start_time}")

    def stop_collection(self):
        """데이터 수집 중지"""
        if not self.is_collecting:
            print("Not currently collecting data")
            return

        self.is_collecting = False
        self.end_time = datetime.now()

        if self.collection_thread:
            self.collection_thread.join(timeout=2.0)

        print(f"Data collection stopped at {self.end_time}")
        print(f"Collected {len(self.data_history)} data points")

    def get_data_summary(self) -> Dict[str, Any]:
        """수집된 데이터 요약 반환"""
        if not self.data_history:
            return {}

        # CPU 데이터 추출
        cpu_usage = [d['cpu']['cpu_percent_total'] for d in self.data_history]
        cpu_temps = [d['cpu'].get('cpu_temp_avg', 0) for d in self.data_history if 'cpu_temp_avg' in d['cpu']]

        # 메모리 데이터 추출
        memory_usage = [d['memory']['memory_percent'] for d in self.data_history]

        # 네트워크 데이터 추출
        bytes_sent = [d['network']['bytes_sent'] for d in self.data_history]
        bytes_recv = [d['network']['bytes_recv'] for d in self.data_history]

        # 디스크 데이터 추출
        disk_usage = []
        if self.data_history[0]['disk']['disk_usage']:
            # 첫 번째 파티션의 사용률
            disk_usage = [d['disk']['disk_usage'][0]['percent'] for d in self.data_history if d['disk']['disk_usage']]

        summary = {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            'total_samples': len(self.data_history),
            'cpu': {
                'avg': sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                'max': max(cpu_usage) if cpu_usage else 0,
                'min': min(cpu_usage) if cpu_usage else 0,
                'values': cpu_usage,
            },
            'cpu_temp': {
                'avg': sum(cpu_temps) / len(cpu_temps) if cpu_temps else 0,
                'max': max(cpu_temps) if cpu_temps else 0,
                'min': min(cpu_temps) if cpu_temps else 0,
                'values': cpu_temps,
            } if cpu_temps else None,
            'memory': {
                'avg': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                'max': max(memory_usage) if memory_usage else 0,
                'min': min(memory_usage) if memory_usage else 0,
                'values': memory_usage,
            },
            'network': {
                'bytes_sent_start': bytes_sent[0] if bytes_sent else 0,
                'bytes_sent_end': bytes_sent[-1] if bytes_sent else 0,
                'bytes_recv_start': bytes_recv[0] if bytes_recv else 0,
                'bytes_recv_end': bytes_recv[-1] if bytes_recv else 0,
                'bytes_sent_values': bytes_sent,
                'bytes_recv_values': bytes_recv,
            },
            'disk': {
                'avg': sum(disk_usage) / len(disk_usage) if disk_usage else 0,
                'max': max(disk_usage) if disk_usage else 0,
                'min': min(disk_usage) if disk_usage else 0,
                'values': disk_usage,
            } if disk_usage else None,
        }

        return summary

    def get_latest_data(self) -> Dict[str, Any]:
        """가장 최근 데이터 반환"""
        if not self.data_history:
            return {}
        return self.data_history[-1]

    def get_all_data(self) -> List[Dict[str, Any]]:
        """모든 수집된 데이터 반환"""
        return self.data_history
