"""
PDF 보고서 생성 모듈
수집된 데이터를 PDF 보고서로 생성합니다.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus import KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import Dict, Any, List
import io
from PIL import Image as PILImage


class PDFReportGenerator:
    """PDF 보고서 생성 클래스"""

    def __init__(self, filename: str = "system_report.pdf"):
        """
        PDF 생성기 초기화

        Args:
            filename: 출력 PDF 파일명
        """
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        self.styles = getSampleStyleSheet()
        self.story = []

        # 커스텀 스타일 추가
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#A23B72'),
            spaceAfter=12,
            spaceBefore=12,
        ))

    def format_bytes(self, bytes_value: int) -> str:
        """바이트를 읽기 쉬운 형식으로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"

    def add_title(self):
        """제목 추가"""
        title = Paragraph("시스템 리소스 모니터링 보고서", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 12))

        # 보고서 생성 시간
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_text = Paragraph(f"<i>생성 시간: {now}</i>", self.styles['Normal'])
        self.story.append(date_text)
        self.story.append(Spacer(1, 20))

    def add_summary_section(self, summary: Dict[str, Any]):
        """요약 섹션 추가"""
        heading = Paragraph("1. 모니터링 요약", self.styles['CustomHeading'])
        self.story.append(heading)

        # 요약 테이블 데이터
        data = [
            ['항목', '값'],
            ['모니터링 시작 시간', summary['start_time'].strftime("%Y-%m-%d %H:%M:%S")],
            ['모니터링 종료 시간', summary['end_time'].strftime("%Y-%m-%d %H:%M:%S")],
            ['총 모니터링 시간', f"{summary['duration_seconds']:.1f}초 ({summary['duration_seconds']/60:.1f}분)"],
            ['수집 샘플 수', f"{summary['total_samples']}개"],
            ['수집 간격', '약 1초'],
        ]

        # 테이블 스타일
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def add_cpu_section(self, summary: Dict[str, Any], first_data: Dict[str, Any]):
        """CPU 섹션 추가"""
        heading = Paragraph("2. CPU 사용률", self.styles['CustomHeading'])
        self.story.append(heading)

        # CPU 통계
        cpu_stats = [
            ['메트릭', '값'],
            ['평균 사용률', f"{summary['cpu']['avg']:.1f}%"],
            ['최대 사용률', f"{summary['cpu']['max']:.1f}%"],
            ['최소 사용률', f"{summary['cpu']['min']:.1f}%"],
            ['논리 코어 수', f"{first_data['cpu']['cpu_count_logical']}개"],
            ['물리 코어 수', f"{first_data['cpu'].get('cpu_count_physical', 'N/A')}개"],
        ]

        if 'cpu_freq_current' in first_data['cpu']:
            cpu_stats.append(['현재 주파수', f"{first_data['cpu']['cpu_freq_current']:.0f} MHz"])
            cpu_stats.append(['최대 주파수', f"{first_data['cpu']['cpu_freq_max']:.0f} MHz"])

        if summary.get('cpu_temp'):
            cpu_stats.append(['평균 온도', f"{summary['cpu_temp']['avg']:.1f}°C"])
            cpu_stats.append(['최대 온도', f"{summary['cpu_temp']['max']:.1f}°C"])

        table = Table(cpu_stats, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def add_memory_section(self, summary: Dict[str, Any], first_data: Dict[str, Any]):
        """메모리 섹션 추가"""
        heading = Paragraph("3. 메모리 사용량", self.styles['CustomHeading'])
        self.story.append(heading)

        memory_data = first_data['memory']
        memory_stats = [
            ['메트릭', '값'],
            ['평균 사용률', f"{summary['memory']['avg']:.1f}%"],
            ['최대 사용률', f"{summary['memory']['max']:.1f}%"],
            ['최소 사용률', f"{summary['memory']['min']:.1f}%"],
            ['총 메모리', self.format_bytes(memory_data['memory_total'])],
            ['사용 가능', self.format_bytes(memory_data['memory_available'])],
            ['사용 중', self.format_bytes(memory_data['memory_used'])],
            ['스왑 총량', self.format_bytes(memory_data['swap_total'])],
            ['스왑 사용', self.format_bytes(memory_data['swap_used'])],
        ]

        table = Table(memory_stats, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def add_disk_section(self, first_data: Dict[str, Any]):
        """디스크 섹션 추가"""
        heading = Paragraph("4. 디스크 사용량", self.styles['CustomHeading'])
        self.story.append(heading)

        disk_usage = first_data['disk']['disk_usage']
        if disk_usage:
            disk_data = [['마운트 포인트', '파일시스템', '총 용량', '사용량', '사용률']]
            for disk in disk_usage:
                disk_data.append([
                    disk['mountpoint'],
                    disk['fstype'],
                    self.format_bytes(disk['total']),
                    self.format_bytes(disk['used']),
                    f"{disk['percent']:.1f}%"
                ])

            table = Table(disk_data, colWidths=[2*inch, 1.2*inch, 1.3*inch, 1.3*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7209B7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            self.story.append(table)
        else:
            self.story.append(Paragraph("디스크 정보를 사용할 수 없습니다.", self.styles['Normal']))

        self.story.append(Spacer(1, 20))

    def add_network_section(self, summary: Dict[str, Any]):
        """네트워크 섹션 추가"""
        heading = Paragraph("5. 네트워크 트래픽", self.styles['CustomHeading'])
        self.story.append(heading)

        network = summary['network']
        total_sent = network['bytes_sent_end'] - network['bytes_sent_start']
        total_recv = network['bytes_recv_end'] - network['bytes_recv_start']

        network_stats = [
            ['메트릭', '값'],
            ['총 전송량', self.format_bytes(total_sent)],
            ['총 수신량', self.format_bytes(total_recv)],
            ['시작 시 전송', self.format_bytes(network['bytes_sent_start'])],
            ['종료 시 전송', self.format_bytes(network['bytes_sent_end'])],
            ['시작 시 수신', self.format_bytes(network['bytes_recv_start'])],
            ['종료 시 수신', self.format_bytes(network['bytes_recv_end'])],
        ]

        table = Table(network_stats, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F18F01')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def add_graph(self, graph_buffer: io.BytesIO, title: str, width: float = 6*inch):
        """그래프 이미지 추가"""
        if graph_buffer:
            heading = Paragraph(title, self.styles['CustomHeading'])
            self.story.append(heading)

            # BytesIO를 PIL Image로 변환
            pil_img = PILImage.open(graph_buffer)

            # 임시 파일로 저장하지 않고 직접 사용
            img = Image(graph_buffer, width=width, height=width*0.6)
            self.story.append(img)
            self.story.append(Spacer(1, 20))

    def generate_report(self, summary: Dict[str, Any], all_data: List[Dict[str, Any]],
                       graphs: Dict[str, io.BytesIO]):
        """
        PDF 보고서 생성

        Args:
            summary: 데이터 요약
            all_data: 전체 수집 데이터
            graphs: 그래프 이미지 딕셔너리
        """
        # 제목 추가
        self.add_title()

        # 요약 섹션
        self.add_summary_section(summary)

        # 페이지 나누기
        self.story.append(PageBreak())

        # CPU 섹션
        self.add_cpu_section(summary, all_data[0])

        # 메모리 섹션
        self.add_memory_section(summary, all_data[0])

        # 페이지 나누기
        self.story.append(PageBreak())

        # 디스크 섹션
        self.add_disk_section(all_data[0])

        # 네트워크 섹션
        self.add_network_section(summary)

        # 페이지 나누기
        self.story.append(PageBreak())

        # 그래프 섹션
        heading = Paragraph("6. 그래프 및 시각화", self.styles['CustomHeading'])
        self.story.append(heading)
        self.story.append(Spacer(1, 12))

        # 통합 개요 그래프
        if 'overview' in graphs and graphs['overview']:
            self.add_graph(graphs['overview'], "6.1 시스템 리소스 개요")
            self.story.append(PageBreak())

        # CPU 그래프
        if 'cpu' in graphs and graphs['cpu']:
            self.add_graph(graphs['cpu'], "6.2 CPU 사용률 추이")

        # 메모리 그래프
        if 'memory' in graphs and graphs['memory']:
            self.add_graph(graphs['memory'], "6.3 메모리 사용률 추이")
            self.story.append(PageBreak())

        # 네트워크 그래프
        if 'network' in graphs and graphs['network']:
            self.add_graph(graphs['network'], "6.4 네트워크 트래픽 추이")

        # CPU 온도 그래프
        if 'cpu_temp' in graphs and graphs['cpu_temp']:
            self.add_graph(graphs['cpu_temp'], "6.5 CPU 온도 추이")

        # 디스크 그래프
        if 'disk' in graphs and graphs['disk']:
            self.add_graph(graphs['disk'], "6.6 디스크 사용률 추이")

        # PDF 빌드
        self.doc.build(self.story)
        print(f"\nPDF 보고서가 생성되었습니다: {self.filename}")
