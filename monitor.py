#!/usr/bin/env python3
"""
시스템 리소스 모니터링 시스템 - 메인 프로그램
5분 동안 시스템 리소스를 모니터링하고 PDF 보고서를 생성합니다.
"""

import time
import sys
from datetime import datetime
from data_collector import DataCollector
from realtime_display import RealtimeDisplay
from visualizer import DataVisualizer
from pdf_generator import PDFReportGenerator


def main():
    """메인 함수"""
    # 모니터링 시간 설정 (초)
    MONITORING_DURATION = 300  # 5분 = 300초
    COLLECTION_INTERVAL = 1.0  # 1초마다 수집

    print("=" * 80)
    print(" " * 20 + "시스템 리소스 모니터링 시스템")
    print("=" * 80)
    print()
    print(f"모니터링 시간: {MONITORING_DURATION}초 ({MONITORING_DURATION/60:.0f}분)")
    print(f"데이터 수집 간격: {COLLECTION_INTERVAL}초")
    print()
    print("모니터링을 시작합니다...")
    print()

    # 데이터 수집기 초기화
    collector = DataCollector(interval=COLLECTION_INTERVAL)

    # 실시간 디스플레이 초기화
    display = RealtimeDisplay()

    # 데이터 수집 시작
    collector.start_collection()

    # 시작 시간 기록
    start_time = time.time()

    try:
        # 모니터링 루프
        while True:
            elapsed_time = time.time() - start_time

            # 종료 조건 확인
            if elapsed_time >= MONITORING_DURATION:
                break

            # 최신 데이터 가져오기
            latest_data = collector.get_latest_data()

            # 실시간 UI 업데이트
            if latest_data:
                display.display_metrics(latest_data, elapsed_time, MONITORING_DURATION)

            # 짧은 대기
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    finally:
        # 데이터 수집 중지
        collector.stop_collection()

    # 데이터 요약
    summary = collector.get_data_summary()
    all_data = collector.get_all_data()

    # 완료 메시지 표시
    display.display_completion(summary)

    # 그래프 생성
    print("\n그래프를 생성하는 중...")
    visualizer = DataVisualizer()

    # 타임스탬프 추출
    timestamps = [d['cpu']['timestamp'] for d in all_data]

    graphs = {}

    # 통합 개요 그래프
    try:
        graphs['overview'] = visualizer.create_combined_overview(summary, timestamps)
        print("  ✓ 통합 개요 그래프 생성 완료")
    except Exception as e:
        print(f"  ✗ 통합 개요 그래프 생성 실패: {e}")
        graphs['overview'] = None

    # CPU 그래프
    try:
        graphs['cpu'] = visualizer.create_cpu_graph(summary, timestamps)
        print("  ✓ CPU 그래프 생성 완료")
    except Exception as e:
        print(f"  ✗ CPU 그래프 생성 실패: {e}")
        graphs['cpu'] = None

    # 메모리 그래프
    try:
        graphs['memory'] = visualizer.create_memory_graph(summary, timestamps)
        print("  ✓ 메모리 그래프 생성 완료")
    except Exception as e:
        print(f"  ✗ 메모리 그래프 생성 실패: {e}")
        graphs['memory'] = None

    # 네트워크 그래프
    try:
        graphs['network'] = visualizer.create_network_graph(summary, timestamps)
        print("  ✓ 네트워크 그래프 생성 완료")
    except Exception as e:
        print(f"  ✗ 네트워크 그래프 생성 실패: {e}")
        graphs['network'] = None

    # CPU 온도 그래프 (가능한 경우)
    try:
        graphs['cpu_temp'] = visualizer.create_cpu_temp_graph(summary, timestamps)
        if graphs['cpu_temp']:
            print("  ✓ CPU 온도 그래프 생성 완료")
    except Exception as e:
        print(f"  ✗ CPU 온도 그래프 생성 실패: {e}")
        graphs['cpu_temp'] = None

    # 디스크 그래프 (가능한 경우)
    try:
        graphs['disk'] = visualizer.create_disk_graph(summary, timestamps)
        if graphs['disk']:
            print("  ✓ 디스크 그래프 생성 완료")
    except Exception as e:
        print(f"  ✗ 디스크 그래프 생성 실패: {e}")
        graphs['disk'] = None

    # PDF 보고서 생성
    print("\nPDF 보고서를 생성하는 중...")
    try:
        pdf_generator = PDFReportGenerator("system_report.pdf")
        pdf_generator.generate_report(summary, all_data, graphs)
        print("  ✓ PDF 보고서 생성 완료: system_report.pdf")
    except Exception as e:
        print(f"  ✗ PDF 보고서 생성 실패: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 80)
    print(" " * 25 + "모니터링 완료!")
    print("=" * 80)
    print()
    print("생성된 파일:")
    print("  - system_report.pdf")
    print()


if __name__ == "__main__":
    main()
