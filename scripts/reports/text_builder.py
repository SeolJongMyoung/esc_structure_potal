"""
text_builder.py  — Facade
이 파일은 하위 호환성을 위한 Facade 역할만 담당합니다.
실제 보고서 생성 로직은 reports/text/ 하위 모듈이 처리합니다.

  설계법 → Builder 매핑:
    LSD계열          → LSDTextBuilder        (reports/text/lsd_text_builder.py)
    KCI/KDS계열      → KCITextBuilder        (reports/text/kci_text_builder.py)
    USD 2010(기본)   → USD2010TextBuilder    (reports/text/usd_2010_text_builder.py)
"""
from .text import get_text_builder


class TextReportBuilder:
    """
    설계법에 맞는 TextBuilder 인스턴스를 투명하게 위임하는 Facade 클래스.
    기존 사용 코드는 변경 없이 그대로 동작한다.
    """

    def __init__(self, analyzer):
        self._builder = get_text_builder(analyzer)

    def generate(self):
        return self._builder.generate()
