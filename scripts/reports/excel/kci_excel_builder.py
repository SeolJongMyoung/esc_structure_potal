"""
kci_excel_builder.py
강도설계법(콘크리트구조설계기준, KCI/KDS) 전용 Excel 보고서 빌더.
"""
from .base_excel_builder import BaseExcelBuilder


class KCIExcelBuilder(BaseExcelBuilder):
    """강도설계법(콘크리트구조설계기준, KCI/KDS) 전용 Excel 보고서 빌더."""

    def _write_section6(self, ws) -> int:
        """6) 철근비 검토 — KCI 상세 방식 (최소/최대 철근량 상세 수식)."""
        ana     = self.analyzer
        min_res = ana.min_rebar_res
        max_res = ana.max_rebar_res

        mcr_knm    = min_res['mcr'] / 1e6
        limit_1    = 1.2 * min_res['mcr']
        limit_2    = (4.0 / 3.0) * ana.Mu_nm
        ig         = min_res['ig']
        fr         = min_res['fr']
        phi_mn_knm = ana.M_r / 1e6

        ws['B31'].value = "* 철근비 검토"
        ws['C32'].value = "* 최소 철근량 검토"
        ws['C33'].value = f"Ig = bh\u00b3 / 12 = {ana.beam_b:.2f} \u00d7 {ana.beam_h:.2f}\u00b3 / 12 = {ig:,.0f} mm\u2074"
        ws['C34'].value = f"fr = 0.63\u03bb\u221a(fck) = 0.63 \u00d7 1.0 \u00d7 \u221a({ana.f_ck}) = {fr:.3f}"
        ws['C35'].value = f"Mcr = fr \u00d7 Ig / yt = {fr:.3f} \u00d7 {ig:,.0f} / ({ana.beam_h:.2f} / 2) = {mcr_knm:,.3f} kN.m"

        compare_sign = "<" if limit_1 < limit_2 else "\u2265"
        ws['C36'].value = f"1.2Mcr = 1.2 \u00d7 {mcr_knm:,.3f} = {limit_1/1e6:,.3f} kN.m {compare_sign} 4/3Mu = 4/3 \u00d7 {ana.Mu:,.3f} = {limit_2/1e6:,.3f} kN.m"

        status_min = "만족" if min_res['is_ok'] else "불만족"
        ok_ng_min  = "O.K"  if min_res['is_ok'] else "N.G"
        ws['C37'].value = f"\u03a6Mn = {phi_mn_knm:,.3f} kN.m \u2265 1.2Mcr = {limit_1/1e6:,.3f} kN.m  최소철근량 {status_min}, \u2234 {ok_ng_min}"

        rho_max    = max_res['rho_max']
        rho_use    = max_res['rho_use']
        status_max = "만족" if max_res['is_ok'] else "불만족"
        ok_ng_max  = "O.K"  if max_res['is_ok'] else "N.G"
        ecu        = 0.0033
        es         = 200000.0
        alpha_val  = 0.85 if ana.f_ck <= 28 else max(0.65, 0.85 - (ana.f_ck - 28) * 0.007)

        ws['B39'].value = "* 최대 철근비 검토"
        ws['C40'].value = f"\u03c1max = 0.726 \u00d7 Pb = 0.726 \u00d7 \u03b1 \u00d7 0.85 \u00d7 (fck / fy) \u00d7 (\u03b5cu \u00d7 Es) / (\u03b5cu \u00d7 Es + fy)"
        ws['C41'].value = f"     = 0.726 \u00d7 {alpha_val:.3f} \u00d7 0.85 \u00d7 ({ana.f_ck:.0f} / {ana.f_y:.0f}) \u00d7 ({ecu:.4f} \u00d7 {es:.2f}) / ({ecu:.4f} \u00d7 {es:.2f} + {ana.f_y:.0f})"
        ws['C42'].value = f"     = {rho_max:.5f}"
        ws['C43'].value = f"\u03c1use = As / bd = {rho_use:.5f}"
        compare_sign_max = "<" if rho_use <= rho_max else ">"
        ws['C44'].value = f"\u03c1use {compare_sign_max} \u03c1max \u2192 철근비 {status_max}, \u2234 {ok_ng_max}"

        return 8  # row_offset: 8행 추가됨
