"""
usd_2010_excel_builder.py
강도설계법(도로교 설계기준, 2010) 전용 Excel 보고서 빌더.
"""
from .base_excel_builder import BaseExcelBuilder


class USD2010ExcelBuilder(BaseExcelBuilder):
    """강도설계법(도로교 설계기준, 2010) 전용 Excel 보고서 빌더."""

    def _write_section6(self, ws) -> int:
        """6) 철근비 검토 — 간략 방식 (ρmin / ρmax)."""
        ana = self.analyzer
        ws['B31'].value = "* 철근비 검토"
        ws['C32'].value = f"ρmin : 1.4 / fy          = {ana.lo_min_1:.6f} "
        ws['C33'].value = f"       0.25 x √fck / fy  = {ana.lo_min_2:.6f},  ρmin = {ana.lo_min:.6f} 적용"
        ws['C34'].value = f"ρmax = 0.75 x ρb = 0.75 x (0.85 x β1 x fck / fy) x (600 / (600 + fy)) = {ana.lo_bal:.6f}"
        ws['C35'].value = f"ρuse = As / ( b x d ) = {ana.lo_use:.6f} "
        if ana.lo_use >= ana.lo_min:
            if ana.lo_use < ana.lo_max:
                ws['C36'].value = "ρmax ≥ ρuse ≥ ρmin --> 최소철근비, 최대철근비 만족   ∴ O.K"
            else:
                ws['C36'].value = "ρmax < ρuse ≥ ρmin --> 최소철근비 만족, 최대 철근비 불만족   ∴ N.G"
        else:
            if ana.lo_use < ana.lo_max:
                ws['C36'].value = "ρmax ≥ ρuse < ρmin --> 최소철근비 불만족,  최대 철근비 만족   ∴ N.G"
                if ana.lo_use >= ana.lo_min_3:
                    ws['C37'].value = f"ρuse ≥ 4 x ρreq / 3 = {ana.lo_min_3:.6f} --> 최소철근비 만족   ∴ O.K"
                else:
                    ws['C37'].value = f"ρuse < 4 x ρreq / 3 = {ana.lo_min_3:.6f} --> 최소철근비 불만족   ∴ N.G"
            else:
                ws['C36'].value = "ρmax < ρuse < ρmin --> 최소철근비, 최대 철근비 불만족   ∴ N.G"
        return 0  # row_offset: 추가된 행 없음
