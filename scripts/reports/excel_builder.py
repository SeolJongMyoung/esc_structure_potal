"""
excel_builder.py  — Facade
이 파일은 하위 호환성을 위한 Facade 역할만 담당합니다.
실제 보고서 생성 로직은 reports/excel/ 하위 모듈이 처리합니다.

  설계법 → Builder 매핑:
    LSD계열          → LSDExcelBuilder       (reports/excel/lsd_excel_builder.py)
    KCI/KDS계열      → KCIExcelBuilder       (reports/excel/kci_excel_builder.py)
    USD 2010(기본)   → USD2010ExcelBuilder   (reports/excel/usd_2010_excel_builder.py)
"""
from .excel import get_excel_builder


class ExcelReportBuilder:
    """
    설계법에 맞는 ExcelBuilder 인스턴스를 투명하게 위임하는 Facade 클래스.
    기존 사용 코드는 변경 없이 그대로 동작한다.
    """

    def __init__(self, analyzer):
        self._builder = get_excel_builder(analyzer)

    def add_to_workbook(self, wb, sheet_name):
        return self._builder.add_to_workbook(wb, sheet_name)
