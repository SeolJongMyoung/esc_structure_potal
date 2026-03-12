class TextReportBuilder:
    """
    RCSectionAnalyzer의 연산 결과를 받아 텍스트 보고서를 생성하는 클래스.
    설계기준(standard)에 따라 유연하게 문구를 조정할 수 있도록 설계.
    """
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.std = analyzer.standard

    def generate(self):
        try:
            if self.analyzer.method == "LSD":
                return self._generate_lsd_report()
            
            # Default USD Report
            header = []
            header.append("=" * 75)
            header.append(f"{self.std.name:^75}")
            header.append(f"{'강도설계법(USD)에 의한 단면 검토 보고서':^75}")
            header.append("=" * 75)
            header.append("")

            total_data = self._generate_usd_report(header)
            return total_data
        except Exception as e:
            err_msg = f"보고서 생성 중 오류 발생: {str(e)}"
            return {"total": err_msg, "flexure": err_msg, "shear": err_msg, "service": err_msg}

    def _generate_usd_report(self, header):
        # Migrated original USD logic here
        ana = self.analyzer
        sec1 = []
        sec1.append("1) 단면제원 및 설계가정")
        sec1.append(f"   fck = {ana.f_ck:.1f} MPa, fy = {ana.f_y:.1f} MPa, \u03a6f = {ana.pi_f_r:.2f}, \u03a6v = {ana.pi_v:.2f}, Es = {ana.E_s:.0f} MPa")
        sec1.append("   " + "-"*90)
        sec1.append(f"   | {'B(mm)':^8} | {'H(mm)':^8} | {'d(mm)':^8} | {'피복(mm)':^8} | {'Mu(kN.m)':^10} | {'Vu(kN)':^10} | {'Ms(kN.m)':^10} |")
        sec1.append("   " + "-"*90)
        sec1.append(f"   | {ana.beam_b:^8.0f} | {ana.beam_h:^8.0f} | {ana.d_eff:^8.1f} | {ana.d_c:^8.1f} | {ana.Mu:^10.3f} | {ana.Vu:^10.3f} | {ana.Ms:^10.3f} |")
        sec1.append("   " + "-"*90)
        
        sec2 = []
        sec2.append("2) 콘크리트 재료상수")
        sec2.append(f"   \u03b21   : 등가 사각형 응력 블록의 깊이계수           = {ana.standard.get_beta_1(ana.f_ck):.3f}")
        
        sec3 = []
        sec3.append("3) 강도감소계수(\u03a6) 산정")
        sec3.append(f"   T = As \u00d7 fy = {ana.as_use:.1f} \u00d7 {ana.f_y:.1f} = {ana.tension_force:.1f} N")
        sec3.append(f"   C = 0.85 \u00d7 fck \u00d7 a \u00d7 b = 0.85 \u00d7 {ana.f_ck:.1f} \u00d7 a \u00d7 {ana.beam_b:.1f} = {0.85*ana.f_ck*ana.beam_b:.1f} \u00d7 a")
        sec3.append(f"   T = C 이므로, a = {ana.a:.3f} mm, c = a / \u03b21 = {ana.a:.3f} / {ana.standard.get_beta_1(ana.f_ck):.3f} = {ana.c:.3f} mm")
        sec3.append(f"   \u03b5y = fy / Es = {ana.f_y:.1f} / {ana.E_s:.0f} = {ana.epsilon_y:.5f}")
        sec3.append(f"   \u03b5t = 0.00300 \u00d7 (dt - c) / c = 0.00300 \u00d7 ({ana.dt:.3f} - {ana.c:.3f}) / {ana.c:.3f} = {ana.epsilon_t:.5f}")
        compare_op = "\u2265" if ana.epsilon_t >= 0.005 else "<"
        sec3.append(f"   \u03b5t {compare_op} 0.0050 이므로 {ana.epsilon_t_result}이며, \u03a6 = {ana.pi_f_r:.2f} 를 적용한다")

        sec4 = []
        sec4.append("4) 필요철근량 산정")
        sec4.append("   Mu / \u03a6f = As \u00d7 fy \u00d7 (d - a / 2)              ---------------- \u2460")
        sec4.append("   a = As \u00d7 fy / (0.85 \u00d7 fck \u00d7 b)               ---------------- \u2461")
        sec4.append("   식\u2461를 식\u2460에 대입하여 이차방정식으로 As를 구한다")
        sec4.append("           fy\u00b2                                Mu")
        sec4.append(f"   ------------------ As\u00b2 - fy \u00d7 d \u00d7 As + ------ = 0 ,  Asreq = {ana.as_req:.1f} mm\u00b2")
        sec4.append(f"    2 \u00d7 0.85 \u00d7 fck \u00d7 b                         \u03a6f")

        sec5 = []
        usage_ratio = ana.as_use / ana.as_req if ana.as_req > 0 else 0
        sec5.append(f"5) 사용철근량 : Asuse = {ana.as_use:.1f} mm\u00b2, 철근도심 : dc_avg = {ana.d_c:.1f} mm, [ 사용율 = {usage_ratio:.3f} ]")
        sec5.append(f"   1단 : D {ana.as_dia1} - {ana.as_num1} EA (= {ana.as_use1:.1f} mm\u00b2, dc1 = {ana.dc_1:.1f} mm)")
        if ana.as_num2 > 0:
            sec5.append(f"   2단 : D {ana.as_dia2} - {ana.as_num2} EA (= {ana.as_use2:.1f} mm\u00b2, dc2 = {ana.dc_2:.1f} mm)")
        if ana.as_num3 > 0:
            sec5.append(f"   3단 : D {ana.as_dia3} - {ana.as_num3} EA (= {ana.as_use3:.1f} mm\u00b2, dc3 = {ana.dc_3:.1f} mm)")

        sec6 = []
        sec6.append("6) 철근비 검토")
        sec6.append(f"   \u03c1min : 1.4 / fy          = {ana.lo_min_1:.6f}")
        sec6.append(f"          0.25 \u00d7 \u221afck / fy  = {ana.lo_min_2:.6f}, \u03c1min = {ana.lo_min:.6f} 적용")
        sec6.append(f"   \u03c1max = 0.75 \u00d7 \u03c1b = {ana.lo_max:.6f}")
        sec6.append(f"   \u03c1use = As / ( b \u00d7 d ) = {ana.lo_use:.6f}")
        
        check_msg = ""
        if ana.lo_use >= ana.lo_min:
            if ana.lo_use <= ana.lo_max:
                check_msg = "\u03c1max \u2265 \u03c1use \u2265 \u03c1min --> 최소철근비, 최대철근비 만족   \u2234 O.K"
            else:
                check_msg = "\u03c1max < \u03c1use \u2265 \u03c1min --> 최소철근비 만족, 최대철근비 불만족   \u2234 N.G"
        else:
            if ana.lo_use >= ana.lo_min_3:
                check_msg = f"\u03c1use < \u03c1min 이나, \u03c1use \u2265 4/3 \u00d7 \u03c1req ({ana.lo_min_3:.6f}) 만족   \u2234 O.K"
            else:
                check_msg = f"\u03c1use < \u03c1min 이며, \u03c1use < 4/3 \u00d7 \u03c1req ({ana.lo_min_3:.6f}) 불만족   \u2234 N.G"
        sec6.append(f"   {check_msg}")

        sec7 = []
        sec7.append("7) 설계 휨강도 산정")
        sec7.append(f"   a = As \u00d7 fy / (0.85 \u00d7 fck \u00d7 b) = {ana.a:.3f} mm")
        sec7.append(f"   \u03a6 Mn = \u03a6f \u00d7 As \u00d7 fy \u00d7 (d - a / 2)")
        sec7.append(f"        = {ana.pi_f_r:.2f} \u00d7 {ana.as_use:.1f} \u00d7 {ana.f_yd} \u00d7 ({ana.d_eff:.1f} - {ana.a:.3f} / 2)")
        res_f = "O.K" if ana.M_r >= ana.Mu_nm else "N.G"
        sf = ana.M_sf
        sec7.append(f"        = {ana.M_r/1e6:.1f} kN.m \u2500\u2500\u2500> {res_f} (Mu = {ana.Mu:.1f} kN.m) [S.F = {sf:.3f}]")

        flex_all = []
        flex_all.extend(header)
        flex_all.extend(sec1); flex_all.append("")
        flex_all.extend(sec2); flex_all.append("")
        flex_all.extend(sec3); flex_all.append("")
        flex_all.extend(sec4); flex_all.append("")
        flex_all.extend(sec5); flex_all.append("")
        flex_all.extend(sec6); flex_all.append("")
        flex_all.extend(sec7)

        shear = []
        shear.append("10) 전단검토")
        shear.append(f"   \u03a6 Vc = \u03a6v \u00d7 \u221afck \u00d7 b \u00d7 d / 6")
        shear.append(f"      = {ana.pi_v:.2f} \u00d7 \u221a{ana.f_ck:.1f} \u00d7 {ana.beam_b:.1f} \u00d7 {ana.d_eff:.1f} / 6 = {ana.pi_V_c/1e3:.1f} kN")
        if ana.pi_V_c >= ana.Vu_n:
            shear.append(f"   \u03a6 Vc \u2265 Vu = {ana.Vu:.1f} kN  \u2234 전단보강 불필요")
        else:
            shear.append(f"   \u03a6 Vc < Vu = {ana.Vu:.1f} kN  \u2234 전단보강 필요")
            shear.append(f"   Vs_req = (Vu - \u03a6Vc) / \u03a6v = {(ana.Vu_n - ana.pi_V_c)/ana.pi_v/1e3:.1f} kN")
            shear.append(f"   Av_use = {ana.av_use:.1f} mm\u00b2 (D{ana.av_dia}-{ana.av_leg:.0f}EA, CTC {ana.av_space:.0f})")
            shear.append(f"   Vs_use = Av \u00d7 fy \u00d7 d / s = {ana.V_s/1e3:.1f} kN")
            res_v = "O.K" if (ana.pi_V_c + ana.pi_v * ana.V_s) >= ana.Vu_n else "N.G"
            shear.append(f"   \u03a6(Vc + Vs) = {(ana.pi_V_c + ana.pi_v * ana.V_s)/1e3:.1f} kN \u2234 {res_v}")

        service = []
        service.append("11) 균열검토")
        service.append(f"    Sa = {ana.s_min:.3f} mm  \u2265 suse = {ana.s_use:.3f} mm  \u2234 {ana.crack_status}")

        total = []
        total.extend(flex_all); total.append(""); total.extend(shear); total.append(""); total.extend(service)
        return {"total": "\n".join(total), "flexure": "\n".join(flex_all), "shear": "\n".join(shear), "service": "\n".join(service)}

    def _generate_lsd_report(self):
        # Image-based LSD Report Template (Page 1 & 2)
        ana = self.analyzer
        con = ana.con_material
        
        header = []
        header.append("=" * 75)
        header.append(f"{self.std.name:^75}")
        header.append(f"{'한계상태설계법(LSD) 단면 검토 보고서':^75}")
        header.append("=" * 75)
        header.append("")

        # * Section property
        sec_prop = []
        sec_prop.append("* Section property")
        l1 = f"fck = {ana.f_ck:>5.1f} MPa, fy = {ana.f_y:>5.1f} MPa, \u03a6c = {ana.phi_c:>5.2f}, \u03a6s = {ana.phi_s:>5.2f}, Es = {ana.E_s:>7.0f} MPa"
        sec_prop.append(l1)
        sec_prop.append("-" * 95)
        sec_prop.append(f"| {'b(mm)':^8} | {'H(mm)':^8} | {'d(mm)':^8} | {'피복(mm)':^8} | {'Mu(kN.m)':^10} | {'Vu(kN)':^10} | {'Muy(kN.m)':^10} |")
        sec_prop.append("-" * 95)
        # Assuming Muy column in image is same as Mu if not provided
        muy_val = ana.Mu
        sec_prop.append(f"| {ana.beam_b:^8.1f} | {ana.beam_h:^8.1f} | {ana.d_eff:^8.1f} | {ana.d_c:^8.1f} | {ana.Mu:^10.3f} | {ana.Vu:^10.3f} | {muy_val:^10.3f} |")
        sec_prop.append("-" * 95)
        sec_prop.append("")

        # * 콘크리트 재료상수
        con_mat = []
        con_mat.append("* 콘크리트 재료상수")
        con_mat.append(f"  n      : 상승 곡선부의 형상을 나타내는 지수         = {con.n_eps:>8.2f}")
        con_mat.append(f"  \u03b5co,r  : 최대응력에 처음 도달했을때의 변형률       = {con.eps_co:>8.4f}")
        con_mat.append(f"  \u03b5cu,r  : 극한변형률                               = {con.eps_cu:>8.4f}")
        con_mat.append(f"  \u03b1cc    : 유효계수                                   = {ana.alpha_cc:>8.2f}")
        con_mat.append(f"  fcd    : 콘크리트 설계압축강도 ( fck \u00d7 \u03a6c \u00d7 \u03b1cc )    = {ana.f_cd:>8.3f} MPa")
        con_mat.append(f"  fcm    : 평균압축강도 ( fck + \u0394f )                = {con.f_cm:>8.1f} MPa")
        con_mat.append(f"  Ec = 0.077 mc^1.5 \u221bfcm                          = {con.E_c:>8.1f} MPa")
        con_mat.append(f"  \u03b1      : 압축합력의 평균 응력계수                   = {ana.alpha_fac:>8.2f}")
        con_mat.append(f"  \u03b2      : 압축합력의 작용점 위치계수                 = {ana.beta_fac:>8.2f}")
        eta_val = ana.alpha_fac / con.alpha_cc
        con_mat.append(f"  \u03b7      : 등가 사각형 응력 블록의 크기계수           = {eta_val:>8.2f}")
        con_mat.append(f"  \u03b21     : 등가 사각형 응력 블록의 깊이계수 ( 2\u03b2 )   = {ana.beta_fac*2:>8.2f}")
        con_mat.append("")

        # * 철근 재료상수
        reb_mat = []
        reb_mat.append("* 철근 재료상수")
        reb_mat.append(f"  fyd    : 설계인장강도 ( \u03a6s fy )                    = {ana.f_yd:>8.1f} MPa")
        reb_mat.append(f"  \u03b5yd    : 설계 항복 변형률 ( fyd / Es )             = {ana.f_yd/ana.E_s:>8.5f}")
        reb_mat.append("")

        # * Requirement As
        req_as = []
        req_as.append("* Requirement As")
        req_as.append("  Mu = As \u00d7 fyd \u00d7 ( d - a/2 )              ---------------- ①")
        req_as.append(f"  a = As \u00d7 fyd / ( {eta_val:.2f} \u00d7 fcd \u00d7 b )             ---------------- ②")
        req_as.append("  substitution ② \u2192 ① : solve an equation (As)")
        req_as.append(f"  Asreq = {ana.as_req:>8.1f} mm\u00b2")
        req_as.append("")

        # * Used As
        used_as = []
        sf_m = ana.M_sf
        used_as.append(f"* Used As = {ana.as_use:>8.1f} mm\u00b2 (reinforcement center : {ana.d_c:>8.1f} mm), [S.F = {sf_m:>6.3f} ]")
        used_as.append(f"  1단 : H {ana.as_dia1:>2} - {ana.as_num1:>3.0f} EA,  Cover = {ana.dc_1:>8.1f} mm, ( {ana.as_use1:>8.1f} mm\u00b2 )")
        if ana.as_num2 > 0:
            used_as.append(f"  2단 : H {ana.as_dia2:>2} - {ana.as_num2:>3.0f} EA,  Cover = {ana.dc_2:>8.1f} mm, ( {ana.as_use2:>8.1f} mm\u00b2 )")
        used_as.append("")

        # * Reinforcement Check
        rebar_check = []
        rebar_check.append("* Reinforcement Check")
        as_min_val = min(ana.lo_min * ana.beam_b * ana.d_eff, ana.as_req * 4/3)
        as_max_val = 0.04 * ana.beam_b * ana.beam_h # Conventional 4% of gross section
        ok_min = "O.K" if ana.as_use >= as_min_val else "N.G"
        ok_max = "O.K" if ana.as_use <= as_max_val else "N.G"
        
        rebar_check.append(f"  As_max ({as_max_val:.1f}) \u2265 As_use ({ana.as_use:.1f}) \u2265 As_min ({as_min_val:.1f})")
        rebar_check.append(f"  Max Reinforcement ratio - {ok_max} , Min Reinforcement ratio - {ok_min}")
        
        # Rebar spacing check
        rebar_check.append(f"  \ucca0\uadfc \uac04\uaca9\uac80\ud1a0: s_max = min( 2h, 250 ) = {ana.s_detailing_max:.0f} \u2265 s = {ana.s_use:.0f} mm  {ana.s_detailing_ok} ( \ub3c4.\uc124.\uae30 5.12.3.1 )")
        rebar_check.append("")

        # * Moment check
        mom = []
        mom.append("* Moment check")
        mom.append(f"  T = As \u00d7 fyd = {ana.as_use:>8.1f} \u00d7 {ana.f_yd:>8.1f} = {ana.tension_force:>10.0f} N")
        mom.append(f"  C = n \u00d7 fcd \u00d7 a \u00d7 b = {eta_val:.2f} \u00d7 {ana.f_cd:.3f} \u00d7 a \u00d7 {ana.beam_b:.1f} = {eta_val*ana.f_cd*ana.beam_b:>10.1f} \u00d7 a")
        mom.append(f"  a = As \u00d7 fyd / ( {eta_val:.2f} \u00d7 fcd \u00d7 b ) = {ana.a:>8.3f} mm")
        mom.append(f"  c = a / {ana.beta_fac*2:.3f} = {ana.c:>8.3f} mm")
        mom.append(f"  Mr = {ana.M_r/1e6:>8.3f} kN.m (Mu = {ana.Mu:>8.3f} kN.m)  --> {'O.K' if ana.M_r >= ana.Mu_nm else 'N.G'}")
        mom.append("")

        # Page 2: Shear
        shr = []
        shr.append("* Shear force check (d = {0:.1f} mm)".format(ana.d_eff))
        shr.append(f"  Vcd = {ana.pi_V_c/1e3:>8.2f} kN, Vu = {ana.Vu:>8.2f} kN")
        shr.append(f"  {'전단보강 불필요' if ana.pi_V_c >= ana.Vu_n else '전단보강 필요 !!'}")
        shr.append("")
        
        add_reb = []
        # Stirrup check details if needed
        if ana.pi_V_c < ana.Vu_n:
            shr.append("* 전단철근량 검토")
            shr.append("  Vsd = (\u03a6s \u00d7 fyv \u00d7 Av \u00d7 z / s) \u00d7 cot\u03b8")
            z_val = 0.9 * ana.d_eff
            shr.append(f"  z : 단면 내부 팔길이 (0.9 d)               = {z_val:>8.2f} mm")
            if hasattr(ana, 'v_theta'):
                shr.append(f"  \u03b8 : 복부 압축스트럿의 각도                       = {ana.v_theta:>8.2f} \u00b0")
                shr.append(f"  cot\u03b8 = {ana.v_cot_theta:>8.3f}")
            
            av_use = ana.rebar.get_area(ana.av_dia) * ana.av_leg
            shr.append(f"  Av_use  = {av_use:>8.1f} mm\u00b2 ({ana.av_dia} - {ana.av_leg:.0f} EA, C.T.C {ana.av_space:.0f} mm)")
            shr.append(f"  Vsd = {ana.V_s/1e3:>8.2f} kN")
            shr.append(f"  Vd_Max = {ana.V_s_max/1e3:>8.2f} kN")
            res_v = "O.K" if (ana.pi_V_c + ana.V_s) >= ana.Vu_n else "N.G"
            shr.append(f"  Vd = Vcd + Vsd = {(ana.pi_V_c + ana.V_s)/1e3:>8.2f} kN  \u2234 {res_v}")
            shr.append("")

            # * 종방향 철근의 추가인장력 검토
            add_reb.append("* 종방향 철근의 추가인장력 검토")
            add_reb.append(f"  \u0394T = 0.5 \u00d7 Vu \u00d7 cot\u03b8 = {ana.delta_t/1000:>8.2f} kN")
            add_reb.append(f"  \u0394TB = (Mr - Mu) / z = {ana.delta_tb/1000:>8.2f} kN")
            res_t = "O.K" if (ana.delta_t <= ana.delta_tb) or (ana.delta_t <= 0) else "N.G"
            add_reb.append(f"  \u0394T {'\u2264' if res_t=='O.K' else '>'} \u0394TB  \u2234 {res_t}")

        total = []
        total.extend(header)
        total.extend(sec_prop)
        total.extend(con_mat)
        total.extend(reb_mat)
        total.extend(req_as)
        total.extend(used_as)
        total.extend(rebar_check)
        total.extend(mom)
        total.extend(shr)
        total.extend(add_reb)

        return {
            "total": "\n".join(total),
            "flexure": "\n".join(total[:80]),
            "shear": "\n".join(shr + add_reb),
            "service": "See total report for LSD details"
        }
