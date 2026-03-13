from .base_standard import BaseDesignStandard

class LSD2015(BaseDesignStandard):
    @property
    def name(self):
        return "한계상태설계법(도로교 설계기준, 2015)"

    def get_phi_f(self, epsilon_t, epsilon_y):
        # LSD uses Material Factor (gamma) instead of Phi, 
        # but for compatibility with current structure, we return 1.0 or equivalent.
        return 1.0, "한계상태검토"

    def get_phi_v(self):
        return 1.0

    def get_concrete_method(self):
        return "LSD"

    def get_material_factors(self):
        return 0.65, 0.90

    def get_alpha_cc(self):
        return 0.85

    def get_flexure_factors(self, f_ck):
        # KDS 14 20 24 : 4.2.1.3 (3) - Equiv. Rectangular Stress Block
        if f_ck <= 50:
            eta = 1.0
            lambda_fac = 0.8
        else:
            eta = 1.0 - (f_ck - 50) / 200
            lambda_fac = 0.8 - (f_ck - 50) / 400
            
        eta = max(0.67, eta)
        lambda_fac = max(0.65, lambda_fac)
        
        # In rectangular block: alpha = eta * lambda, beta = lambda / 2
        return eta * lambda_fac, lambda_fac / 2

    def get_beta_1(self, f_ck):
        return super().get_beta_1(f_ck)

    def get_k_cr(self, crack_case):
        return super().get_k_cr(crack_case)

    def calc_shear_capacity(self, analyzer):
        """LSD 2015 전단 강도 계산 (LSD 2012와 유사한 트러스 모델 기반)"""
        import math
        f_ck = analyzer.f_ck
        f_cd = analyzer.f_cd
        phi_s = analyzer.phi_s
        f_y = analyzer.f_y
        B = analyzer.beam_b
        D = analyzer.d_tensile
        Vu_n = analyzer.Vu_n
        
        z = 0.9 * D
        nu = 0.6 * (1 - f_ck / 250)
        phi_c = analyzer.phi_c
        
        # Section checking (Vdmax)
        cot81 = 2.5; tan81 = 1/cot81
        Vdmax1 = (nu * phi_c * f_ck * B * z) / (cot81 + tan81) if (cot81 + tan81) > 0 else 0
        
        cot82 = 1.0; tan82 = 1/cot82
        Vdmax2 = (nu * phi_c * f_ck * B * z) / (cot82 + tan82) if (cot82 + tan82) > 0 else 0
        
        if Vu_n <= Vdmax1:
            cot_theta = 2.5
        elif Vu_n > Vdmax2:
            cot_theta = 1.0
        else:
            asin_divisor = (nu * phi_c * f_ck * B * z)
            val_to_asin = Vu_n / asin_divisor if asin_divisor > 0 else 0
            if abs(val_to_asin) <= 1.0:
                theta_rad = 0.5 * math.asin(val_to_asin)
                tan_theta = math.tan(theta_rad)
                cot_theta = 1 / tan_theta if tan_theta != 0 else 2.5
                cot_theta = max(1.0, min(2.5, cot_theta))
            else:
                cot_theta = 1.0
        
        # Concrete capacity (Vc)
        k = 1 + math.sqrt(200 / D) if D > 0 else 2.0
        k = min(k, 2.0)
        rho_l = analyzer.rho_l_tensile
        rho_l_limited = min(rho_l, 0.02)
        
        Ac = B * analyzer.beam_h
        fn = analyzer.Nu * 1e3 / Ac if Ac > 0 else 0
        fn_limited = min(fn, 0.2 * phi_c * f_ck)
        f_ctk = analyzer.con_material.f_ctk
        
        Vcd_calc = (0.85 * phi_c * k * (rho_l_limited * f_ck)**(1/3) + 0.15 * fn_limited) * (B * D)
        Vcd_min = (0.4 * phi_c * f_ctk + 0.15 * fn_limited) * (B * D)
        V_c = max(Vcd_calc, Vcd_min)
        
        # Stirrup capacity
        av_use = analyzer.rebar.get_area(analyzer.av_dia) * analyzer.av_leg
        V_s = (phi_s * f_y * av_use * z / analyzer.av_space) * cot_theta if analyzer.av_space > 0 else 0
        
        delta_t = 0.5 * Vu_n * cot_theta
        delta_tb = (analyzer.M_r - analyzer.Mu_nm) / z if z > 0 else 0

        return {
            "V_c": V_c,
            "V_s": V_s,
            "V_n": V_c + V_s,
            "V_max": Vdmax2,
            "theta": math.degrees(math.atan(1/cot_theta)) if cot_theta > 0 else 90,
            "details": {
                "k": k, "rho_l": rho_l, "fn": fn, "f_ctk": f_ctk, "Ac": Ac,
                "Vcd_calc": Vcd_calc, "Vcd_min": Vcd_min,
                "nu": nu, "cot_theta": cot_theta, "z": z, "av_use": av_use,
                "Vdmax1": Vdmax1, "Vdmax2": Vdmax2,
                "delta_t": delta_t, "delta_tb": delta_tb,
                "cot_alpha": 0, "alpha_deg": 90.0,
                "s_max_1": 0.75 * D,
                "s_max_2": min(0.75 * D, 600)
            }
        }
