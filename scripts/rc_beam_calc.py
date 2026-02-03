import sys
import json
import math
from civil_usd_materials import ConcMaterial, RebarMaterial
from rebar_area_ks import KoreanRebar

class CalcReinfoeceConcrete:
    def __init__(self, data):
        self.rebar = KoreanRebar()
        
        mat = data.get("material", {})
        row = data.get("row", {})

        self.f_ck = float(mat.get("fck", 35))
        self.f_y = float(mat.get("fy", 400))
        self.pi_f = float(mat.get("phi_s", 0.85)) # Øf (Flexible - user might input as phi_s or similar)
        self.pi_v = float(mat.get("phi_s", 0.85)) # Øv

        self.con_material = ConcMaterial(f_ck=self.f_ck)
        self.rebar_material = RebarMaterial(f_y=self.f_y)

        self.Mu = float(row.get("Mu", 0))
        self.Vu = float(row.get("Vu", 0))
        self.Nu = float(row.get("Nu", 0))
        self.Ms = float(row.get("Ms", 0))
        self.beam_h = float(row.get("H", 0))
        self.beam_b = float(row.get("B", 0))
        self.dc_1 = float(row.get("Dc", 0))
        
        self.as_dia1 = int(row.get("as_dia", 25))
        self.as_num1 = float(row.get("as_num", 0))
        
        self.av_dia = int(row.get("av_dia", 16))
        self.av_leg = float(row.get("av_leg", 0))
        self.av_space = float(row.get("av_space", 200)) # Default 200 if not provided
        
        # Unit conversion
        self.Mu_nm = self.Mu * 1e6
        self.Vu_n = self.Vu * 1e3
        self.Nu_n = self.Nu * 1e3
        self.Ms_nm = self.Ms * 1e6
        
        self.E_s = self.rebar_material.E_s
        self.E_c = self.con_material.E_c
        
        # Simple d_c calculation (single layer for now as per minimal UI)
        self.as_use = self.rebar.get_area(self.as_dia1) * self.as_num1
        self.d_c = self.dc_1
        self.d_eff = self.beam_h - self.d_c

    def calc_moment(self):
        if self.beam_h <= 0 or self.beam_b <= 0 or self.d_eff <= 0:
            self.as_req = 0
            self.M_r = 0
            return

        if self.f_ck <= 28:
            self.beta_1 = 0.85
        else:
            self.beta_1 = max(0.65, 0.85 - (self.f_ck - 28) * 0.007)

        # Maximum/Minimum reinforcement ratio
        self.lo_bal = (0.85 * self.beta_1 * self.f_ck / self.f_y) * (6000 / (6000 + self.f_y))
        self.lo_max = 0.75 * self.lo_bal
        self.lo_min = max(1.4 / self.f_y, 0.25 * math.sqrt(self.f_ck) / self.f_y)

        # Tension behavior check (epsilon_t)
        # Assuming tension reinforcement only for simplicity as per user snippet
        self.tension_force = self.as_use * self.f_y
        self.compression_force_unit = 0.85 * self.f_ck * self.beam_b
        self.a = self.tension_force / self.compression_force_unit if self.compression_force_unit > 0 else 0
        self.c = self.a / self.beta_1 if self.beta_1 > 0 else 0
        
        self.epsilon_y = self.f_y / self.E_s
        self.epsilon_t = 0.003 * (self.d_eff - self.c) / self.c if self.c > 0 else 0

        # Strength reduction factor (phi) interpolation
        if self.epsilon_t >= 0.005:
            self.pi_f_r = self.pi_f
        elif self.epsilon_t > self.epsilon_y:
            # Linear interpolation between 0.65 and 0.85 (or self.pi_f)
            self.pi_f_r = (self.pi_f - 0.65) / (0.005 - self.epsilon_y) * (self.epsilon_t - self.epsilon_y) + 0.65
        else:
            self.pi_f_r = 0.65

        # Required Rebar Calculation (Quadratic equation for 'as')
        # Mu = phi * as * fy * (d - (as * fy)/(2 * 0.85 * fck * b))
        # Let K = 1 / (2 * 0.85 * fck * b)
        # Mu / (phi * fy) = as * d - K * fy * as^2
        # (K * fy) * as^2 - d * as + (Mu / (phi * fy)) = 0
        K_fy = self.f_y / (2 * 0.85 * self.f_ck * self.beam_b) if self.f_ck * self.beam_b > 0 else 0
        
        if K_fy > 0:
            A = K_fy
            B = -self.d_eff
            C = self.Mu_nm / (self.pi_f_r * self.f_y) if self.pi_f_r * self.f_y > 0 else 0
            
            det = B**2 - 4 * A * C
            if det >= 0:
                self.as_req = (-B - math.sqrt(det)) / (2 * A)
            else:
                self.as_req = 99999 # Design Fail
        else:
            self.as_req = 0

        # Resistant Moment (M_r) in kN.m
        self.M_r = self.pi_f_r * self.as_use * self.f_y * (self.d_eff - self.a / 2) / 1e6

    def calc_shear(self):
        if self.beam_b <= 0 or self.d_eff <= 0:
            self.V_c = 0
            self.pi_V_c = 0
            self.V_s = 0
            self.pi_V_n = 0
            return

        # Vc: Concrete shear strength
        self.V_c = (math.sqrt(self.f_ck) / 6) * self.beam_b * self.d_eff / 1000 # kN
        self.pi_V_c = self.pi_v * self.V_c
        
        # Vs: Stirrup strength
        # Vs = Av * fy * d / s
        self.av_area = self.rebar.get_area(self.av_dia) * self.av_leg
        if self.av_space > 0:
            self.V_s = self.av_area * self.f_y * self.d_eff / self.av_space / 1000 # kN
        else:
            self.V_s = 0
            
        self.pi_V_n = self.pi_v * (self.V_c + self.V_s)

    def calc_service(self):
        # cracking check (simplified as per user code)
        if self.as_use <= 0 or self.E_c <= 0:
            self.chi_o = 0
            self.f_s = 0
            return

        # Normal rebar ratio (n)
        self.nr = round(self.E_s / self.E_c)
        # Neutral axis depth (chi_o)
        B1 = self.nr * self.as_use / self.beam_b
        self.chi_o = -B1 + math.sqrt(B1**2 + 2 * B1 * self.d_eff)
        
        # Stress in rebar (f_s)
        self.f_s = self.Ms_nm / (self.as_use * (self.d_eff - self.chi_o / 3)) if self.as_use > 0 else 0

    def calculate(self):
        self.calc_moment()
        self.calc_shear()
        self.calc_service()
        
        return {
            "as_req": round(self.as_req, 1),
            "as_used": round(self.as_use, 1),
            "as_ratio": round(self.as_use / self.as_req, 3) if self.as_req > 0 else 0,
            "Mr": round(self.M_r, 1),
            "Vn": round(self.pi_V_n, 1),
            "fs": round(self.f_s, 1),
            "phi_f": round(self.pi_f_r, 3),
            "phi_v": round(self.pi_v, 3)
        }

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())
        results = []
        material = input_data.get("material", {})
        for row in input_data.get("rows", []):
            calc = CalcReinfoeceConcrete({"material": material, "row": row})
            results.append(calc.calculate())
        print(json.dumps(results))
    except Exception as e:
        # Standard error response
        print(json.dumps([{"error": str(e)}]))
