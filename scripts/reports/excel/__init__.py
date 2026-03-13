"""
excel/__init__.py
설계법에 맞는 Excel Builder를 반환하는 Factory 함수.
"""
from .usd_2010_excel_builder import USD2010ExcelBuilder
from .kci_excel_builder import KCIExcelBuilder
from .lsd_excel_builder import LSDExcelBuilder


def get_excel_builder(analyzer):
    """
    analyzer의 설계기준에 따라 적합한 ExcelBuilder 인스턴스를 반환한다.

    Args:
        analyzer: RCSectionAnalyzer 인스턴스

    Returns:
        해당 설계법 전용 ExcelBuilder 인스턴스
    """
    std_name = analyzer.standard.name
    method   = analyzer.method  # "USD" or "LSD"

    if method == "LSD":
        return LSDExcelBuilder(analyzer)

    # USD 계열 분기
    if "콘크리트" in std_name or "KCI" in std_name or "KDS" in std_name:
        return KCIExcelBuilder(analyzer)

    # 기본: 강도설계법 (도로교 설계기준, 2010)
    return USD2010ExcelBuilder(analyzer)
