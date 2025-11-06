"""
데이터 시각화 모듈
수집된 데이터를 그래프와 차트로 시각화합니다.
"""

import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, Any, List
from datetime import datetime
import io


class DataVisualizer:
    """데이터 시각화 클래스"""

    def __init__(self):
        """시각화 초기화"""
        plt.style.use('seaborn-v0_8-darkgrid')
        self.figure_size = (12, 8)

    def create_cpu_graph(self, summary: Dict[str, Any], timestamps: List[datetime]) -> io.BytesIO:
        """CPU 사용률 그래프 생성"""
        fig, ax = plt.subplots(figsize=self.figure_size)

        cpu_values = summary['cpu']['values']
        ax.plot(timestamps[:len(cpu_values)], cpu_values, label='CPU Usage (%)', color='#2E86AB', linewidth=2)
        ax.fill_between(timestamps[:len(cpu_values)], cpu_values, alpha=0.3, color='#2E86AB')

        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('CPU Usage (%)', fontsize=12)
        ax.set_title('CPU Usage Over Time', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # 시간 포맷팅
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)

        # 통계 정보 추가
        stats_text = f"Avg: {summary['cpu']['avg']:.1f}% | Max: {summary['cpu']['max']:.1f}% | Min: {summary['cpu']['min']:.1f}%"
        ax.text(0.5, 0.02, stats_text, transform=ax.transAxes,
                ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        # BytesIO에 저장
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def create_memory_graph(self, summary: Dict[str, Any], timestamps: List[datetime]) -> io.BytesIO:
        """메모리 사용률 그래프 생성"""
        fig, ax = plt.subplots(figsize=self.figure_size)

        memory_values = summary['memory']['values']
        ax.plot(timestamps[:len(memory_values)], memory_values, label='Memory Usage (%)', color='#A23B72', linewidth=2)
        ax.fill_between(timestamps[:len(memory_values)], memory_values, alpha=0.3, color='#A23B72')

        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Memory Usage (%)', fontsize=12)
        ax.set_title('Memory Usage Over Time', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # 시간 포맷팅
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)

        # 통계 정보 추가
        stats_text = f"Avg: {summary['memory']['avg']:.1f}% | Max: {summary['memory']['max']:.1f}% | Min: {summary['memory']['min']:.1f}%"
        ax.text(0.5, 0.02, stats_text, transform=ax.transAxes,
                ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def create_network_graph(self, summary: Dict[str, Any], timestamps: List[datetime]) -> io.BytesIO:
        """네트워크 트래픽 그래프 생성"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figure_size)

        bytes_sent = summary['network']['bytes_sent_values']
        bytes_recv = summary['network']['bytes_recv_values']

        # 바이트를 MB로 변환
        mb_sent = [b / (1024 * 1024) for b in bytes_sent]
        mb_recv = [b / (1024 * 1024) for b in bytes_recv]

        # 전송 그래프
        ax1.plot(timestamps[:len(mb_sent)], mb_sent, label='Bytes Sent (MB)', color='#F18F01', linewidth=2)
        ax1.fill_between(timestamps[:len(mb_sent)], mb_sent, alpha=0.3, color='#F18F01')
        ax1.set_ylabel('Sent (MB)', fontsize=12)
        ax1.set_title('Network Traffic - Sent', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # 수신 그래프
        ax2.plot(timestamps[:len(mb_recv)], mb_recv, label='Bytes Received (MB)', color='#06A77D', linewidth=2)
        ax2.fill_between(timestamps[:len(mb_recv)], mb_recv, alpha=0.3, color='#06A77D')
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_ylabel('Received (MB)', fontsize=12)
        ax2.set_title('Network Traffic - Received', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def create_cpu_temp_graph(self, summary: Dict[str, Any], timestamps: List[datetime]) -> io.BytesIO:
        """CPU 온도 그래프 생성"""
        if not summary.get('cpu_temp') or not summary['cpu_temp']['values']:
            return None

        fig, ax = plt.subplots(figsize=self.figure_size)

        temp_values = summary['cpu_temp']['values']
        ax.plot(timestamps[:len(temp_values)], temp_values, label='CPU Temperature (°C)', color='#D62828', linewidth=2)
        ax.fill_between(timestamps[:len(temp_values)], temp_values, alpha=0.3, color='#D62828')

        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title('CPU Temperature Over Time', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # 시간 포맷팅
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)

        # 통계 정보 추가
        stats_text = f"Avg: {summary['cpu_temp']['avg']:.1f}°C | Max: {summary['cpu_temp']['max']:.1f}°C | Min: {summary['cpu_temp']['min']:.1f}°C"
        ax.text(0.5, 0.02, stats_text, transform=ax.transAxes,
                ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def create_disk_graph(self, summary: Dict[str, Any], timestamps: List[datetime]) -> io.BytesIO:
        """디스크 사용률 그래프 생성"""
        if not summary.get('disk') or not summary['disk']['values']:
            return None

        fig, ax = plt.subplots(figsize=self.figure_size)

        disk_values = summary['disk']['values']
        ax.plot(timestamps[:len(disk_values)], disk_values, label='Disk Usage (%)', color='#7209B7', linewidth=2)
        ax.fill_between(timestamps[:len(disk_values)], disk_values, alpha=0.3, color='#7209B7')

        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Disk Usage (%)', fontsize=12)
        ax.set_title('Disk Usage Over Time', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # 시간 포맷팅
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)

        # 통계 정보 추가
        stats_text = f"Avg: {summary['disk']['avg']:.1f}% | Max: {summary['disk']['max']:.1f}% | Min: {summary['disk']['min']:.1f}%"
        ax.text(0.5, 0.02, stats_text, transform=ax.transAxes,
                ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def create_combined_overview(self, summary: Dict[str, Any], timestamps: List[datetime]) -> io.BytesIO:
        """통합 개요 그래프 생성 (CPU, Memory, Network)"""
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # CPU 그래프
        ax1 = fig.add_subplot(gs[0, :])
        cpu_values = summary['cpu']['values']
        ax1.plot(timestamps[:len(cpu_values)], cpu_values, label='CPU Usage (%)', color='#2E86AB', linewidth=2)
        ax1.fill_between(timestamps[:len(cpu_values)], cpu_values, alpha=0.3, color='#2E86AB')
        ax1.set_ylabel('CPU (%)', fontsize=10)
        ax1.set_title('CPU Usage', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # 메모리 그래프
        ax2 = fig.add_subplot(gs[1, :])
        memory_values = summary['memory']['values']
        ax2.plot(timestamps[:len(memory_values)], memory_values, label='Memory Usage (%)', color='#A23B72', linewidth=2)
        ax2.fill_between(timestamps[:len(memory_values)], memory_values, alpha=0.3, color='#A23B72')
        ax2.set_ylabel('Memory (%)', fontsize=10)
        ax2.set_title('Memory Usage', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right', fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # 네트워크 송신
        ax3 = fig.add_subplot(gs[2, 0])
        bytes_sent = summary['network']['bytes_sent_values']
        mb_sent = [b / (1024 * 1024) for b in bytes_sent]
        ax3.plot(timestamps[:len(mb_sent)], mb_sent, label='Sent (MB)', color='#F18F01', linewidth=2)
        ax3.fill_between(timestamps[:len(mb_sent)], mb_sent, alpha=0.3, color='#F18F01')
        ax3.set_xlabel('Time', fontsize=10)
        ax3.set_ylabel('MB', fontsize=10)
        ax3.set_title('Network Sent', fontsize=12, fontweight='bold')
        ax3.legend(loc='upper right', fontsize=9)
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

        # 네트워크 수신
        ax4 = fig.add_subplot(gs[2, 1])
        bytes_recv = summary['network']['bytes_recv_values']
        mb_recv = [b / (1024 * 1024) for b in bytes_recv]
        ax4.plot(timestamps[:len(mb_recv)], mb_recv, label='Received (MB)', color='#06A77D', linewidth=2)
        ax4.fill_between(timestamps[:len(mb_recv)], mb_recv, alpha=0.3, color='#06A77D')
        ax4.set_xlabel('Time', fontsize=10)
        ax4.set_ylabel('MB', fontsize=10)
        ax4.set_title('Network Received', fontsize=12, fontweight='bold')
        ax4.legend(loc='upper right', fontsize=9)
        ax4.grid(True, alpha=0.3)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

        fig.suptitle('System Resource Monitoring Overview', fontsize=16, fontweight='bold')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf
