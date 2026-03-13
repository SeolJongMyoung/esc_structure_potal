import math
import numpy as np
from scipy import interpolate
from .base_standard import BaseDesignStandard

class LSD2012(BaseDesignStandard):
    """
    한계상태설계법 (도로교 설계기준, 2012)
    사용자 제공 Sec_back 로직 반영
    """
    def __init__(self):
        # Interpolation tables for alpha, beta, eta
        self.fck_list = [40, 50, 60, 70, 80, 90]
        self.alpha_list = [0.8, 0.78, 0.72, 0.67, 0.63, 0.59]
        self.beta_list = [0.4, 0.4, 0.38, 0.37, 0.36, 0.35]
        self.eta_list = [1.0, 0.97, 0.95, 0.91, 0.87, 0.84]

    @property
    def name(self):
        return "한계상태설계법(도로교 설계기준, 2012)"

    def get_concrete_method(self):
        return "LSD"

    def get_material_factors(self):
        # fcd = fck * phi_c * alpha_cc
        return 0.65, 0.90

    def get_alpha_cc(self):
        return 0.85

    def get_flexure_factors(self, f_ck):
        if f_ck <= 40:
            alpha = self.alpha_list[0]
            beta = self.beta_list[0]
        elif f_ck >= 90:
            alpha = self.alpha_list[5]
            beta = self.beta_list[5]
        else:
            f_alpha = interpolate.interp1d(self.fck_list, self.alpha_list)
            alpha = float(f_alpha(f_ck))
            f_beta = interpolate.interp1d(self.fck_list, self.beta_list)
            beta = float(f_beta(f_ck))
            
        return alpha, beta

    def get_phi_f(self, epsilon_t, epsilon_y):
        return 1.0, "한계상태(LSD)"

    def get_phi_v(self):
        return 1.0

    def calc_shear_capacity(self, analyzer):
        """가변각 트러스 모델 (LSD 2012)"""
        # (This will be called by RCSectionAnalyzer)
        f_ck = analyzer.f_ck
        f_cd = analyzer.f_cd
        phi_s = analyzer.phi_s
        f_y = analyzer.f_y
        B = analyzer.beam_b
        D = analyzer.d_tensile
        Vu_n = analyzer.Vu_n
        
        # Methodology from user's calshear
        # Methodology from user's calshear
        z = 0.9 * D
        nu = 0.6 * (1 - f_ck / 250)
        phi_c = analyzer.phi_c
        
        # Section checking (Vdmax)
        cot81 = 2.5
        tan81 = 1/cot81
        Vdmax_divisor = (cot81 + tan81)
        Vdmax1 = (nu * phi_c * f_ck * B * z) / Vdmax_divisor if Vdmax_divisor > 0 else 0
        
        cot82 = 1.0
        tan82 = 1/cot82
        Vdmax_divisor2 = (cot82 + tan82)
        Vdmax2 = (nu * phi_c * f_ck * B * z) / Vdmax_divisor2 if Vdmax_divisor2 > 0 else 0
        
        if Vu_n <= Vdmax1:
            cot_theta = 2.5
        elif Vu_n > Vdmax2:
            cot_theta = 1.0 # Section needs increase, but we use 1.0 for capacity calc
        else:
            # Automatic calculation
            asin_divisor = (nu * phi_c * f_ck * B * z)
            val_to_asin = Vu_n / asin_divisor if asin_divisor > 0 else 0
            if abs(val_to_asin) <= 1.0:
                theta_rad = 0.5 * math.asin(val_to_asin)
                tan_theta = math.tan(theta_rad)
                cot_theta = 1 / tan_theta if tan_theta != 0 else 2.5
                cot_theta = max(1.0, min(2.5, cot_theta))
            else:
                cot_theta = 1.0 # Fallback
        
        # Concrete capacity (Vc) for LSD 2012
        k = 1 + math.sqrt(200 / D) if D > 0 else 2.0
        k = min(k, 2.0)
        rho_l = analyzer.rho_l_tensile 
        rho_l_limited = min(rho_l, 0.02)
        
        # Sigma_cp (fn) due to axial force
        # Nu: compression (+), tension (-)
        Ac = B * analyzer.beam_h
        fn = analyzer.Nu * 1e3 / Ac if Ac > 0 else 0
        fn_limited = min(fn, 0.2 * phi_c * f_ck)
        
        f_ctk = analyzer.con_material.f_ctk
        
        # Vcd expressions
        Vcd_calc = (0.85 * phi_c * k * (rho_l_limited * f_ck)**(1/3) + 0.15 * fn_limited) * (B * D)
        Vcd_min = (0.4 * phi_c * f_ctk + 0.15 * fn_limited) * (B * D)
        V_c = max(Vcd_calc, Vcd_min)
        
        # Stirrup capacity
        av_use = analyzer.rebar.get_area(analyzer.av_dia) * analyzer.av_leg
        V_s = (phi_s * f_y * av_use * z / analyzer.av_space) * cot_theta if analyzer.av_space > 0 else 0
        
        # Additional tension check (Delta T)
        # Delta T = 0.5 * Vu * (cot_theta - cot_alpha)
        # alpha is stirrup angle (usually 90)
        cot_alpha = 0 # for vertical stirrups
        delta_t = 0.5 * Vu_n * (cot_theta - cot_alpha)
        
        # Delta TB = (Mr - Mu) / z
        # Mr is capacity at the section (pi_f * Mn)
        delta_tb = (analyzer.M_r - analyzer.Mu_nm) / z if z > 0 else 0

        # Result packaging
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
                "cot_alpha": cot_alpha, "alpha_deg": 90.0,
                "s_max_1": 0.75 * D * (1 + cot_alpha), # Simplified s_max
                "s_max_2": min(0.75 * D, 600)
            }
        }
