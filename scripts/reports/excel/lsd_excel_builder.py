"""
lsd_excel_builder.py
한계상태설계법(LSD) 전용 Excel 보고서 빌더.
"""
from .base_excel_builder import BaseExcelBuilder
from openpyxl.styles import Font, Alignment
import math

class LSDExcelBuilder(BaseExcelBuilder):
    """한계상태설계법(LSD) 전용 Excel 보고서 빌더."""

    def add_to_workbook(self, wb, sheet_name):
        """LSD 전용 동적 행 구조로 워크북에 시트를 추가한다."""
        wsout = wb.create_sheet(title=sheet_name)
        self._setup_sheet(wsout)
        self._write_header(wsout)
        
        curr = 2 
        curr = self._write_section1_lsd(wsout, curr)
        curr = self._write_section2_lsd(wsout, curr)
        curr = self._write_section3_lsd(wsout, curr)
        curr = self._write_section4_lsd(wsout, curr)
        curr = self._write_section5_lsd(wsout, curr)
        curr = self._write_section6_lsd(wsout, curr)
        curr = self._write_flexure_strength_lsd(wsout, curr)
        curr = self._write_shear_lsd(wsout, curr)
        self._write_crack_lsd(wsout, curr)

    def _write_section1_lsd(self, ws, row):
        ana = self.analyzer
        ws.cell(row, 2).value = '1) 단면제원 및 설계가정'
        ws.cell(row+1, 3).value = f"fck = {ana.f_ck} MPa, fy = {ana.f_y} MPa, \u03a6c = {ana.phi_c:.2f}, \u03a6s = {ana.phi_s:.2f}, Es = {ana.E_s} MPa"
        ws.cell(row+2, 3).value = f"B={ana.beam_b}mm, H={ana.beam_h}mm, d={ana.d_eff:.1f}mm, Mu={ana.Mu_nm/1e6:.2f}kN.m, Vu={ana.Vu_n/1e3:.1f}kN, Ms={ana.Ms_nm/1e6:.2f}kN.m"
        return row + 4

    def _write_section2_lsd(self, ws, row):
        """2) 콘크리트 재료상수 — 이미지와 100% 동일."""
        ana = self.analyzer
        con = ana.con_material
        ws.cell(row, 2).value = '2) 콘크리트 재료상수'
        
        eta_val = ana.alpha_fac / con.alpha_cc
        items = [
            (f"n", f"상승 곡선부의 형상을 나타내는 지수", f"{con.n_eps:.2f}"),
            (f"\u03b5co,r", f"최대응력에 처음 도달했을때의 변형률", f"{con.eps_co:.4f}"),
            (f"\u03b5cu,r", f"극한변형률", f"{con.eps_cu:.4f}"),
            (f"\u03b1cc", f"유효계수", f"{ana.alpha_cc:.2f}"),
            (f"fcd", f"콘크리트 설계압축강도 ( fck \u00d7 \u03a6c \u00d7 \u03b1cc )", f"{ana.f_cd:.3f} MPa"),
            (f"fcm", f"평균압축강도 ( fck + \u0394f )", f"{con.f_cm:.1f} MPa"),
            (f"Ec", f"0.077 mc^1.5 \u221bfcm", f"{con.E_c:.1f} MPa"),
            (f"\u03b1", f"압축합력의 평균 응력계수", f"{ana.alpha_fac:.2f}"),
            (f"\u03b2", f"압축합력의 작용점 위치계수", f"{ana.beta_fac:.2f}"),
            (f"\u03b7", f"등가 사각형 응력 블록의 크기계수", f"{eta_val:.2f}"),
            (f"\u03b21", f"등가 사각형 응력 블록의 깊이계수 ( 2\u03b2 )", f"{ana.beta_fac*2:.2f}"),
        ]
        for i, (sym, desc, val) in enumerate(items):
            r = row + 1 + i
            ws.cell(r, 3).value = f"{sym:<6} : {desc:<40} = {val:>10}"
        return row + 1 + len(items) + 1

    def _write_section3_lsd(self, ws, row):
        """3) 철근 재료상수 및 강도감소계수."""
        ana = self.analyzer
        ws.cell(row, 2).value = '3) 철근 재료상수 및 강도감소계수'
        ws.cell(row+1, 3).value = f"fyd : 설계인장강도 ( \u03a6s fy ) = {ana.f_yd:.1f} MPa"
        ws.cell(row+2, 3).value = f"\u03b5yd : 설계 항복 변형률 ( fyd / Es ) = {ana.f_yd/ana.E_s:.5f}"
        
        ws.cell(row+4, 3).value = f"T = As x fyd = {ana.tension_force:.1f} N"
        ws.cell(row+5, 3).value = f"C = \u03b7 x fcd x a x b = {ana.compression_force:.1f} x a"
        ws.cell(row+6, 3).value = f"a = {ana.a:.3f} mm, c = {ana.c:.3f} mm"
        ep_t = ana.epsilon_t if hasattr(ana, 'epsilon_t') else (0.0033 * (ana.d_eff - ana.c) / ana.c if ana.c > 0 else 0)
        ws.cell(row+7, 3).value = f"\u03b5t = {ep_t:.5f} (d={ana.d_eff:.1f}) -> \u03a6c = {ana.phi_c:.2f}"
        return row + 9

    def _write_section4_lsd(self, ws, row):
        ana = self.analyzer
        ws.cell(row, 2).value = '4) 필요철근량 산정'
        ws.cell(row+1, 3).value = f"As_req = {ana.as_req:.3f} mm\u00b2"
        return row + 3

    def _write_section5_lsd(self, ws, row):
        ana = self.analyzer
        usage = ana.as_use / ana.as_req if ana.as_req > 0 else 1.0
        ws.cell(row, 2).value = '5) 사용철근량'
        ws.cell(row+1, 3).value = f"As_use = {ana.as_use:.1f} mm\u00b2 ( Ratio = {usage:.3f} )"
        ws.cell(row+2, 4).value = f"1단: {ana.as_dia1}-{ana.as_num1}EA, 2단: {ana.as_dia2}-{ana.as_num2}EA"
        return row + 4

    def _write_section6_lsd(self, ws, row):
        ana = self.analyzer
        ws.cell(row, 2).value = '6) 철근비 검토'
        ws.cell(row+1, 3).value = f"\u03c1min = {ana.lo_min:.6f}, \u03c1max = {ana.lo_max:.6f}, \u03c1use = {ana.lo_use:.6f}"
        status = "O.K" if ana.lo_min <= ana.lo_use <= ana.lo_max else "N.G"
        ws.cell(row+2, 3).value = f"Result: {status}"
        return row + 4

    def _write_flexure_strength_lsd(self, ws, row):
        ana = self.analyzer
        ws.cell(row, 2).value = "7) 설계 휨강도 산정"
        ws.cell(row+1, 3).value = f"Mr = {ana.M_r/1e6:.2f} kN.m \u2265 Mu = {ana.Mu:.2f} kN.m  .. {'O.K' if ana.M_r >= ana.Mu_nm else 'N.G'}"
        return row + 3

    def _write_shear_lsd(self, ws, row):
        ana = self.analyzer
        vd = getattr(ana, 'v_details', {})
        ws.cell(row, 2).value = "8) 전단검토"
        vcd = vd.get('Vcd_calc', 0)
        ws.cell(row+1, 3).value = f"Vcd = {vcd/1e3:.1f} kN ( \u03ba={vd.get('k',0):.3f}, \u03c1={vd.get('rho_l',0):.5f}, fctk={vd.get('f_ctk',0):.3f} )"
        ws.cell(row+2, 3).value = f"Ac = {vd.get('Ac', ana.beam_b * ana.beam_h):.1f} mm\u00b2, fn = {vd.get('fn',0):.3f} MPa"
        
        if ana.pi_V_c < ana.Vu_n:
            vsd = ana.V_s / 1e3
            ws.cell(row+3, 3).value = f"Vsd = {vsd:.1f} kN, Vd,max = {vd.get('Vdmax2',0)/1e3:.1f} kN  .. {'O.K' if vd.get('Vdmax2',0) >= ana.V_s else 'N.G'}"
            v_tot = (ana.pi_V_c + ana.V_s) / 1e3
            ws.cell(row+4, 3).value = f"Total Vd = {v_tot:.1f} kN \u2265 Vu = {ana.Vu:.1f} kN .. {'O.K' if v_tot >= ana.Vu else 'N.G'}"
            return row + 6
        else:
            ws.cell(row+3, 3).value = f"Vcd = {ana.pi_V_c/1e3:.1f} kN \u2265 Vu = {ana.Vu:.1f} kN : 전단보강 불필요"
            return row + 5

    def _write_crack_lsd(self, ws, row):
        ana = self.analyzer
        sd = getattr(ana, 'service_details', {})
        if not sd: return
        ws.cell(row, 2).value = "9) 균열 및 철근 간격 검토"
        as_min = sd.get('as_min_lsd', 0)
        ws.cell(row+1, 3).value = f"\u2460 최소철근량: As_min = {as_min:.2f} mm\u00b2 .. {'O.K' if ana.as_use >= as_min else 'N.G'}"
        ws.cell(row+2, 3).value = f"\u2461 철근응력: fs = {sd.get('fs', 0):.3f} MPa \u2264 fsa = {sd.get('fsa',0):.1f} MPa .. {'O.K' if sd.get('fs',0) <= sd.get('fsa',0) else 'N.G'}"
        
        dia_limit = sd.get('max_dia_limit', 0)
        dia_use = ana.as_dia1
        ws.cell(row+3, 3).value = f"\u2462 직경검토: \u03a6_use = {dia_use:.0f} mm \u2264 \u03a6_limit = {dia_limit:.1f} mm .. {'O.K' if dia_use <= dia_limit else 'N.G'}"
        
        s_use = ana.beam_b / ana.as_num1 if ana.as_num1 > 0 else 0
        sa_limit = sd.get('sa_limit', 300)
        s_table = sd.get('s_table_limit', 300)
        ws.cell(row+4, 3).value = f"\u2463 간격검토: S = {s_use:.1f} mm \u2264 Sa = min(3d, {s_table:.1f}) = {sa_limit:.1f} mm .. {'O.K' if s_use <= sa_limit else 'N.G'}"

    # Base overrides (unused in LSD but required to avoid mess)
    def _write_section6(self, ws): return 0
    def _write_flexure_strength(self, ws, offset): pass
    def _write_shear(self, ws, offset): pass
    def _write_crack(self, ws, offset): pass
