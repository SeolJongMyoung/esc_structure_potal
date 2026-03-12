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
        D = analyzer.d_eff
        Vu_n = analyzer.Vu_n
        
        # Methodology from user's calshear
        z = 0.9 * D
        nu = 0.6 * (1 - f_ck / 250)
        
        # User's logic for cot(theta)
        # sg = 3 (Auto calculation) assumed for engine
        # Vdmax calculations for theta selection
        cot81 = 2.5
        tan81 = 1/cot81
        Vdmax1 = (nu * analyzer.phi_c * f_ck * B * z) / (cot81 + tan81)
        
        cot82 = 1.0
        tan82 = 1/cot82
        Vdmax2 = (nu * analyzer.phi_c * f_ck * B * z) / (cot82 + tan82)
        
        if Vu_n <= Vdmax1:
            cot_theta = 2.5
        elif Vu_n > Vdmax2:
            cot_theta = 0 # Section needs increase
        else:
            # Automatic calculation
            val_to_asin = Vu_n / (0.2 * f_ck * (1 - f_ck / 250) * B * z)
            if abs(val_to_asin) <= 1.0:
                theta_rad = 0.5 * math.asin(val_to_asin)
                cot_theta = 1 / math.tan(theta_rad)
            else:
                cot_theta = 1.0 # Fallback
        
        # Calculate Vd (Shear reinforcement capacity)
        # Vd = (phi_s * fy * Av * 0.9*D / s) * cot_theta
        av_use = analyzer.rebar.get_area(analyzer.av_dia) * analyzer.av_leg
        
        # Concrete capacity (Vc) for LSD 2012
        k = 1 + math.sqrt(200 / D)
        k = min(k, 2.0)
        rho_s = min(analyzer.as_use / (B * D), 0.02)
        V_c = (0.85 * analyzer.phi_c * k * (rho_s * f_ck)**(1/3)) * (B * D)
        
        V_s = (phi_s * f_y * av_use * z / analyzer.av_space) * cot_theta
        
        # Result packaging
        return {
            "V_c": V_c,
            "V_s": V_s,
            "V_n": V_c + V_s,
            "V_max": Vdmax2, # Or specific Vdmax for cot_theta
            "theta": math.degrees(math.atan(1/cot_theta)) if cot_theta > 0 else 90
        }
