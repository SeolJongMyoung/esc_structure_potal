import math
from core.materials import ConcMaterial, RebarMaterial # Updated to new unified module
from rebar_area_ks import KoreanRebar
from standards import get_standard

class RCSectionAnalyzer:
    """
    핵심 연산 모듈 (단면력 및 철근량, 사용성 검토)
    구조물의 형태(보, 기둥, 옹벽)에 상관없이 단면정보와 하중정보만으로 해석 수행
    """
    def __init__(self, f_ck, f_y, standard_name, beam_h, beam_b, loads, rebar_data, phi_f=0.85, phi_v=None):
        self.f_ck = float(f_ck)
        self.f_y = float(f_y)
        self.standard_name = standard_name
        self.standard = get_standard(standard_name)
        
        # Methodology selection (USD vs LSD)
        self.method = self.standard.get_concrete_method() # "USD" or "LSD"
        
        # Default factors from standard
        std_phi_c, std_phi_s = self.standard.get_material_factors()
        
        if self.method == "LSD":
            # For LSD, UI's phi_f is phi_c, and phi_v is phi_s
            self.phi_c = float(phi_f) if phi_f is not None else std_phi_c
            self.phi_s = float(phi_v) if phi_v is not None else std_phi_s
            self.pi_f = 1.0 # Strength reduction is handled by material factors in LSD
            self.pi_v = 1.0 # But standard might define its own pi_v (handled in calc_shear)
        else:
            # For USD, UI's phi_f is strength reduction for flexure, phi_v is for shear
            self.phi_c, self.phi_s = std_phi_c, std_phi_s
            self.pi_f = float(phi_f)
            self.pi_v = float(phi_v) if phi_v is not None else self.standard.get_phi_v()

        self.alpha_fac, self.beta_fac = self.standard.get_flexure_factors(self.f_ck)
        self.alpha_cc = self.standard.get_alpha_cc()
        self.beta_1 = self.standard.get_beta_1(self.f_ck)
        
        # Design Strengths
        self.f_cd = self.f_ck * self.phi_c * self.alpha_cc
        self.f_yd = self.f_y * self.phi_s
        
        self.rebar = KoreanRebar()
        self.con_material = ConcMaterial(f_ck=self.f_ck, method=self.method)
        self.rebar_material = RebarMaterial(f_y=self.f_y)
        self.E_s = self.rebar_material.E_s
        self.E_c = self.con_material.E_c

        # Dimensions
        self.beam_h = float(beam_h)
        self.beam_b = float(beam_b)

        # Loads
        self.Mu = float(loads.get('Mu', 0))
        self.Vu = float(loads.get('Vu', 0))
        self.Nu = float(loads.get('Nu', 0))
        self.Ms = float(loads.get('Ms', 0))

        self.Mu_nm = self.Mu * 1e6
        self.Vu_n = self.Vu * 1e3
        self.Ms_nm = self.Ms * 1e6
        
        # Flexure defaults
        self.as_req = 0
        self.a = 0
        self.c = 0
        self.M_r = 0
        self.M_sf = 0
        self.tension_force = 0
        self.compression_force = 0
        self.phi_f_r = 0.85 # Default
        self.pi_f_r = 0.85
        self.epsilon_t = 0
        self.epsilon_y = 0
        self.as_min_val = 0
        self.as_max_val = 999999
        self.as_shrink = 0
        self.as_min_1 = 0
        self.as_min_2 = 0
        self.as_min_3 = 0
        self.s_detailing_max = 250
        self.s_detailing_ok = "-"
        self.c_max = 0
        self.eps_cu = 0.0033
        self.delta_redist = 1.0
        self.eps_s = 0
        self.eps_yd = 0

        # Rebar Data
        self.rebar_data = rebar_data
        self._parse_rebar_data(self.rebar_data)

        # Shear/Report defaults to avoid AttributeError (Moved after _parse_rebar_data to ensure d_eff is set)
        self.v_details = {}
        self.v_theta = 45 if self.method == "USD" else 0
        self.v_cot_theta = 1.0 if self.method == "USD" else 0
        self.delta_t = 0
        self.delta_tb = 0
        self.pi_V_c = 0
        self.V_s = 0
        self.z = 0.9 * self.d_eff

    def _parse_rebar_data(self, row):
        # Layer 1
        self.dc_1 = float(row.get("dc1", row.get("Dc", 0)))
        self.as_dia1 = int(row.get("dia1", row.get("as_dia", 25)))
        self.as_num1 = float(row.get("num1", row.get("as_num", 0)))
        self.as_use1 = self.rebar.get_area(self.as_dia1) * self.as_num1
        
        # Layer 2
        self.dc_2 = float(row.get("dc2", 0))
        self.as_dia2 = int(row.get("dia2", 13))
        self.as_num2 = float(row.get("num2", 0))
        self.as_use2 = self.rebar.get_area(self.as_dia2) * self.as_num2
        
        # Layer 3
        self.dc_3 = float(row.get("dc3", 0))
        self.as_dia3 = int(row.get("dia3", 13))
        self.as_num3 = float(row.get("num3", 0))
        self.as_use3 = self.rebar.get_area(self.as_dia3) * self.as_num3
        
        # Total Area and Centroid Calculation
        self.as_use = self.as_use1 + self.as_use2 + self.as_use3
        if self.as_use > 0:
            self.d_c = (self.as_use1 * self.dc_1 + self.as_use2 * self.dc_2 + self.as_use3 * self.dc_3) / self.as_use
        else:
            self.d_c = self.dc_1 if self.dc_1 > 0 else 0
            
        self.d_eff = self.beam_h - self.d_c
        # Use TOTAL reinforcement for LSD as requested by user to avoid Vcd=0 issues
        self.as_tensile = self.as_use
        self.d_tensile = self.d_eff
        self.dt = self.beam_h - self.dc_1 # Furthest layer for ductility checks
        
        self.rho_l_tensile = self.as_tensile / (self.beam_b * self.d_tensile) if (self.beam_b * self.d_tensile) > 0 else 0
        self.rho_l_tensile = min(self.rho_l_tensile, 0.02)
        self.rebar_id = 'D'

        # Stirrup
        self.av_dia = int(row.get("av_dia", 16))
        self.av_leg = float(row.get("av_leg", 0))
        self.av_space = float(row.get("av_space", 200))

        # Crack control environment
        self.crack_case = row.get("crack_case", "일반환경").strip()

    def calc_moment(self):
        if self.beam_h <= 0 or self.beam_b <= 0 or self.d_eff <= 0:
            self.as_req = 0; self.M_r = 0; self.M_sf = 0; return

        # Calculation based on DESIGN strengths (f_cd, f_yd)
        self.tension_force = self.as_use * self.f_yd
        # Force = alpha_fac * f_cd * b * c
        self.c = self.tension_force / (self.alpha_fac * self.f_cd * self.beam_b) if self.f_cd * self.beam_b > 0 else 0
        self.a = self.c * 2 * self.beta_fac # Approximation for 'a' to keep report consistent
        self.compression_force = self.alpha_fac * self.f_cd * self.beam_b # Force per unit depth c
        
        self.epsilon_y = self.f_y / self.E_s
        self.epsilon_t = 0.003 * (self.dt - self.c) / self.c if self.c > 0 else 0

        # Strength reduction factor for flexure (phi_f)
        std_phi_f, self.epsilon_t_result = self.standard.get_phi_f(self.epsilon_t, self.epsilon_y)
        
        if self.method == "USD":
            # Prioritize UI-provided phi_f override for USD/KCI
            self.pi_f_r = self.pi_f if self.pi_f > 0 else std_phi_f
        else:
            # For LSD, strength reduction is handled by material factors (phi_c, phi_s)
            self.pi_f_r = std_phi_f

        # Required Rebar
        # Mu = phi * As * f_yd * (d - beta_fac * c)
        # Force Equilibrium: As * f_yd = alpha_fac * f_cd * b * c  => c = (As * f_yd) / (alpha_fac * f_cd * b)
        # Mu = phi * As * f_yd * (d - beta_fac * (As * f_yd) / (alpha_fac * f_cd * b))
        # Mu = phi * As * f_yd * d - phi * As^2 * f_yd^2 * beta_fac / (alpha_fac * f_cd * b)
        # term * As^2 - (phi * f_yd * d) * As + Mu = 0
        K_val = (self.pi_f_r * self.f_yd**2 * self.beta_fac) / (self.alpha_fac * self.f_cd * self.beam_b) if self.alpha_fac * self.f_cd * self.beam_b > 0 else 0
        if K_val > 0:
            A = K_val
            B = -(self.pi_f_r * self.f_yd * self.d_eff)
            C = self.Mu_nm
            det = B**2 - 4 * A * C
            self.as_req = (-B - math.sqrt(det)) / (2 * A) if det >= 0 else 9999
        else:
            self.as_req = 0

        # Reinforcement ratio
        self.lo_min_1 = 1.4 / self.f_y
        self.lo_min_2 = 0.25 * math.sqrt(self.f_ck) / self.f_y
        self.lo_min = max(self.lo_min_1, self.lo_min_2)
        
        beta_1_usd = self.standard.get_beta_1(self.f_ck)
        self.lo_bal = (0.85 * beta_1_usd * self.f_ck / self.f_y) * (600 / (600 + self.f_y))
        self.lo_max = 0.75 * self.lo_bal
        self.lo_use = self.as_use / (self.beam_b * self.d_eff) if self.beam_b * self.d_eff > 0 else 0
        self.lo_min_3 = (4/3) * (self.as_req / (self.beam_b * self.d_eff)) if self.beam_b * self.d_eff > 0 else 0
        
        # Area based values for detailed reporting
        self.as_min_1 = self.lo_min_1 * self.beam_b * self.d_eff
        self.as_min_2 = self.lo_min_2 * self.beam_b * self.d_eff
        self.as_min_3 = (4/3) * self.as_req if hasattr(self, 'as_req') else 0
        self.as_min_val = min(max(self.as_min_1, self.as_min_2), self.as_min_3)
        
        self.as_shrink = 0.0018 * self.beam_b * self.beam_h
        self.as_max_val = 0.04 * self.beam_b * self.d_eff

        # Resistant Moment
        self.M_r = self.pi_f_r * self.as_use * self.f_yd * (self.d_eff - self.beta_fac * self.c) # N.mm
        self.M_sf = self.M_r / self.Mu_nm if self.Mu_nm > 0 else 0
        
        # LSD Specific details for report
        if self.method == "LSD":
            self.eps_cu = self.con_material.eps_cu
            self.delta_redist = 1.0 # Default redistribution factor
            self.c_max = (self.delta_redist - 0.6) * self.d_eff
            self.eps_s = self.eps_cu * (self.d_eff - self.c) / self.c if self.c > 0 else 0
            self.eps_yd = self.f_yd / self.E_s

    def calc_shear(self):
        # Initialize attributes used in reports
        self.V_c = 0; self.pi_V_c = 0; self.V_s = 0; self.pi_V_n = 0; self.av_req = 0
        self.av_use = self.rebar.get_area(self.av_dia) * self.av_leg
        self.av_space_min = 0; self.V_s_max = 0; self.d_eff_v = self.d_eff 
        
        if self.beam_b <= 0 or self.d_eff <= 0:
            return
        
        # Check for standard-specific shear logic (e.g. Truss model for LSD 2012)
        res = self.standard.calc_shear_capacity(self)
        if res is not None:
            self.V_c = res["V_c"]
            self.V_s = res["V_s"]
            self.pi_V_n = res["V_n"]
            self.pi_V_c = self.V_c # In LSD, material factors are often already in Vc
            self.v_theta = res.get("theta", 45)
            self.v_cot_theta = 1.0 / math.tan(math.radians(self.v_theta)) if self.v_theta > 0 else 0
            self.z = 0.9 * self.d_eff
            self.pi_v_s = self.V_s # In LSD stirrup phi is usually already in Vs
            self.v_details = res.get("details", {})
            # Delta T check (image p2)
            self.delta_t = self.v_details.get("delta_t", 0.5 * self.Vu_n * self.v_cot_theta)
            self.delta_tb = self.v_details.get("delta_tb", (self.M_r - self.Mu_nm) / self.z if self.z > 0 else 0)
            return

        self.z = 0.9 * self.d_eff_v
        self.v_theta = 45 # Default for USD
        self.v_cot_theta = 1.0 # cot(45) = 1.0
        self.delta_t = 0
        self.delta_tb = 0
        self.v_details = {}
        # For LSD, Vc often uses design strengths.
        # But here we stick to standard provided pi_v which may encapsulate material factors.
        self.V_c = (math.sqrt(self.f_ck) / 6) * self.beam_b * self.d_eff_v 
        if self.method == "LSD":
            # Simplified LSD Vc: roughly proportional to sqrt(fcd)
            self.V_c = (math.sqrt(self.f_cd) / 6) * self.beam_b * self.d_eff_v 
            
        self.pi_V_c = self.pi_v * self.V_c
        
        # Use f_yd for stirrups in LSD
        f_y_shear = self.f_yd if self.method == "LSD" else self.f_y
        self.V_s_max = self.standard.get_vs_max(self.f_ck, self.beam_b, self.d_eff_v)
        
        # Populate v_details for reporting even in fallback
        k_val = 1 + math.sqrt(200 / self.d_eff_v) if self.d_eff_v > 0 else 2.0
        k_val = min(k_val, 2.0)
        f_ctk = getattr(self.con_material, 'f_ctk', 0.6 * math.sqrt(self.f_ck))
        Ac_val = self.beam_b * self.beam_h
        self.v_details = {
            "k": k_val,
            "rho_l": self.rho_l_tensile,
            "f_ctk": f_ctk,
            "fn": self.Nu * 1e3 / Ac_val if Ac_val > 0 else 0,
            "Ac": Ac_val,
            "Vcd_calc": self.V_c,
            "Vcd_min": 0,
            "Vdmax1": self.V_s_max * 0.5, # Rough estimate for fallback
            "Vdmax2": self.V_s_max,
            "z": self.z,
            "nu": 0.6 * (1 - self.f_ck / 250),
            "cot_theta": self.v_cot_theta,
            "av_use": self.av_use
        }
        
        self.av_req = (self.Vu_n - self.pi_V_c) * self.av_space / (f_y_shear * self.d_eff_v * self.pi_v) if f_y_shear * self.d_eff_v * self.pi_v > 0 else 0
        self.av_req = max(0, self.av_req)
        
        self.av_space_min = min(600, 0.5 * self.d_eff_v)
        self.V_s = self.av_use * f_y_shear * self.d_eff_v / self.av_space if self.av_space > 0 else 0
        self.pi_V_n = self.pi_v * (self.V_c + self.V_s)

    def calc_service(self):
        # Initialize all service attributes to avoid AttributeErrors
        self.f_s = 0
        self.chi_o = 0
        self.s_use = 0
        self.s_min = 0
        self.service_details = {}
        
        if self.as_use <= 0 or self.E_c <= 0 or self.beam_b <= 0:
            return
        
        self.nr = self.E_s / self.E_c
        n = self.nr
        rho = self.as_use / (self.beam_b * self.d_eff) if (self.beam_b * self.d_eff) > 0 else 0
        
        # Neutral axis depth factor k = sqrt((n*rho)^2 + 2*n*rho) - n*rho
        k_neutral = math.sqrt((n * rho)**2 + 2 * n * rho) - n * rho
        self.chi_o = k_neutral * self.d_eff
        
        # Reinforcement stress sigma_s (f_s)
        # z = d - c/3
        z_arm = self.d_eff - self.chi_o / 3
        self.f_s = self.Ms_nm / (self.as_use * z_arm) if (self.as_use * z_arm) > 0 else 0
        
        # Spacing sa = sa,min
        self.s_use = (self.beam_b) / (self.as_num1) if self.as_num1 > 0 else 0
        
        # LSD Specific serviceability details
        if self.method == "LSD":
            f_ctm = self.con_material.f_ctm
            
            # kc calculation (KDS 24 14 21, 4.2.3.1 (1))
            if abs(self.Nu) < 1e-6:
                kc = 0.4  # Pure flexure
            else:
                # Subjected to flexure and axial force
                sigma_n = (self.Nu * 1e3) / (self.beam_b * self.beam_h) if (self.beam_b * self.beam_h) > 0 else 0
                h_star = 1000.0 # 1.0m reference
                h_ratio = self.beam_h / h_star if self.beam_h < h_star else 1.0
                
                if self.Nu > 0: # Compression
                    k1 = 1.5
                else: # Tension
                    k1 = (2 * h_star) / (3 * self.beam_h) if self.beam_h > 0 else 1.0
                
                # Equation from user provided image (3.1-6 context)
                # kc = 0.4 * [ 1 - sigma_n / (k1 * (h/h*) * fctm) ]
                divisor = k1 * (self.beam_h / h_star) * f_ctm
                kc = 0.4 * (1 - sigma_n / divisor) if divisor != 0 else 0.4
                kc = min(1.0, max(0.4, kc)) # Capped at 1.0 as per image/standard
            # k for scale effect (image shows 1.0, likely simplified or for h <= 300)
            k_scale = 1.0
            if self.beam_h > 300:
                k_scale = max(0.65, 1.0 - (self.beam_h - 300) * (1.0 - 0.65) / (800 - 300))
            
            # Act: area of concrete in tension zone (simplified as b * h / 2 or using c)
            # User image shows 475000 for 1000 width beam, likely h=950.
            # We'll use the gross tension side area for As_min check consistency with image patterns.
            h_tension = self.beam_h - self.chi_o
            Act = self.beam_b * h_tension # Or b * h / 2? Image suggests 475000 is 1000 * 950 / 2.
            # Let's use 0.5 * b * h for consistency with image's "gross tension area" feel.
            Act = 0.5 * self.beam_b * self.beam_h 
            
            as_min_lsd = (kc * k_scale * Act * f_ctm) / self.f_y if self.f_y > 0 else 0
            
            # 3. Max Bar Diameter Check (Table 4.2-4)
            def get_max_dia_limit(fs):
                # Table values based on user image (280 -> 14)
                table = [(160, 32), (200, 25), (240, 16), (280, 14), (320, 10), (360, 8)]
                if fs <= 160: return 32.0
                if fs >= 360: return 8.0
                for i in range(len(table)-1):
                    s1, d1 = table[i]
                    s2, d2 = table[i+1]
                    if s1 <= fs <= s2:
                        return d1 + (fs - s1)*(d2 - d1)/(s2 - s1)
                return 8.0
            
            max_dia_limit = get_max_dia_limit(self.f_s)
            dia_ok = self.as_dia1 <= max_dia_limit
            
            # 4. Max Bar Spacing Check (Table 4.2-5)
            def get_max_spacing_table(fs):
                # Table values based on user image
                table = [(160, 300), (200, 250), (240, 200), (280, 150), (320, 100), (360, 50)]
                if fs <= 160: return 300.0
                if fs >= 360: return 50.0
                for i in range(len(table)-1):
                    s1, l1 = table[i]
                    s2, l2 = table[i+1]
                    if s1 <= fs <= s2:
                        return l1 + (fs - s1)*(l2 - l1)/(s2 - s1)
                return 50.0
            
            s_table_limit = get_max_spacing_table(self.f_s)
            
            # sa_limit (Indirect crack control limit: min(3*d, S_table))
            sa_limit = min(3 * self.d_eff, s_table_limit) if self.d_eff > 0 else s_table_limit
            self.s_min = sa_limit # Sync for analyze()
            
            self.service_details = {
                "n": n,
                "rho": rho,
                "k_neutral": k_neutral,
                "c_neutral": self.chi_o,
                "z_arm": z_arm,
                "fs": self.f_s,
                "fsa": 0.8 * self.f_y, # Stress limit
                "kc": kc,
                "k_scale": k_scale,
                "Act": Act,
                "fctm": f_ctm,
                "as_min_lsd": as_min_lsd,
                "sa_limit": sa_limit,
                "sa_label": f"min(3d, {s_table_limit:.1f})",
                "max_dia_limit": max_dia_limit,
                "dia_ok": dia_ok,
                "s_table_limit": s_table_limit,
                "Ms_knm": self.Ms
            }
        else:
            # Existing USD bits
            self.cr_index = self.crack_case
            self.c_c = self.dc_1 - self.as_dia1 / 2
            self.k_cr = self.standard.get_k_cr(self.crack_case)
            self.s_min_1 = 375 * (self.k_cr / self.f_s) - 2.5 * self.c_c if self.f_s > 0 else 999
            self.s_min_2 = 300 * (self.k_cr / self.f_s) if self.f_s > 0 else 999
            self.s_min = min(self.s_min_1, self.s_min_2)

    def analyze(self):
        self.calc_moment()
        self.calc_shear()
        self.calc_service()
        
        calc_data = {
            "f_ck": self.f_ck, "f_y": self.f_y, "b": self.beam_b, "h": self.beam_h,
            "d": self.d_eff, "as_use": self.as_use, "as_req": self.as_req,
            "phi_mn": self.M_r, "mu_nm": self.Mu_nm
        }
        self.min_rebar_res = self.standard.check_min_rebar(calc_data)
        self.max_rebar_res = self.standard.check_max_rebar(calc_data)

        self.Mr_rate = self.M_r / self.Mu_nm if self.Mu_nm > 0 else 9.99
        self.Vn_rate = self.pi_V_n / self.Vu_n if self.Vu_n > 0 else 9.99
        
        self.v_reinf = "필요" if self.Vu_n > self.pi_V_c else "불필요"
        
        if self.as_use <= 0:
            self.crack_status = "-"
            self.s_detailing_ok = "-"
        else:
            if self.method == "LSD":
                # Aggregate Serviceability Checks for LSD (Min Rebar, Stress, Diameter, Spacing)
                sd = getattr(self, 'service_details', {})
                as_min_ok = self.as_use >= sd.get('as_min_lsd', 0)
                fs_ok = self.f_s <= sd.get('fsa', 999)
                dia_ok = sd.get('dia_ok', True) # Max diameter check
                s_ok = self.s_use <= self.s_min
                self.crack_status = "OK" if (as_min_ok and fs_ok and dia_ok and s_ok) else "NG"
            else:
                self.crack_status = "OK" if self.s_use <= self.s_min else "NG"
            
            # Detailing check based on user request: s_max = min(2h, 250)
            self.s_detailing_max = min(2 * self.beam_h, 250)
            self.s_detailing_ok = "O.K" if self.s_use <= self.s_detailing_max else "N.G"

        return self  # Return self so reports can access calculated properties

    def get_summary_result(self):
        # In LSD, we want to return phi_c and phi_s back to the UI's phi_f and phi_v fields
        # to prevent them from being reset to 1.0 (internal pi_f/pi_v).
        if self.method == "LSD":
            ret_phi_f = self.phi_c
            ret_phi_v = self.phi_s
        else:
            ret_phi_f = self.pi_f_r
            ret_phi_v = self.pi_v

        return {
            "as_req": round(self.as_req, 1) if hasattr(self, 'as_req') else 0,
            "as_used": round(self.as_use, 1),
            "as_ratio": round(self.as_use / self.as_req, 3) if self.as_req > 0 else 9.99,
            "Mr": round(self.M_r / 1e6, 1) if hasattr(self, 'M_r') else 0,
            "Mr_rate": round(self.Mr_rate, 3) if hasattr(self, 'Mr_rate') else 0,
            "Vn": round(self.pi_V_n / 1e3, 1) if hasattr(self, 'pi_V_n') else 0,
            "Vn_rate": round(self.Vn_rate, 3) if hasattr(self, 'Vn_rate') else 0,
            "V_reinf": getattr(self, 'v_reinf', "-"),
            "fs": round(self.f_s, 1) if hasattr(self, 'f_s') else 0,
            "crack_status": getattr(self, 'crack_status', "-"),
            "phi_f": round(ret_phi_f, 3),
            "phi_v": round(ret_phi_v, 3),
            "min_rebar_ok": getattr(self, 'min_rebar_res', {}).get('is_ok', False),
            "max_rebar_ok": getattr(self, 'max_rebar_res', {}).get('is_ok', False)
        }
