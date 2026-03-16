"""
lsd_text_builder.py
한계상태설계법(LSD, 도로교 설계기준 등) 전용 텍스트 보고서 빌더.
"""
import math


class LSDTextBuilder:
    """한계상태설계법(LSD) 전용 텍스트 보고서 빌더."""

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.std = analyzer.standard

    def generate(self):
        try:
            return self._build_report()
        except Exception as e:
            import traceback
            err_msg = f"보고서 생성 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
            return {"total": err_msg, "flexure": err_msg, "shear": err_msg, "service": err_msg}

    def _build_report(self):
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
        sec_prop.append("1) 단면제원 및 설계가정")
        l1 = f"fck = {ana.f_ck:>5.1f} MPa, fy = {ana.f_y:>5.1f} MPa, \u03a6c = {ana.phi_c:>5.2f}, \u03a6s = {ana.phi_s:>5.2f}, Es = {ana.E_s:>7.0f} MPa"
        sec_prop.append(l1)
        sec_prop.append("-" * 95)
        sec_prop.append(f"| {'b(mm)':^8} | {'H(mm)':^8} | {'d(mm)':^8} | {'피복(mm)':^8} | {'Mu(kN.m)':^10} | {'Vu(kN)':^10} | {'Muy(kN.m)':^10} |")
        sec_prop.append("-" * 95)
        muy_val = ana.Mu
        sec_prop.append(f"| {ana.beam_b:^8.1f} | {ana.beam_h:^8.1f} | {ana.d_eff:^8.1f} | {ana.d_c:^8.1f} | {ana.Mu:^10.3f} | {ana.Vu:^10.3f} | {muy_val:^10.3f} |")
        sec_prop.append("-" * 95)
        sec_prop.append("")

        # * 콘크리트 재료상수 (Image Sync)
        con_mat = []
        con_mat.append("2) 콘크리트 재료상수")
        eta_val = ana.alpha_fac / con.alpha_cc
        # Fixed alignment to match user image exactly. Uses Cyrillic 'Ф' as seen in image.
        con_mat.append(f"  n      : 상승 곡선부의 형상을 나타내는 지수             = {con.n_eps:>10.2f}")
        con_mat.append(f"  \u03b5co,r  : 최대응력에 처음 도달했을때의 변형률           = {con.eps_co:>10.4f}")
        con_mat.append(f"  \u03b5cu,r  : 극한변형률                                   = {con.eps_cu:>10.4f}")
        con_mat.append(f"  \u03b1cc    : 유효계수                                     = {ana.alpha_cc:>10.2f}")
        con_mat.append(f"  fcd    : 콘크리트 설계압축강도 ( fck \u00d7 \u0424c \u00d7 \u03b1cc )     = {ana.f_cd:>10.3f} MPa")
        con_mat.append(f"  fcm    : 평균압축강도 ( fck + \u0394f )                    = {con.f_cm:>10.1f} MPa")
        con_mat.append(f"  Ec = 0.077 mc^1.5 \u221bfcm                              = {con.E_c:>10.1f} MPa")
        con_mat.append(f"  \u03b1      : 압축합력의 평균 응력계수                     = {ana.alpha_fac:>10.2f}")
        con_mat.append(f"  \u03b2      : 압축합력의 작용점 위치계수                   = {ana.beta_fac:>10.2f}")
        con_mat.append(f"  \u03b7      : 등가 사각형 응력 블록의 크기계수               = {eta_val:>10.2f}")
        con_mat.append(f"  \u03b21     : 등가 사각형 응력 블록의 깊이계수 ( 2\u03b2 )       = {ana.beta_fac*2:>10.2f}")
        con_mat.append("")

        # * 철근 재료상수
        reb_mat = []
        reb_mat.append("3) 철근 재료상수")
        reb_mat.append(f"  fyd    : 설계인장강도 ( \u03a6s fy )                    = {ana.f_yd:>8.1f} MPa")
        reb_mat.append(f"  \u03b5yd    : 설계 항복 변형률 ( fyd / Es )             = {ana.f_yd/ana.E_s:>8.5f}")
        reb_mat.append("")

        # * Requirement As
        req_as = []
        req_as.append("4) 필요철근량 산정")
        req_as.append("  Mu = As \u00d7 fyd \u00d7 ( d - a/2 )              ---------------- \u2460")
        req_as.append(f"  a = As \u00d7 fyd / ( {eta_val:.2f} \u00d7 fcd \u00d7 b )             ---------------- \u2461")
        req_as.append("  substitution \u2461 \u2192 \u2460 : solve an equation (As)")
        req_as.append(f"  Asreq = {ana.as_req:>8.1f} mm\u00b2")
        req_as.append("")

        # * Used As
        used_as = []
        usage_ratio = ana.as_use / ana.as_req if ana.as_req > 0 else 9.99
        used_as.append(f"* Used As = {ana.as_use:>8.1f} mm\u00b2 (reinforcement center : {ana.d_c:>8.1f} mm), [ 사용율 = {usage_ratio:>6.3f} ]")
        used_as.append(f"  1단 : H {ana.as_dia1:>2} - {ana.as_num1:>3.0f} EA,  Cover = {ana.dc_1:>8.1f} mm, ( {ana.as_use1:>8.1f} mm\u00b2 )")
        if ana.as_num2 > 0:
            used_as.append(f"  2단 : H {ana.as_dia2:>2} - {ana.as_num2:>3.0f} EA,  Cover = {ana.dc_2:>8.1f} mm, ( {ana.as_use2:>8.1f} mm\u00b2 )")
        used_as.append("")

        # * Reinforcement Check
        rebar_check = []
        rebar_check.append("5) 철근비 검토")
        ok_min = "O.K" if ana.as_use >= ana.as_min_val else "N.G"
        ok_max = "O.K" if ana.as_use <= ana.as_max_val else "N.G"
        ok_shrink = "O.K" if ana.as_use >= ana.as_shrink else "N.G"

        rebar_check.append(f"  \u03c1min : 1.4 \u00d7 bw \u00d7 d / fy          = {ana.as_min_1:>8.1f} mm\u00b2")
        rebar_check.append(f"         0.25 \u221afck \u00d7 bw \u00d7 d / fy  = {ana.as_min_2:>8.1f} mm\u00b2 , As_min = {ana.as_min_val:>8.1f} mm\u00b2")
        rebar_check.append(f"         4 / 3 \u00d7 Asreq            = {ana.as_min_3:>8.1f} mm\u00b2")
        rebar_check.append(f"  Shrinkable reinforcemenet       = {ana.as_shrink:>8.1f} mm\u00b2    Shrinkage Reinforcement - {ok_shrink} !!")
        rebar_check.append(f"  As_max = 0.04 \u00d7 b \u00d7 d           = {ana.as_max_val:>8.1f} mm\u00b2")
        rebar_check.append(f"  As_max ({ana.as_max_val:.1f}) \u2265 As_use ({ana.as_use:.1f}) \u2265 As_min ({ana.as_min_val:.1f})")
        rebar_check.append(f"  Max Reinforcement ratio - {ok_max} , Min Reinforcement ratio - {ok_min}")
        rebar_check.append(f"  철근 간격검토: s_max = min( 2h, 250 ) = {ana.s_detailing_max:.0f} \u2265 s = {ana.s_use:.0f} mm  {ana.s_detailing_ok} ( 도.설.기 5.12.3.1 )")
        rebar_check.append("")

        # * Moment check
        mom = []
        mom.append("6) 설계 휨강도 산정")
        mom.append(f"  T = As \u00d7 fyd = {ana.as_use:>8.1f} \u00d7 {ana.f_yd:>8.1f} = {ana.tension_force:>10.0f}")
        mom.append(f"  C = \u03b7 \u00d7 fcd \u00d7 a \u00d7 b = {eta_val:.2f} \u00d7 {ana.f_cd:.3f} \u00d7 a \u00d7 {ana.beam_b:.1f} = {eta_val*ana.f_cd*ana.beam_b:>10.1f} \u00d7 a")
        mom.append(f"  a = As \u00d7 fyd / ( \u03b7 \u00d7 fcd \u00d7 b ) = {ana.a:>8.3f} mm")
        mom.append(f"  중립축 깊이 c = a / \u03b21 = {ana.a:>8.1f} / {ana.beta_fac*2:.3f} = {ana.c:>8.1f} mm")
        
        c_max_formula = f"( \u03b4 \u00d7 \u03b5cu / 0.0033 - 0.600 ) \u00d7 d"
        c_max_calc = f"( {ana.delta_redist:.1f} \u00d7 {ana.eps_cu:.4f} / 0.0033 - 0.600 ) \u00d7 {ana.d_eff:.1f}"
        ok_cmax = "O.K !!" if ana.c_max >= ana.c else "N.G !!"
        mom.append(f"  최대 중립축 깊이 c_max = {c_max_formula} , 여기서 \u03b4 = {ana.delta_redist:.1f} (모멘트 재분배 계수)")
        mom.append(f"                     = {c_max_calc}")
        mom.append(f"                     = {ana.c_max:>8.1f} mm \u2265 c = {ana.c:>8.1f} mm      {ok_cmax}")
        
        eps_s_calc = f"{ana.eps_cu:.4f} \u00d7 ( {ana.d_eff:.1f} - {ana.c:.1f} ) / {ana.c:.1f}"
        ok_yield = "O.K !!" if ana.eps_s >= ana.eps_yd else "N.G !!"
        mom.append(f"  인장철근 변형률 \u03b5s = \u03b5cu \u00d7 ( d - c ) / c  = {eps_s_calc}")
        mom.append(f"                   = {ana.eps_s:>8.4f}  \u2265 \u03b5yd = {ana.eps_yd:>8.4f}   철근항복 가정 {ok_yield}")
        mom.append("")
        
        res_m = "O.K" if ana.M_r >= ana.Mu_nm else "N.G"
        mom.append(f"  Mr = {ana.as_use:>8.1f} \u00d7 {ana.f_yd:.0f} \u00d7 ( {ana.d_eff:^7.1f} - a / 2 ) = {ana.M_r/1e6:>8.2f} kN.m")
        mom.append(f"     \u2265 Mu ( = {ana.Mu:>8.3f} kN.m)  \u2234 {res_m}   [ S.F = {ana.M_sf:>8.3f} ]")
        mom.append("")

        # Shear
        shr = []
        vd = ana.v_details
        shr.append("7) 전단검토 (d = {0:>10.1f} mm)".format(ana.d_eff))
        
        vcd_formula = "( 0.85 \u00d7 \u03a6c \u00d7 \u03ba \u00d7 (\u03c1 \u00d7 fck)^1/3 + 0.15 \u00d7 fn ) \u00d7 bw \u00d7 d"
        vcd_calc = f"( 0.85 \u00d7 {ana.phi_c:.1f} \u00d7 {vd.get('k',0):.3f} \u00d7 ( {vd.get('rho_l',0):.4f} \u00d7 {ana.f_ck:.0f} )^1/3 + 0.15 \u00d7 {vd.get('fn',0):.2f} )"
        shr.append(f"  Vcd = {vcd_formula}")
        shr.append(f"      = {vcd_calc}")
        shr.append(f"        \u00d7 {ana.beam_b:.1f} \u00d7 {ana.d_eff:.1f} = {vd.get('Vcd_calc',0)/1e3:>8.1f} kN")
        
        vcd_min_formula = "( 0.4 \u00d7 \u03a6c \u00d7 fctk + 0.15 \u00d7 fn ) \u00d7 bw \u00d7 d"
        vcd_min_calc = f"( 0.4 \u00d7 {ana.phi_c:.1f} \u00d7 {vd.get('f_ctk',0):.3f} + 0.15 \u00d7 {vd.get('fn',0):.2f} ) \u00d7 {ana.beam_b:.1f} \u00d7 {ana.d_eff:.1f}"
        shr.append(f"  Vcd,min = {vcd_min_formula}")
        shr.append(f"          = {vcd_min_calc}")
        shr.append(f"          = {vd.get('Vcd_min',0)/1e3:>8.1f} kN")
        
        res_vcd = "Vcd < Vcd,min 이므로," if vd.get('Vcd_calc',0) < vd.get('Vcd_min',0) else "Vcd \u2265 Vcd,min 이므로,"
        reinf_needed = " - 전단보강 필요 !!" if ana.pi_V_c < ana.Vu_n else " - 전단보강 불필요"
        shr.append(f"     {res_vcd}")
        shr.append(f"  \u2234 Vcd = {ana.pi_V_c/1e3:>8.1f} kN  <  Vu = {ana.Vu:>8.1f} kN     : {reinf_needed}")
        
        shr.append(f"     fctk : 콘크리트 인장강도 (0.7 fctm)         = {vd.get('f_ctk',0):>8.3f} MPa")
        shr.append(f"     \u03ba    : 1 + \u221a( 200 / d ) \u2264 2.0                 = {vd.get('k',0):>8.3f}")
        shr.append(f"     As   : 전체 종방향 철근량                       = {ana.as_use:>8.1f} mm\u00b2")
        shr.append(f"     \u03c1    : 철근비 As / ( bw \u00d7 d ) \u2264 0.02           = {vd.get('rho_l',0):>8.4f}")
        shr.append(f"     d    : 유효깊이                                 = {ana.d_eff:>8.1f} mm")
        shr.append(f"     Nu   : 축방향력                                 = {ana.Nu:>8.3f} kN  (축방향력, 압축 + )")
        shr.append(f"     Ac   : 콘크리트 단면적 (bw \u00d7 h)                = {vd.get('Ac', ana.beam_b * ana.beam_h):>8.1f} mm\u00b2")
        shr.append(f"     fn   : Nu / Ac \u2264 0.2 \u03a6c fck                     = {vd.get('fn',0):>8.3f} MPa")
        shr.append("")

        add_reb = []
        if ana.pi_V_c < ana.Vu_n:
            shr.append("* 전단철근량 검토")
            vsd_formula = "\u03a6s \u00d7 fvy \u00d7 Av \u00d7 z / s \u00d7 cot\u03b8"
            vd_max_formula = "\u03bd \u00d7 \u03a6c \u00d7 fck \u00d7 bw \u00d7 z / (cot\u03b8 + tan\u03b8)"
            shr.append(f"  Vsd = {vsd_formula:^25} < Vd,max = {vd_max_formula}")
            shr.append("")
            shr.append(f"     z    : 단면 내부 팔길이 (0.9 d)               = {vd.get('z',0):>8.2f} mm")
            shr.append(f"     \u03bd    : 콘크리트 압축강도 유효계수 (0.6(1-fck/250)) = {vd.get('nu',0):>8.3f}")
            shr.append(f"     \u03b8    : 복부 압축스트럿의 각도               = {ana.v_theta:>8.2f} \u00b0")
            
            av_use = vd.get('av_use', ana.rebar.get_area(ana.av_dia) * ana.av_leg)
            shr.append(f"  Av_use = {av_use:>8.1f} mm\u00b2 ( H {ana.av_dia:>2} - {ana.av_leg:.0f} EA, C.T.C {ana.av_space:.0f} mm)")
            
            vsd_calc = f"{ana.phi_s:.1f} \u00d7 {ana.f_y:.0f} \u00d7 {av_use:.1f} \u00d7 {vd.get('z',0):.1f} \u00d7 {vd.get('cot_theta',0):.3f} / {ana.av_space:.0f}"
            shr.append(f"  Vsd  = {vsd_calc}")
            shr.append(f"       = {ana.V_s/1e3:>8.1f} kN")
            
            tan_theta = 1/vd.get('cot_theta',1) if vd.get('cot_theta',0) > 0 else 0
            vd_max_calc = f"{vd.get('nu',0):.3f} \u00d7 {ana.phi_c:.1f} \u00d7 {ana.f_ck:.0f} \u00d7 {ana.beam_b:.1f} \u00d7 {vd.get('z',0):.1f} / {vd.get('cot_theta',0)+tan_theta:.3f}"
            vd_max_val = vd.get('Vdmax2',0)
            shr.append(f"  Vd,Max = {vd_max_calc}")
            shr.append(f"         = {vd_max_val/1e3:>8.1f} kN \u2265 Vsd = {ana.V_s/1e3:>8.1f} kN      .. {'O.K' if vd_max_val >= ana.V_s else 'N.G'}")
            
            sin_alpha = math.sin(math.radians(vd.get('alpha_deg',90)))
            divisor = (ana.av_space * ana.beam_b * sin_alpha)
            rho_v = av_use / divisor if divisor > 0 else 0
            rho_v_min = (0.08 * math.sqrt(ana.f_ck)) / ana.f_y if ana.f_y > 0 else 0
            shr.append(f"  \u03c1v_use = Av_use / ( s \u00d7 bw \u00d7 sin \u03b1 )      = {rho_v:>8.6f}")
            shr.append(f"  \u03c1v_min = ( 0.08 \u00d7 \u221afck ) / fy      = {rho_v_min:>8.5f} { '<' if rho_v_min < rho_v else '>='} \u03c1v_use = {rho_v:>8.5f} .. { 'O.K' if rho_v >= rho_v_min else 'N.G'}")
            
            shr.append(f"     \u03b1    : 전단철근과 부재축과의 각도               = {vd.get('alpha_deg',90):>8.2f} \u00b0")
            s_ok = "O.K" if ana.av_space <= vd.get('s_max_1',0) else "N.G"
            shr.append(f"  Space Check : s = {ana.av_space:>8.0f} mm \u2264 s_max = 0.75 d ( 1 + cot \u03b1 ) = {vd.get('s_max_1',0):>8.0f} mm .. {s_ok}")
            
            v_total = (ana.pi_V_c + ana.V_s) / 1e3
            v_ok = "O.K" if v_total >= ana.Vu else "N.G"
            shr.append(f"  Vd = {ana.pi_V_c/1e3:.1f} + {ana.V_s/1e3:.1f} = {v_total:>8.1f} kN \u2265 {ana.Vu:.1f} kN .. {v_ok} [ S.F = {v_total/ana.Vu if ana.Vu>0 else 9.99:.3f} ]")
            shr.append("")

            add_reb.append("* 종방향 철근의 추가인장력 검토")
            dt_formula = "0.5 \u00d7 Vu \u00d7 ( cot\u03b8 - cot \u03b1 )"
            dt_calc = f"0.5 \u00d7 {ana.Vu:>8.3f} \u2215 ( {vd.get('cot_theta',0):.3f} - {vd.get('cot_alpha',0):.3f} )"
            add_reb.append(f"  \u0394T = {dt_formula} = {dt_calc} = {ana.delta_t/1e3:>8.3f} kN")
            
            dtb_formula = "( Mr - Mu ) / z"
            dtb_calc = f"( {ana.M_r/1e6:.3f} - {ana.Mu_nm/1e6:.3f} ) / {vd.get('z',0)/1000:.3f}"
            add_reb.append(f"  \u0394TB = {dtb_formula} = {dtb_calc} = {ana.delta_tb/1e3:>8.3f} kN")
            
            add_reb.append(f"     Mr : 전단력 검토단면의 휨강도                     = {ana.M_r/1e6:>8.3f} kN.m")
            add_reb.append(f"     MuV : 전단력 검토단면의 계수모멘트                 = {ana.Mu_nm/1e6:>8.3f} kN.m")
            
            t_ok = "O.K" if ana.delta_t <= ana.delta_tb else "N.G"
            comp_sym = "\u2264" if t_ok == "O.K" else ">"
            add_reb.append(f"  \u2234 \u0394T = {ana.delta_t/1e3:.2f} kN {comp_sym} \u0394TB = {ana.delta_tb/1e3:.2f} kN .. {t_ok}")

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

        # Serviceability (Crack)
        if hasattr(ana, 'service_details'):
            sd = ana.service_details
            srv = []
            srv.append("")
            #srv.append("-" * 80)
            srv.append("8) 균열 및 철근 간격 검토")
            #srv.append("-" * 80)
            
            # 1. Min Rebar
            srv.append("  \u2460 최소철근량 검토")
            as_min_formula = "kc \u00d7 k \u00d7 Act \u00d7 fct / fs"
            as_min_calc = f"{sd.get('kc',0.4):.2f} \u00d7 {sd.get('k_scale',1.0):.2f} \u00d7 {sd.get('Act',0):.0f} \u00d7 {sd.get('fctm',0):.2f} / {ana.f_y:.0f}"
            srv.append(f"     As_min = {as_min_formula}")
            srv.append(f"            = {as_min_calc} = {sd.get('as_min_lsd',0):>8.2f} mm\u00b2")
            
            srv.append(f"        kc  : 균열발생 직전의 단면 내 응력 분포 상태를 반영하는 계수 = {sd.get('kc',0.4):.2f}")
            srv.append(f"        k   : 부등 분포하는 응력의 영향을 반영하는 계수          = {sd.get('k_scale',1.0):.2f}")
            srv.append(f"        Act : 첫 균열발생 직전 상태의 콘크리트 인장영역 단면적    = {sd.get('Act',0):.0f} mm\u00b2")
            srv.append(f"        fct : 첫 균열 발생 시 유효 콘크리트 인장강도 (fctm)      = {sd.get('fctm',0):.2f} MPa")
            srv.append(f"        fs  : 허용하는 철근 인장강도 (fy)                        = {ana.f_y:.0f} MPa")
            
            status_min = "O.K" if ana.as_use >= sd.get('as_min_lsd', 0) else "N.G"
            srv.append(f"     As_use = {ana.as_use:>8.2f} mm\u00b2 > As_min = {sd.get('as_min_lsd',0):>8.2f} mm\u00b2    \u2234 {status_min}")
            srv.append("")
            
            # 2. Indirect Crack Control (Stress fs)
            srv.append("  \u2461 간접균열제어")
            srv.append(f"     사용 한계상태 모멘트 (Ms) = {sd.get('Ms_knm',0):>8.3f} kN.m")
            fs_formula = "Ms / ( As \u00d7 ( d - c / 3 ) )"
            fs_calc = f"{sd.get('Ms_knm',0)*1e3:.3f} / ( {ana.as_use:.1f} \u00d7 ( {ana.d_eff:.1f} - {sd.get('c_neutral',0):.1f} / 3 ) )"
            srv.append(f"     fs = {fs_formula}")
            srv.append(f"        = {fs_calc}")
            srv.append(f"        = {sd.get('fs',0):>8.3f} MPa \u2264 fsa = 0.8 \u00d7 fy = {sd.get('fsa',0):.1f} MPa    \u2234 {'O.K' if sd.get('fs',0) <= sd.get('fsa',0) else 'N.G'}")
            
            srv.append(f"        n   : 탄성계수비 (Es / Ec)                              = {sd.get('n',0):.2f}")
            srv.append(f"        \u03c1   : 철근비                                            = {sd.get('rho',0):.5f}")
            srv.append(f"        k   : 중립축 비                                         = {sd.get('k_neutral',0):.5f}")
            srv.append(f"        c   : 중립축 (kd)                                       = {sd.get('c_neutral',0):.1f} mm")
            srv.append("")
            
            # 3. Spacing check
            srv.append("  \u2462 철근 간격검토")
            sa_val = sd.get('sa_limit', 300.0)
            srv.append(f"     Sa = limit({sa_val:.1f}) = {sa_val:.1f} mm")
            s_use = ana.beam_b / ana.as_num1 if ana.as_num1 > 0 else 0
            srv.append(f"     S = {ana.beam_b:.0f} / {ana.as_num1:.1f} EA = {s_use:>8.1f} mm \u2264 Sa = {sa_val:.1f} mm    \u2234 {'O.K' if s_use <= sa_val else 'N.G'}")
            srv.append("")
            total.extend(srv)

        return {
            "total": "\n".join(total),
            "flexure": "\n".join(header + sec_prop + con_mat + reb_mat + req_as + used_as + rebar_check + mom),
            "shear": "\n".join(shr + add_reb),
            "service": "\n".join(srv) if hasattr(ana, 'service_details') else "사용성 검토 결과가 없습니다."
        }
