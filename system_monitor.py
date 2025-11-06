"""
시스템 리소스 모니터링 모듈
CPU, 메모리, 디스크, 네트워크, 온도 등의 시스템 리소스를 모니터링합니다.
"""

import psutil
import time
from datetime import datetime
from typing import Dict, List, Any


class SystemMonitor:
    """시스템 리소스 모니터링 클래스"""

    def __init__(self):
        """모니터 초기화"""
        self.start_time = time.time()
        # 네트워크 초기 카운터
        self.net_io_start = psutil.net_io_counters()
        # 디스크 초기 카운터
        self.disk_io_start = psutil.disk_io_counters()

    def get_cpu_info(self) -> Dict[str, Any]:
        """CPU 정보 수집"""
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_freq = psutil.cpu_freq()

        data = {
            'timestamp': datetime.now(),
            'cpu_percent_total': psutil.cpu_percent(interval=0.1),
            'cpu_percent_per_core': cpu_percent,
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_count_physical': psutil.cpu_count(logical=False),
        }

        # CPU 주파수 정보 (가능한 경우)
        if cpu_freq:
            data['cpu_freq_current'] = cpu_freq.current
            data['cpu_freq_min'] = cpu_freq.min
            data['cpu_freq_max'] = cpu_freq.max

        # CPU 온도 (가능한 경우)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                cpu_temps = []
                for name, entries in temps.items():
                    if 'coretemp' in name.lower() or 'cpu' in name.lower():
                        for entry in entries:
                            cpu_temps.append(entry.current)
                if cpu_temps:
                    data['cpu_temp_avg'] = sum(cpu_temps) / len(cpu_temps)
                    data['cpu_temp_max'] = max(cpu_temps)
        except (AttributeError, OSError):
            pass

        return data

    def get_memory_info(self) -> Dict[str, Any]:
        """메모리 정보 수집"""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()

        return {
            'timestamp': datetime.now(),
            'memory_total': virtual_mem.total,
            'memory_available': virtual_mem.available,
            'memory_used': virtual_mem.used,
            'memory_percent': virtual_mem.percent,
            'swap_total': swap_mem.total,
            'swap_used': swap_mem.used,
            'swap_percent': swap_mem.percent,
        }

    def get_disk_info(self) -> Dict[str, Any]:
        """디스크 정보 수집"""
        disk_partitions = psutil.disk_partitions()
        disk_usage_data = []

        for partition in disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage_data.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                })
            except PermissionError:
                continue

        # 디스크 I/O 통계
        disk_io = psutil.disk_io_counters()
        disk_io_data = {}
        if disk_io:
            disk_io_data = {
                'read_count': disk_io.read_count,
                'write_count': disk_io.write_count,
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes,
                'read_time': disk_io.read_time,
                'write_time': disk_io.write_time,
            }

        return {
            'timestamp': datetime.now(),
            'disk_usage': disk_usage_data,
            'disk_io': disk_io_data,
        }

    def get_network_info(self) -> Dict[str, Any]:
        """네트워크 정보 수집"""
        net_io = psutil.net_io_counters()
        net_connections = len(psutil.net_connections())

        # 인터페이스별 통계
        net_io_per_nic = psutil.net_io_counters(pernic=True)

        return {
            'timestamp': datetime.now(),
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout,
            'connections': net_connections,
            'per_nic': {name: {
                'bytes_sent': nic.bytes_sent,
                'bytes_recv': nic.bytes_recv,
            } for name, nic in net_io_per_nic.items()}
        }

    def get_process_info(self) -> Dict[str, Any]:
        """프로세스 정보 수집 (상위 10개)"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent'],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # CPU 사용률 기준 정렬
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)

        return {
            'timestamp': datetime.now(),
            'top_processes': processes[:10],
            'total_processes': len(processes),
        }

    def get_gpu_info(self) -> Dict[str, Any]:
        """GPU 정보 수집 (가능한 경우)"""
        gpu_data = {
            'timestamp': datetime.now(),
            'available': False,
        }

        try:
            temps = psutil.sensors_temperatures()
            if temps:
                gpu_temps = []
                for name, entries in temps.items():
                    if 'gpu' in name.lower() or 'nvidia' in name.lower() or 'amd' in name.lower():
                        for entry in entries:
                            gpu_temps.append(entry.current)
                            gpu_data['available'] = True
                if gpu_temps:
                    gpu_data['gpu_temp_avg'] = sum(gpu_temps) / len(gpu_temps)
                    gpu_data['gpu_temp_max'] = max(gpu_temps)
        except (AttributeError, OSError):
            pass

        return gpu_data

    def get_battery_info(self) -> Dict[str, Any]:
        """배터리 정보 수집 (노트북인 경우)"""
        battery_data = {
            'timestamp': datetime.now(),
            'available': False,
        }

        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_data['available'] = True
                battery_data['percent'] = battery.percent
                battery_data['power_plugged'] = battery.power_plugged
                battery_data['secsleft'] = battery.secsleft
        except (AttributeError, OSError):
            pass

        return battery_data

    def get_all_metrics(self) -> Dict[str, Any]:
        """모든 시스템 메트릭 수집"""
        return {
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'processes': self.get_process_info(),
            'gpu': self.get_gpu_info(),
            'battery': self.get_battery_info(),
        }
