"""
text/__init__.py
설계법에 맞는 Text Builder를 반환하는 Factory 함수.
"""
from .usd_2010_text_builder import USD2010TextBuilder
from .kci_text_builder import KCITextBuilder
from .lsd_text_builder import LSDTextBuilder


def get_text_builder(analyzer):
    """
    analyzer의 설계기준에 따라 적합한 TextBuilder 인스턴스를 반환한다.

    Args:
        analyzer: RCSectionAnalyzer 인스턴스

    Returns:
        해당 설계법 전용 TextBuilder 인스턴스
    """
    std_name = analyzer.standard.name
    method   = analyzer.method  # "USD" or "LSD"

    if method == "LSD":
        return LSDTextBuilder(analyzer)

    # USD 계열 분기
    if "콘크리트" in std_name or "KCI" in std_name or "KDS" in std_name:
        return KCITextBuilder(analyzer)

    # 기본: 강도설계법 (도로교 설계기준, 2010)
    return USD2010TextBuilder(analyzer)
