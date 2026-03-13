"""
base_text_builder.py
모든 설계법 Text Builder가 공통으로 사용하는 기반 클래스.
- 섹션 1~5 (단면제원, 재료상수, 강도감소계수, 필요/사용철근량) 공통 구현
- 전단 및 균열 검토 공통 구현 (USD 계열)
- 서브클래스에서 반드시 구현해야 하는 메서드 선언
"""
from abc import ABC, abstractmethod


class BaseTextBuilder(ABC):
    """
    USD 계열 설계법(USD2010, KCI 등) 텍스트 보고서의 공통 Base 클래스.
    공통 섹션은 여기서 구현하고, 설계법별 차이나는 부분만 서브클래스에서 구현한다.
    """

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.std = analyzer.standard

    def generate(self):
        """보고서를 생성하여 딕셔너리로 반환한다."""
        try:
            ana = self.analyzer
            header = self._build_header()
            flex_all = self._build_flexure_sections(header)
            shear = self._build_shear_section()
            service = self._build_service_section()

            total = []
            total.extend(flex_all)
            total.append("")
            total.extend(shear)
            total.append("")
            total.extend(service)

            return {
                "total": "\n".join(total),
                "flexure": "\n".join(flex_all),
                "shear": "\n".join(shear),
                "service": "\n".join(service),
            }
        except Exception as e:
            import traceback
            err_msg = f"보고서 생성 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
            return {"total": err_msg, "flexure": err_msg, "shear": err_msg, "service": err_msg}

    # ── 공통 섹션 ────────────────────────────────────────────────────────────

    def _build_header(self):
        """설계법 이름을 포함한 공통 보고서 헤더를 생성한다."""
        header = []
        header.append("=" * 75)
        header.append(f"{self.std.name:^75}")
        header.append(f"{'강도설계법(USD)에 의한 단면 검토 보고서':^75}")
        header.append("=" * 75)
        header.append("")
        return header

    def _build_sec1(self):
        """1) 단면제원 및 설계가정"""
        ana = self.analyzer
        sec = []
        sec.append("1) 단면제원 및 설계가정")
        sec.append(f"   fck = {ana.f_ck:.1f} MPa, fy = {ana.f_y:.1f} MPa, \u03a6f = {ana.pi_f_r:.2f}, \u03a6v = {ana.pi_v:.2f}, Es = {ana.E_s:.0f} MPa")
        sec.append("   " + "-" * 90)
        sec.append(f"   | {'B(mm)':^8} | {'H(mm)':^8} | {'d(mm)':^8} | {'피복(mm)':^8} | {'Mu(kN.m)':^10} | {'Vu(kN)':^10} | {'Ms(kN.m)':^10} |")
        sec.append("   " + "-" * 90)
        sec.append(f"   | {ana.beam_b:^8.0f} | {ana.beam_h:^8.0f} | {ana.d_eff:^8.1f} | {ana.d_c:^8.1f} | {ana.Mu:^10.3f} | {ana.Vu:^10.3f} | {ana.Ms:^10.3f} |")
        sec.append("   " + "-" * 90)
        return sec

    def _build_sec2(self):
        """2) 콘크리트 재료상수"""
        ana = self.analyzer
        sec = []
        sec.append("2) 콘크리트 재료상수")
        sec.append(f"   \u03b21   : 등가 사각형 응력 블록의 깊이계수           = {ana.standard.get_beta_1(ana.f_ck):.3f}")
        return sec

    def _build_sec3(self):
        """3) 강도감소계수(Ø) 산정"""
        ana = self.analyzer
        sec = []
        sec.append("3) 강도감소계수(\u03a6) 산정")
        sec.append(f"   T = As \u00d7 fy = {ana.as_use:.1f} \u00d7 {ana.f_y:.1f} = {ana.tension_force:.1f} N")
        sec.append(f"   C = 0.85 \u00d7 fck \u00d7 a \u00d7 b = 0.85 \u00d7 {ana.f_ck:.1f} \u00d7 a \u00d7 {ana.beam_b:.1f} = {0.85*ana.f_ck*ana.beam_b:.1f} \u00d7 a")
        sec.append(f"   T = C 이므로, a = {ana.a:.3f} mm, c = a / \u03b21 = {ana.a:.3f} / {ana.standard.get_beta_1(ana.f_ck):.3f} = {ana.c:.3f} mm")
        sec.append(f"   \u03b5y = fy / Es = {ana.f_y:.1f} / {ana.E_s:.0f} = {ana.epsilon_y:.5f}")
        sec.append(f"   \u03b5t = 0.00300 \u00d7 (dt - c) / c = 0.00300 \u00d7 ({ana.dt:.3f} - {ana.c:.3f}) / {ana.c:.3f} = {ana.epsilon_t:.5f}")
        compare_op = "\u2265" if ana.epsilon_t >= 0.005 else "<"
        sec.append(f"   \u03b5t {compare_op} 0.0050 이므로 {ana.epsilon_t_result}이며, \u03a6 = {ana.pi_f_r:.2f} 를 적용한다")
        return sec

    def _build_sec4(self):
        """4) 필요철근량 산정"""
        ana = self.analyzer
        sec = []
        sec.append("4) 필요철근량 산정")
        sec.append("   Mu / \u03a6f = As \u00d7 fy \u00d7 (d - a / 2)              ---------------- \u2460")
        sec.append("   a = As \u00d7 fy / (0.85 \u00d7 fck \u00d7 b)               ---------------- \u2461")
        sec.append("   식\u2461를 식\u2460에 대입하여 이차방정식으로 As를 구한다")
        sec.append("           fy\u00b2                                Mu")
        sec.append(f"   ------------------ As\u00b2 - fy \u00d7 d \u00d7 As + ------ = 0 ,  Asreq = {ana.as_req:.1f} mm\u00b2")
        sec.append(f"    2 \u00d7 0.85 \u00d7 fck \u00d7 b                         \u03a6f")
        return sec

    def _build_sec5(self):
        """5) 사용철근량"""
        ana = self.analyzer
        sec = []
        usage_ratio = ana.as_use / ana.as_req if ana.as_req > 0 else 9.99
        sec.append(f"5) 사용철근량 : Asuse = {ana.as_use:.1f} mm\u00b2, 철근도심 : dc_avg = {ana.d_c:.1f} mm, [ 사용율 = {usage_ratio:.3f} ]")
        sec.append(f"   1단 : D {ana.as_dia1} - {ana.as_num1} EA (= {ana.as_use1:.1f} mm\u00b2, dc1 = {ana.dc_1:.1f} mm)")
        if ana.as_num2 > 0:
            sec.append(f"   2단 : D {ana.as_dia2} - {ana.as_num2} EA (= {ana.as_use2:.1f} mm\u00b2, dc2 = {ana.dc_2:.1f} mm)")
        if ana.as_num3 > 0:
            sec.append(f"   3단 : D {ana.as_dia3} - {ana.as_num3} EA (= {ana.as_use3:.1f} mm\u00b2, dc3 = {ana.dc_3:.1f} mm)")
        return sec

    def _build_sec7(self):
        """6) 설계 휨강도 산정"""
        ana = self.analyzer
        sec = []
        sec.append("6) 설계 휨강도 산정")
        sec.append(f"   a = As \u00d7 fy / (0.85 \u00d7 fck \u00d7 b) = {ana.a:.3f} mm")
        sec.append(f"   \u03a6 Mn = \u03a6f \u00d7 As \u00d7 fy \u00d7 (d - a / 2)")
        sec.append(f"        = {ana.pi_f_r:.2f} \u00d7 {ana.as_use:.1f} \u00d7 {ana.f_yd} \u00d7 ({ana.d_eff:.1f} - {ana.a:.3f} / 2)")
        res_f = "O.K" if ana.M_r >= ana.Mu_nm else "N.G"
        sec.append(f"        = {ana.M_r/1e6:.1f} kN.m \u2500\u2500\u2500> {res_f} (Mu = {ana.Mu:.1f} kN.m) [S.F = {ana.M_sf:.3f}]")
        return sec

    def _build_shear_section(self):
        """7) 전단검토"""
        ana = self.analyzer
        shear = []
        shear.append("7) 전단검토")
        shear.append(f"   \u03a6 Vc = \u03a6v \u00d7 \u221afck \u00d7 b \u00d7 d / 6")
        shear.append(f"      = {ana.pi_v:.2f} \u00d7 \u221a{ana.f_ck:.1f} \u00d7 {ana.beam_b:.1f} \u00d7 {ana.d_eff:.1f} / 6 = {ana.pi_V_c/1e3:.1f} kN")
        if ana.pi_V_c >= ana.Vu_n:
            shear.append(f"   \u03a6 Vc \u2265 Vu = {ana.Vu:.1f} kN  \u2234 전단보강 불필요")
        else:
            shear.append(f"   \u03a6 Vc < Vu = {ana.Vu:.1f} kN  \u2234 전단보강 필요")
            shear.append(f"   Vs_req = (Vu - \u03a6Vc) / \u03a6v = {(ana.Vu_n - ana.pi_V_c)/ana.pi_v/1e3:.1f} kN")
            shear.append(f"   Av_use = {ana.av_use:.1f} mm\u00b2 (D{ana.av_dia}-{ana.av_leg:.0f}EA, CTC {ana.av_space:.0f})")
            shear.append(f"   Vs_use = Av \u00d7 fy \u00d7 d / s = {ana.V_s/1e3:.1f} kN")
            res_vmax = "O.K" if ana.V_s <= ana.V_s_max else "N.G"
            shear.append(f"   Vs_max = (2/3) \u00d7 \u221afck \u00d7 b \u00d7 d = {ana.V_s_max/1e3:.1f} kN \u2234 {res_vmax}")
            v_total_kn = (ana.pi_V_c + ana.pi_v * ana.V_s) / 1e3
            vu_kn = ana.Vu
            compare_op = "\u2265" if v_total_kn >= vu_kn else "<"
            res_v = "O.K" if v_total_kn >= vu_kn and ana.V_s <= ana.V_s_max else "N.G"
            shear.append(f"   \u03a6(Vc + Vs) = {v_total_kn:.1f} kN {compare_op} Vu = {vu_kn:.1f} kN \u2234 {res_v}")
        return shear

    def _build_service_section(self):
        """8) 균열검토"""
        ana = self.analyzer
        service = []
        service.append("8) 균열검토")
        service.append("    \u2460 응력 산정")
        service.append(f"       fs = Ms / [As \u00d7 (d - x/3)] = {ana.Ms_nm:.1f} / [ {ana.as_use:.1f} \u00d7 ( {ana.d_eff:.3f} - {ana.chi_o:.2f} / 3 ) ]")
        service.append(f"          = {ana.f_s:.3f} MPa")
        service.append(f"       x = -n \u00d7 As / b + n \u00d7 As / b \u00d7 \u221a [ 1 + 2 \u00d7 b \u00d7 d / ( n \u00d7 As ) ]")
        service.append(f"         = -{ana.nr:.1f} \u00d7 {ana.as_use:.1f} / {ana.beam_b:.1f} + {ana.nr:.1f} \u00d7 {ana.as_use:.1f} / {ana.beam_b:.1f} \u00d7 \u221a [ 1 + 2 \u00d7 {ana.beam_b:.1f} \u00d7 {ana.d_eff:.1f} / ( {ana.nr:.1f} \u00d7 {ana.as_use:.1f} ) ]")
        service.append(f"         = {ana.chi_o:.3f} mm")
        service.append(f"       사용철근량 = {ana.as_use:.1f} mm\u00b2  (철근군 평균도심 : {ana.d_c:.1f} mm)")
        service.append(f"       1단 : D{ana.as_dia1}-{ana.as_num1}EA, 2단 : D{ana.as_dia2}-{ana.as_num2}EA, 3단 : D{ana.as_dia3}-{ana.as_num3}EA")
        service.append("")
        service.append("    \u2461 철근의 최대 중심간격")
        service.append(f"       강재의 부식에 대한 환경조건은 \u300e {ana.crack_case} \u300f 적용")
        service.append(f"       Cc = {ana.dc_1:.1f} - {ana.as_dia1} / 2 = {ana.c_c:.2f} mm")
        service.append("       여기서 Cc : 인장철근이나 긴장재의 표면과 콘크리트 표면사이의 두께(mm)")
        service.append("")
        service.append(f"       Smin : 375 \u00d7 (Kcr / fs) - 2.5 \u00d7 Cc = 375 \u00d7 ({ana.k_cr} / {ana.f_s:.3f}) - 2.5 \u00d7 {ana.c_c:.3f} = {ana.s_min_1:.3f} mm")
        service.append(f"              300 \u00d7 (Kcr / fs) = 300 \u00d7 ({ana.k_cr} / {ana.f_s:.3f}) = {ana.s_min_2:.3f} mm")
        service.append(f"       여기서 Kcr = {ana.k_cr} ( 철근 간격을 통한 균열 검증에서 철근의 노출 조건을 고려한 계수 )")
        service.append(f"       \u2234 Sa는 작은 값인 {ana.s_min:.3f} mm 를 적용")
        service.append(f"       Sa = {ana.s_min:.3f} mm  \u2265 suse = {ana.s_use:.3f} mm  \u2234 {ana.crack_status}")
        return service

    def _build_flexure_sections(self, header):
        """공통 휨 섹션(1~5, 7)을 조합하되 섹션6(철근비)은 서브클래스가 구현한다."""
        flex_all = []
        flex_all.extend(header)
        flex_all.extend(self._build_sec1()); flex_all.append("")
        flex_all.extend(self._build_sec2()); flex_all.append("")
        flex_all.extend(self._build_sec3()); flex_all.append("")
        flex_all.extend(self._build_sec4()); flex_all.append("")
        flex_all.extend(self._build_sec5()); flex_all.append("")
        flex_all.extend(self._build_sec6()); flex_all.append("")
        flex_all.extend(self._build_sec7())
        return flex_all

    # ── 서브클래스에서 구현 필수 ───────────────────────────────────────────────

    @abstractmethod
    def _build_sec6(self):
        """6) 철근비 검토 — 설계법마다 출력 형식이 다르므로 서브클래스에서 구현."""
        pass
