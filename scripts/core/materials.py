from math import sin, pi, sqrt
import math
import pandas as pd

class ConcMaterial:
    """
    Concrete material class supporting both USD and LSD methods.
    """
    def __init__(self, f_ck: float, m_c: float = 2300, method: str = "USD"):
        self.f_ck = f_ck
        self.m_c = m_c
        self.method = method # "USD" or "LSD"
        
        if method == "LSD":
            # LSD specific logic (User provided)
            self.f_cm = self._calc_f_cm_lsd(f_ck)
            res_e = self._calc_E_c_lsd(f_ck, m_c)
            self.E_c = res_e["val"]
            self.E_c_latex = res_e["latex"]
            
            # Tensile strength for LSD (Reference: Eurocode 2 or Korean Road Bridge Standard)
            # f_ctm = 0.3 * f_ck^(2/3) for f_ck <= 50
            # f_ctm = 2.12 * ln(1 + f_cm/10) for f_ck > 50
            if f_ck <= 50:
                self.f_ctm = 0.3 * (self.f_cm**(2/3))
            else:
                self.f_ctm = 2.12 * (math.log(1 + self.f_cm/10))
            self.f_ctk = 0.7 * self.f_ctm
            
            # Additional LSD constants for reporting
            self.alpha_cc = 0.85
            if 1.2 + 1.5 * ((100 - f_ck) / 60)**4 >= 2:
                self.n_eps = 2.0
            else:
                self.n_eps = 1.2 + 1.5 * ((100 - f_ck) / 60)**4
                
            if 0.002 + ((f_ck - 40) / 100000) <= 0.002:
                self.eps_co = 0.002
            else:
                self.eps_co = 0.002 + ((f_ck - 40) / 100000)
                
            if 0.0033 - ((f_ck - 40) / 100000) >= 0.0033:
                self.eps_cu = 0.0033
            else:
                self.eps_cu = 0.0033 - ((f_ck - 40) / 100000)
        else:
            # Traditional USD constants placeholders
            self.f_cm = f_ck
            self.E_c = self._calc_E_c_usd(f_ck, m_c)
            self.E_c_latex = ""
            self.alpha_cc = 1.0
            self.n_eps = 2.0
            self.eps_co = 0.002
            self.eps_cu = 0.003

    def _calc_E_c_usd(self, f_ck, m_c):
        # Existing logic from civil_usd_materials.py
        if f_ck <= 30:
            val = 0.043 * m_c**(1.5) * sqrt(f_ck)
        else:
            val = 0.030 * m_c**(1.5) * sqrt(f_ck) + 7700
        return val

    def _calc_E_c_lsd(self, f_ck, m_c):
        # New LSD logic from user
        f_cm = self._calc_f_cm_lsd(f_ck)
        # Ec formula: 0.077 * m_c^1.5 * fcm^1/3
        val = 0.077 * (m_c**1.5) * (f_cm**(1.0/3.0))
        latex = f"$0.077 \\times {m_c} ^ {{1.5}} \\times {f_cm} ^ {{1/3}} = {val:,.1f} \\; \\mathrm{{MPa}}$"
        return {"val": val, "latex": latex}

    def _calc_f_cm_lsd(self, f_ck):
        # New LSD logic from user (Sec_back version)
        if f_ck < 40:
            deltaf = 4.0
        elif f_ck >= 60:
            deltaf = 6.0
        else:
            deltaf = 4 + (f_ck - 40) / 10
        return f_ck + deltaf

    def __str__(self):
        return f"f_ck = {self.f_ck}, E_c = {self.E_c:.1f} (Method: {self.method})"

    def latex(self):
        latex_fck = f"f_{{ck}} = {self.f_ck} \\; \\mathrm{{MPa}}  "
        if self.method == "LSD":
            latex_fcm = f"f_{{cm}} = {self.f_cm} \\; \\mathrm{{MPa}}  "
            latex_E_c = f"E_{{c}} = {self.E_c:,.1f} \\; \\mathrm{{MPa}}"
            return "$" + latex_fck + "\\\\" + latex_fcm + "\\\\" + latex_E_c + "$"
        else:
            latex_E_c = f"E_{{c}} = {self.E_c:,.1f} \\; \\mathrm{{MPa}}"
            return "$" + latex_fck + "\\\\" + "\\\\" + latex_E_c + "$"

class RebarMaterial:
    def __init__(self, f_y):
        self.f_y = f_y
        self.E_s = 200000
        
    def __str__(self):
        return f"f_y = {self.f_y}, E_s = {self.E_s}"

class TendonMaterial:
    def __init__(self, f_y):
        self.E_ps = 200000
        
    def __str__(self):
        return f"E_ps = {self.E_ps}"
    
class SoilMaterial:
    def __init__(self, gamma_t, phi):
        self.gamma_t = gamma_t
        self.phi = phi
        self.phirad = phi / 180 * pi
        self.gamma_sub = gamma_t - 10.0
        self.coef_epressa = (1-sin(self.phirad))/(1+sin(self.phirad)) 
        self.coef_epressp = (1+sin(self.phirad))/(1-sin(self.phirad)) 
        self.coef_epresso = 1 - sin(self.phirad)

class SteelMaterial:
    def __init__(self, steelgrade: str, thick: int):
        # (Same implementation as provided by user)
        # Simplified for brevity in this initial version if needed, 
        # but the user provided the full logic so I will include it.
        steelgrades_1    =["SS235","SS275","SM275","SMA275","SS315","SM355","SMA355","SS410","SM420","SS450","SM460","SMA460","SS550"]
        Fylist_1_16mm    =[    235,    275,    275,     275,    315,    355,     355,    410,    420,    450,    460,     460,    550]
        Fylist_1_16_40mm =[    225,    265,    265,     265,    305,    345,     345,    400,    410,    440,    450,     450,    540]
        Fylist_1_40_75mm =[    205,    245,    255,     255,    295,    335,     335,    None,   400,   None,    430,     430,   None]
        Fylist_1_75_100mm =[    205,    245,    245,     245,    295,    325,     325,   None,   390,   None,    420,     420,   None]
        Fylist_1_100mm    =[    195,    235,    235,     235,    275,    305,     305,   None,   380,   None,   None,    None,   None]
        Fulist_1          =[    330,    410,    410,     410,    490,    490,     490,    540,   520,    590,    570,     570,    690]  

        df1 = pd.DataFrame([Fylist_1_16mm], columns=steelgrades_1)
        df1.loc[len(df1.index)] = Fylist_1_16_40mm
        df1.loc[len(df1.index)] = Fylist_1_40_75mm
        df1.loc[len(df1.index)] = Fylist_1_75_100mm
        df1.loc[len(df1.index)] = Fylist_1_100mm
        df1.loc[len(df1.index)] = Fulist_1

        if steelgrade in steelgrades_1:
            if thick <= 16: thickindex = 0
            elif thick < 40: thickindex = 1
            elif thick < 75: thickindex = 2
            elif thick < 100: thickindex = 3
            else: thickindex = 4
            self.F_y = df1.loc[thickindex, steelgrade]
            self.F_u = df1.loc[5, steelgrade]
        else:
            self.F_y = 0
            self.F_u = 0
