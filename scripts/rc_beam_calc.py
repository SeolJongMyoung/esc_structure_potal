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
        self.pi_f = float(mat.get("phi_s", 0.85)) # Base Øf
        self.pi_v = float(mat.get("phi_v", 0.75)) # Øv (Usually 0.75 for USD)
        
        self.con_material = ConcMaterial(f_ck=self.f_ck)
        self.rebar_material = RebarMaterial(f_y=self.f_y)
        self.E_s = self.rebar_material.E_s
        self.E_c = self.con_material.E_c

        self.Mu = float(row.get("Mu", 0))
        self.Vu = float(row.get("Vu", 0))
        self.Nu = float(row.get("Nu", 0))
        self.Ms = float(row.get("Ms", 0))
        self.beam_h = float(row.get("H", 0))
        self.beam_b = float(row.get("B", 0))
        self.dc_1 = float(row.get("Dc", 0))
        
        self.Mu_nm = self.Mu * 1e6
        self.Vu_n = self.Vu * 1e3
        self.Ms_nm = self.Ms * 1e6
        
        self.as_dia1 = int(row.get("as_dia", 25))
        self.as_num1 = float(row.get("as_num", 0))
        self.rebar_id = 'D'
        self.as_use1 = self.rebar.get_area(self.as_dia1)
        self.as_use = self.as_use1 * self.as_num1
        self.d_c = self.dc_1 # Used in report
        self.d_eff = self.beam_h - self.dc_1
        self.dt = self.d_eff # dt is usually for bottom rebar

        # Multi-layer placeholders as per snippet
        self.as_dia2 = 0; self.as_num2 = 0; self.as_use2 = 0; self.dc_2 = 0
        self.as_dia3 = 0; self.as_num3 = 0; self.as_use3 = 0; self.dc_3 = 0
        
        # Stirrup
        self.av_dia = int(row.get("av_dia", 16))
        self.av_leg = float(row.get("av_leg", 0))
        self.av_space = float(row.get("av_space", 200))

    def calc_moment(self):
        if self.beam_h <= 0 or self.beam_b <= 0 or self.d_eff <= 0:
            self.as_req = 0; self.M_r = 0; self.M_sf = 0; return

        if self.f_ck <= 28:
            self.beta_1 = 0.85
        else:
            self.beta_1 = max(0.65, 0.85 - (self.f_ck - 28) * 0.007)

        # Tension behavior
        self.tension_force = self.as_use * self.f_y
        self.a = self.tension_force / (0.85 * self.f_ck * self.beam_b) if self.f_ck * self.beam_b > 0 else 0
        self.c = self.a / self.beta_1 if self.beta_1 > 0 else 0
        self.compression_force = 0.85 * self.f_ck * self.beam_b # This is Force per mm (0.85*fck*b) as per user snippet logic C = ... * a
        
        self.epsilon_y = self.f_y / self.E_s
        self.epsilon_t = 0.003 * (self.dt - self.c) / self.c if self.c > 0 else 0

        # Strength reduction factor interpolation
        if self.epsilon_t >= 0.005:
            self.pi_f_r = 0.85
            self.epsilon_t_result = "인장지배단면"
        elif self.epsilon_t <= self.epsilon_y:
            self.pi_f_r = 0.65
            self.epsilon_t_result = "압축지배단면"
        else:
            self.pi_f_r = 0.65 + (0.85 - 0.65) * (self.epsilon_t - self.epsilon_y) / (0.005 - self.epsilon_y)
            self.epsilon_t_result = "변화구역단면"

        # Required Rebar (Quadratic solver)
        K_fy = self.f_y / (2 * 0.85 * self.f_ck * self.beam_b) if self.f_ck * self.beam_b > 0 else 0
        if K_fy > 0:
            A = K_fy
            B = -self.d_eff
            C = self.Mu_nm / (self.pi_f_r * self.f_y) if self.pi_f_r * self.f_y > 0 else 0
            det = B**2 - 4 * A * C
            self.as_req = (-B - math.sqrt(det)) / (2 * A) if det >= 0 else 9999
        else:
            self.as_req = 0

        # Reinforcement ratio check
        self.lo_min_1 = 1.4 / self.f_y
        self.lo_min_2 = 0.25 * math.sqrt(self.f_ck) / self.f_y
        self.lo_min = max(self.lo_min_1, self.lo_min_2)
        self.lo_bal = (0.85 * self.beta_1 * self.f_ck / self.f_y) * (6000 / (6000 + self.f_y))
        self.lo_max = 0.75 * self.lo_bal
        self.lo_use = self.as_use / (self.beam_b * self.d_eff) if self.beam_b * self.d_eff > 0 else 0
        self.lo_min_3 = (4/3) * (self.as_req / (self.beam_b * self.d_eff)) if self.beam_b * self.d_eff > 0 else 0

        # Resistant Moment
        self.M_r = self.pi_f_r * self.as_use * self.f_y * (self.d_eff - self.a / 2) # N.mm
        self.M_sf = self.M_r / self.Mu_nm if self.Mu_nm > 0 else 0

    def calc_shear(self):
        if self.beam_b <= 0 or self.d_eff <= 0:
            self.V_c = 0; self.pi_V_c = 0; self.V_s = 0; self.pi_V_n = 0; return
        
        self.d_eff_v = self.d_eff # Snippet uses d_eff_v
        self.V_c = (math.sqrt(self.f_ck) / 6) * self.beam_b * self.d_eff_v # N
        self.pi_V_c = self.pi_v * self.V_c
        
        self.av_use = self.rebar.get_area(self.av_dia) * self.av_leg
        self.av_req = (self.Vu_n - self.pi_V_c) * self.av_space / (self.f_y * self.d_eff_v * self.pi_v) if self.f_y * self.d_eff_v * self.pi_v > 0 else 0
        self.av_req = max(0, self.av_req)
        
        self.av_space_min = min(600, 0.5 * self.d_eff_v)
        self.V_s = self.av_use * self.f_y * self.d_eff_v / self.av_space if self.av_space > 0 else 0
        self.V_s_max = (2/3) * math.sqrt(self.f_ck) * self.beam_b * self.d_eff_v
        self.pi_V_n = self.pi_v * (self.V_c + self.V_s)

    def calc_service(self):
        if self.as_use <= 0 or self.E_c <= 0:
            self.f_s = 0; self.chi_o = 0; self.s_use = 0; self.s_min = 0; return
        
        self.nr = self.E_s / self.E_c
        n = self.nr
        # chi_o = -n*As/b + n*As/b * sqrt(1 + 2*b*d/(n*As))
        term = (n * self.as_use / self.beam_b)
        self.chi_o = -term + term * math.sqrt(1 + 2 * self.beam_b * self.d_eff / (n * self.as_use))
        self.f_s = self.Ms_nm / (self.as_use * (self.d_eff - self.chi_o / 3)) if self.as_use > 0 else 0
        
        # Crack control Sa
        self.cr_index = "보통" # Placeholder
        self.c_c = self.dc_1 - self.as_dia1 / 2
        self.k_cr = 210 # Kcr = 210 (보통), 170 (매우심함)
        self.s_min_1 = 375 * (self.k_cr / self.f_s) - 2.5 * self.c_c if self.f_s > 0 else 999
        self.s_min_2 = 300 * (self.k_cr / self.f_s) if self.f_s > 0 else 999
        self.s_min = min(self.s_min_1, self.s_min_2)
        self.s_use = (self.beam_b - 2 * 40 - self.as_dia1) / (self.as_num1 - 1) if self.as_num1 > 1 else 0

    def calculate(self):
        self.calc_moment()
        self.calc_shear()
        self.calc_service()
        
        return {
            "as_req": round(self.as_req, 1),
            "as_used": round(self.as_use, 1),
            "as_ratio": round(self.as_use / self.as_req, 3) if self.as_req > 0 else 0,
            "Mr": round(self.M_r / 1e6, 1),
            "Vn": round(self.pi_V_n / 1e3, 1),
            "fs": round(self.f_s, 1),
            "phi_f": round(self.pi_f_r, 3),
            "phi_v": round(self.pi_v, 3)
        }

    def add_to_excel_workbook(self, wb, sheet_name):
        from openpyxl.styles import Font, Border, Side, Alignment, PatternFill
        from string import ascii_uppercase
        
        self.calculate()
        wsout = wb.create_sheet(title=sheet_name)
        
        # Set up basic formatting
        alpalist = list(ascii_uppercase)
        for i in range(1, 100):
            wsout.row_dimensions[i].height = 15
        for i in alpalist:
            wsout.column_dimensions[i].width = 3.0
        font_format = Font(size=9, name='굴림체')
        for rows in wsout["A1":"Z100"]:
            for cell in rows:
                cell.font = font_format

        # Section 1: Basic Information
        wsout['B2'].value = '1) 단면제원 및 설계가정'
        wsout['C3'].value = f"fck = {self.f_ck} MPa, fy = {self.f_y} MPa, Øf = {self.pi_f_r:.2f}, Øv = {self.pi_v:.2f}, Es = {self.E_s} MPa"

        # Formatting for table headers
        for r in range(4,6) :                        # 4~5행 글짜 위치 중앙으로 정렬
            for c in range(3,24) :                      
                wsout.cell(r,c).alignment = Alignment(horizontal='center', vertical='center')  
        for r in range(4,6) :                        # 4~5행 테두리 그리기
            for c in range(3,24) :                      
                wsout.cell(r,c).border = Border(left=Side(border_style='thin'),right=Side(border_style='thin'),top=Side(border_style='thin'),bottom=Side(border_style='thin'))
        for r in range(4,6) :                        # 셀 병합 C4~L4, C5~L5
            for c in [3,6,9,12] :                       
                c1 = c + 2
                wsout.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c1)
        for r in range(4,6) :                         # 셀 병합 O4~W4, O5~W5  
            for c in [15,19,23] :                          
                c1 = c + 3
                wsout.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c1)    
        for c in range(3,24) :                         # 셀 채우기 C4~T5
            wsout.cell(4,c).fill = PatternFill(fill_type='solid', fgColor='0FFFF0')
        
        wsout['C4'].value = 'B(mm)'; wsout['F4'].value = 'H(mm)'; wsout['I4'].value = 'd(mm)'; wsout['L4'].value = '피복(mm)'
        wsout['O4'].value = 'Mu(N.mm)'; wsout['S4'].value = 'Vu(N)'; wsout['W4'].value = 'Ms(N.mm)'
        wsout['C5'].value = self.beam_b; wsout['F5'].value = self.beam_h; wsout['I5'].value = f"{self.d_eff:.1f}"; wsout['L5'].value = f"{self.d_c:.1f}"
        wsout['O5'].value = self.Mu_nm; wsout['S5'].value = self.Vu_n; wsout['W5'].value = self.Ms_nm

        wsout['B7'].value = '2) 콘크리트 재료상수'
        wsout['C8'].value = 'β1    : 등가 사각형 응력 블록의 깊이계수'; wsout['P8'].value = '='; wsout['Q8'].value = self.beta_1

        # Section 3: Strength reduction factor
        wsout['B10'].value = '3) 강도감소계수(Ø) 산정'
        wsout['C11'].value = f"T = As x fy = {self.as_use:.3f} x {self.f_y:.3f} = {self.tension_force:.1f} N"
        wsout['C12'].value = f"C = 0.85 x fck x a x b = 0.85 x {self.f_ck:.3f} x a x {self.beam_b:.3f} = {self.compression_force:.1f} x a"
        wsout['C13'].value = f"T = C 이므로, a = {self.a:.3f} mm, c = {self.a:.3f} / β1 = {self.a:.3f} / {self.beta_1:.3f} = {self.c:.3f} mm"
        wsout['C14'].value = f"εy = fy / Es = {self.f_y} / {self.E_s} = {self.epsilon_y:.5f}"
        wsout['C15'].value = f"εt = 0.00300 x (dt - c) / c = 0.00300 x ({self.d_eff:.3f} - {self.c:.2f}) / {self.c:.2f} = {self.epsilon_t:.5f}"
        if self.epsilon_t >= 0.005:
            wsout['C16'].value = f"εt ≥ 0.0050 이므로 {self.epsilon_t_result}이며, Ø = {self.pi_f_r:.2f} 를 적용한다"
        else:
            wsout['C16'].value = f"εt < 0.0050 이므로 {self.epsilon_t_result}이며, Ø = {self.pi_f_r:.2f} 를 적용한다"

        # Section 4: Required Reinforcement Calculation
        wsout['B18'].value = '4) 필요철근량 산정'
        wsout['C19'].value = 'Mu / Øf = As x fy  x (d - a / 2)              ----------------   ①'
        wsout['C20'].value = ' a = As x fy  / ( 0.85 x fck x b)             ----------------   ②'
        wsout['C21'].value = ' 식②를 식①에 대입하여 이차방정식으로 As를 구한다'
        wsout['E22'].value = ' fy²                                Mu'
        wsout['C23'].value = f" ────────── As² - fy x d x As + ───  = 0 ,   Asreq = {self.as_req:.3f} mm²"
        wsout['C24'].value = ' 2 x 0.85 x fck x b                         Øf '
        
        # Section 5: Used Reinforcement
        wsout['B26'].value = f"5) 사용철근량 : Asuse = {self.as_use:.1f} mm², 철근도심 : dc = {self.d_eff:.1f}mm,  [ 사용율 = {self.as_use/self.as_req if self.as_req > 0 else 0:.3f} ]"
        wsout['F27'].value = f"1단 : {self.rebar_id} {self.as_dia1} - {self.as_num1} EA (= {self.as_use1*self.as_num1:.1f} mm², dc1 = {self.dc_1:.1f} mm)"
        wsout['F28'].value = f"2단 : {self.rebar_id} {self.as_dia2} - {self.as_num2} EA (= {self.as_use2*self.as_num2:.1f} mm², dc2 = {self.dc_2:.1f} mm)"
        wsout['F29'].value = f"3단 : {self.rebar_id} {self.as_dia3} - {self.as_num3} EA (= {self.as_use3*self.as_num3:.1f} mm², dc3 = {self.dc_3:.1f} mm)"

        # Section 6: Reinforcement Check
        wsout['B31'].value = "6) 철근비 검토"
        wsout['C32'].value = f"ρmin : 1.4 / fy          = {self.lo_min_1:.6f} "
        wsout['C33'].value = f"       0.25 x √fck / fy  = {self.lo_min_2:.6f},  ρmin = {self.lo_min:.6f} 적용"
        wsout['C34'].value = f"ρmax = 0.75 x ρb = 0.75 x (0.85 x β1 x fck / fy) x (6,000 / (6,000 + fy)) = {self.lo_bal:.6f}" 
        wsout['C35'].value = f"ρuse = As / ( b x d ) = {self.lo_use:.6f} " 
        if self.lo_use >= self.lo_min :
            if self.lo_use < self.lo_max :
                wsout['C36'].value = f"ρmax ≥ ρuse ≥ ρmin --> 최소철근비, 최대철근비 만족   ∴ O.K"
            else:
                wsout['C36'].value = f"ρmax < ρuse ≥ ρmin --> 최소철근비 만족, 최대 철근비 불만족   ∴ N.G"
        else :
            if self.lo_use < self.lo_max :
                wsout['C36'].value = f"ρmax ≥ ρuse < ρmin --> 최소철근비 불만족,  최대 철근비 만족   ∴ N.G"
                if self.lo_use >= self.lo_min_3 :
                    wsout['C37'].value = f"ρuse ≥ 4 x ρreq / 3 = {self.lo_min_3:.6f} --> 최소철근비 만족   ∴ O.K"
                else :
                    wsout['C37'].value = f"ρuse < 4 x ρreq / 3 = {self.lo_min_3:.6f} --> 최소철근비 불만족   ∴ N.G"
            else :    
                wsout['C36'].value = f"ρmax < ρuse < ρmin --> 최소철근비, 최대 철근비 불만족   ∴ N.G"

        # Section 7: Design Flexural Strength Calculation
        wsout['B39'].value = "7) 설계 휨강도 산정"
        wsout['C40'].value = f"a = As x fy / (0.85 x fck x b) = {self.a:.3f}mm"
        wsout['C41'].value = f"Ø Mn = Øf x As x fy x (d - a / 2)"
        wsout['C42'].value = f"     = {self.pi_f_r:.2f} x {self.as_use:.1f} x {self.f_y} x ({self.d_eff:.1f} - {self.a:.3f} / 2)"
        if self.M_r > self.Mu_nm:
            wsout['C43'].value = f"     = {self.M_r:.1f} N.mm ≥ Mu = {self.Mu_nm:.1f} N.mm  ∴ O.K  [S.F = {self.M_sf:.3f}]"
        else:
            wsout['C43'].value = f"     = {self.M_r:.1f} N.mm < Mu = {self.Mu_nm:.1f} N.mm  ∴ N.G  [S.F = {self.M_sf:.3f}]"

        # Section 10: Shear Check
        wsout['B45'].value ="10) 전단검토"
        wsout['C46'].value =f"Φ Vc = Φv x √fck x b x d / 6"
        wsout['C47'].value =f"    = {self.pi_v:.2f} x √{self.f_ck} x {self.beam_b} x {self.d_eff_v:.1f} / 6 = {self.pi_V_c:.1f} N"
        if self.pi_V_c >= self.Vu_n :
            wsout['C48'].value =f"Φ Vc ≥ Vu = {self.Vu_n:.1f} N  ∴ 전단보강 불필요"
        else :
            wsout['C48'].value =f"Φ Vc < Vu = {self.Vu_n:.1f} N  ∴ 전단보강 필요"
            wsout['C50'].value =f"Av_req = ( {self.Vu_n/1000:.3f} - {self.pi_V_c/1000:.3f} ) x {self.av_space:.1f} / ( {self.f_y} x {self.d_eff_v:.1f} x {self.pi_v:.2f}) = {self.av_req:.3f} mm²"
            wsout['C51'].value =f"Av_use = {self.av_use:.3f} mm² ( {self.rebar_id}{self.av_dia} - {self.av_leg}EA,  C.T.C {self.av_space} mm )"
            if self.av_space > self.av_space_min :
                wsout['C52'].value =f"사용간격 {self.av_space} mm > 최소간격 = min(60cm, 0.5D) = {self.av_space_min:.3f}  ∴ N.G"
            else :
                wsout['C52'].value =f"사용간격 {self.av_space}mm ≤ 최소간격 = min(60cm, 0.5D) = {self.av_space_min:.3f}  ∴ O.K"
            wsout['C54'].value =f"Vs = {self.av_use:.3f} x {self.f_y:.1f} x {self.d_eff_v:.1f} / {self.av_space} = {self.V_s:.1f} N "
            wsout['C55'].value =f"Vs_max = 2 x √{self.f_ck:.1f} / 3 x {self.beam_b} x {self.d_eff_v:.3f} "

            if self.V_s <= self.V_s_max :
                wsout['C56'].value =f"       = {self.V_s_max:.1f} N ≤ Vs = {self.V_s:.1f} N  ∴ O.K" 
            else :
                wsout['C56'].value =f"       = {self.V_s_max:.1f} N > Vs = {self.V_s:.1f} N  ∴ N.G" 

            if self.pi_V_n >= self.Vu_n :
                wsout['C57'].value =f" ΦVn = {self.pi_v:.2f} x ( {self.V_c:.1f} + {self.V_s:.1f} ) = {self.pi_V_n:.3f} N ≥ Vu = {self.Vu_n:.1f} N  ∴ O.K" 
            else :
                wsout['C57'].value =f" ΦVn = {self.pi_v:.2f} x ( {self.V_c:.1f} + {self.V_s:.1f} ) = {self.pi_V_n:.3f} N < Vu = {self.Vu_n:.1f} N  ∴ N.G"
            
        # Section 11: Crack Control
        wsout['B59'].value ="11) 균열검토"
        wsout['C60'].value =f"① 응력 산정"
        wsout['D61'].value =f"fs = M / [As x (d - χ/3)] = {self.Ms_nm:.1f} / [ {self.as_use:.3f} x ( {self.d_eff:.3f} - {self.chi_o:.2f} / 3 )] "
        wsout['D62'].value =f"   =  {self.f_s:.3f} MPa"
        wsout['D63'].value =f"χ = -n x As / b + n x As / b x √ [ 1 + 2 x b x d / ( n x As ) ]"
        wsout['D64'].value =f"  = -{self.nr:.1f} x {self.as_use:.1f} / {self.beam_b} + {self.nr:.1f} x {self.as_use:.1f} / {self.beam_b} x √ [1 + 2 x {self.beam_b} x {self.d_eff:.3f} / ({self.nr:.1f} x {self.as_use:.1f})]"
        wsout['D65'].value =f"  = {self.chi_o:.3f} mm"
        wsout['D66'].value =f"사용철근량 = {self.as_use:.3f} mm²  (최외단 철근도심 : {self.dc_1:.1f} mm)"
        wsout['D67'].value =f"      1단 : {self.rebar_id}{self.as_dia1} - {self.as_num1:.1f} EA, 2단 : {self.rebar_id}{self.as_dia2} - {self.as_num2:.1f} EA, 3단 : {self.rebar_id}{self.as_dia3} - {self.as_num3:.1f} EA )"
        
        wsout['C69'].value =f"② 철근의 최대 중심간격"
        wsout['D70'].value =f"강재의 부식에 대한 환경조건은 『 {self.cr_index} 』 적용"
        wsout['D71'].value =f"Cc = {self.dc_1:.1f} - {self.as_dia1} / 2 = {self.c_c:.2f} mm"
        wsout['D72'].value =f"여기서 Cc ; 인장철근이나 긴장재의 표면과 콘크리트 표면사이의 두께(mm)"
        wsout['D74'].value =f"Smin : 375 x (Kcr / fs) - 2.5 x Cc = 375 x ({self.k_cr} / {self.f_s:.3f}) - 2.5 x {self.c_c:.3f} = {self.s_min_1:.3f} mm"
        wsout['D75'].value =f"       300 x (Kcr / fs) = 300 x ({self.k_cr} / {self.f_s:.3f}) = {self.s_min_2:.3f} mm"
        wsout['D76'].value =f"여기서 Kcr = {self.k_cr} ( 철근 간격을 통한 균열 검증에서 철근의 노출 조건을 고려한 계수 )" 
        wsout['D77'].value =f"∴ Sa는 작은 값인 {self.s_min:.3f} mm 를 적용 "
        
        if self.s_min >= self.s_use :
            wsout['D78'].value =f" Sa = {self.s_min:.3f} mm  ≥ suse = {self.s_use:.3f} mm  ∴ O.K" 
        else :
            wsout['D78'].value =f" Sa = {self.s_min:.3f} mm  < suse = {self.s_use:.3f} mm  ∴ N.G"

    def generate_text_report(self):
        self.calculate()
        
        # 1) 단면제원 및 설계가정
        sec1 = []
        sec1.append("1) 단면제원 및 설계가정")
        sec1.append(f"   fck = {self.f_ck:.1f} MPa, fy = {self.f_y:.1f} MPa, Øf = {self.pi_f_r:.2f}, Øv = {self.pi_v:.2f}, Es = {self.E_s:.0f} MPa")
        sec1.append("   " + "-"*75)
        sec1.append(f"   | {'B(mm)':^8} | {'H(mm)':^8} | {'d(mm)':^8} | {'피복(mm)':^8} | {'Mu(N.mm)':^12} | {'Vu(N)':^10} | {'Ms(N.mm)':^10} |")
        sec1.append("   " + "-"*75)
        sec1.append(f"   | {self.beam_b:^8.0f} | {self.beam_h:^8.0f} | {self.d_eff:^8.1f} | {self.dc_1:^8.1f} | {self.Mu_nm:^12.0f} | {self.Vu_n:^10.0f} | {self.Ms_nm:^10.0f} |")
        sec1.append("   " + "-"*75)
        
        # 2) 콘크리트 재료상수
        sec2 = []
        sec2.append("2) 콘크리트 재료상수")
        sec2.append(f"   β1   : 등가 사각형 응력 블록의 깊이계수           = {self.beta_1:.3f}")
        
        # 3) 강도감소계수(Ø) 산정
        sec3 = []
        sec3.append("3) 강도감소계수(Ø) 산정")
        sec3.append(f"   T = As x fy = {self.as_use:.3f} x {self.f_y:.3f} = {self.tension_force:.1f} N")
        sec3.append(f"   C = 0.85 x fck x a x b = 0.85 x {self.f_ck:.3f} x a x {self.beam_b:.3f} = {0.85*self.f_ck*self.beam_b:.1f} x a")
        sec3.append(f"   T = C 이므로, a = {self.a:.3f} mm, c = a / β1 = {self.a:.3f} / {self.beta_1:.3f} = {self.c:.3f} mm")
        sec3.append(f"   εy = fy / Es = {self.f_y:.1f} / {self.E_s:.0f} = {self.epsilon_y:.5f}")
        sec3.append(f"   εt = 0.00300 x (dt - c) / c = 0.00300 x ({self.dt:.3f} - {self.c:.3f}) / {self.c:.3f} = {self.epsilon_t:.5f}")
        compare_op = "≥" if self.epsilon_t >= 0.005 else "<"
        sec3.append(f"   εt {compare_op} 0.0050 이므로 {self.epsilon_t_result}이며, Ø = {self.pi_f_r:.2f} 를 적용한다")

        # 4) 필요철근량 산정
        sec4 = []
        sec4.append("4) 필요철근량 산정")
        sec4.append("   Mu / Øf = As x fy x (d - a / 2)              ---------------- ①")
        sec4.append("   a = As x fy / (0.85 x fck x b)               ---------------- ②")
        sec4.append("   식②를 식①에 대입하여 이차방정식으로 As를 구한다")
        sec4.append("           fy²                                Mu")
        sec4.append(f"   ------------------ As² - fy x d x As + ------ = 0 ,  Asreq = {self.as_req:.3f} mm²")
        sec4.append("    2 x 0.85 x fck x b                         Øf")

        # 5) 사용철근량
        sec5 = []
        usage_ratio = self.as_use / self.as_req if self.as_req > 0 else 0
        sec5.append(f"5) 사용철근량 : Asuse = {self.as_use:.1f} mm², 철근도심 : do = {self.d_eff:.1f}mm, [ 사용율 = {usage_ratio:.3f} ]")
        sec5.append(f"   1단 : D {self.as_dia1} - {self.as_num1} EA (= {self.as_use1*self.as_num1:.1f} mm², do1 = {self.dc_1:.1f} mm)")
        sec5.append(f"   2단 : D {self.as_dia2} - {self.as_num2} EA (= {self.as_use2*self.as_num2:.1f} mm², do2 = {self.dc_2:.1f} mm)")
        sec5.append(f"   3단 : D {self.as_dia3} - {self.as_num3} EA (= {self.as_use3*self.as_num3:.1f} mm², do3 = {self.dc_3:.1f} mm)")

        # 6) 철근비 검토
        sec6 = []
        sec6.append("6) 철근비 검토")
        sec6.append(f"   ρmin : 1.4 / fy          = {self.lo_min_1:.6f}")
        sec6.append(f"          0.25 x √fck / fy  = {self.lo_min_2:.6f}, ρmin = {self.lo_min:.6f} 적용")
        sec6.append(f"   ρmax = 0.75 x ρb = 0.75 x (0.85 x β1 x fck / fy) x (6000 / (6000 + fy)) = {self.lo_max:.6f}")
        sec6.append(f"   ρuse = As / ( b x d ) = {self.lo_use:.6f}")
        
        check_msg = ""
        if self.lo_use >= self.lo_min:
            if self.lo_use <= self.lo_max:
                check_msg = "ρmax ≥ ρuse ≥ ρmin --> 최소철근비, 최대철근비 만족   ∴ O.K"
            else:
                check_msg = "ρmax < ρuse ≥ ρmin --> 최소철근비 만족, 최대철근비 불만족   ∴ N.G"
        else:
            if self.lo_use >= self.lo_min_3:
                check_msg = f"ρuse < ρmin 이나, ρuse ≥ 4/3 x ρreq ({self.lo_min_3:.6f}) 만족   ∴ O.K"
            else:
                check_msg = f"ρuse < ρmin 이며, ρuse < 4/3 x ρreq ({self.lo_min_3:.6f}) 불만족   ∴ N.G"
        sec6.append(f"   {check_msg}")

        # 7) 설계 휨강도 산정
        sec7 = []
        sec7.append("7) 설계 휨강도 산정")
        sec7.append(f"   a = As x fy / (0.85 x fck x b) = {self.a:.3f} mm")
        sec7.append(f"   Ø Mn = Øf x As x fy x (d - a / 2)")
        sec7.append(f"        = {self.pi_f_r:.2f} x {self.as_use:.1f} x {self.f_y} x ({self.d_eff:.1f} - {self.a:.3f} / 2)")
        res_f = "O.K" if self.M_r >= self.Mu_nm else "N.G"
        sf = self.M_sf
        sec7.append(f"        = {self.M_r:.1f} N.mm ───> {res_f} (Mu = {self.Mu_nm:.1f} N.mm) [S.F = {sf:.3f}]")

        # Combined Flexure (for total or tab)
        flexure_all = []
        flexure_all.append("=" * 75)
        flexure_all.append(f"{'강도설계법(USD)에 의한 휨모멘트 검토':^75}")
        flexure_all.append("=" * 75)
        flexure_all.append("")
        flexure_all.extend(sec1); flexure_all.append("")
        flexure_all.extend(sec2); flexure_all.append("")
        flexure_all.extend(sec3); flexure_all.append("")
        flexure_all.extend(sec4); flexure_all.append("")
        flexure_all.extend(sec5); flexure_all.append("")
        flexure_all.extend(sec6); flexure_all.append("")
        flexure_all.extend(sec7)

        # 8) 전단력 검토
        shear = []
        shear.append("=" * 75)
        shear.append(f"{'전단력 검토':^75}")
        shear.append("=" * 75)
        shear.append("")
        shear.append(f"Φ Vc = Φv x √fck x b x d / 6")
        shear.append(f"    = {self.pi_v:.2f} x √{self.f_ck} x {self.beam_b} x {self.d_eff_v:.1f} / 6 = {self.pi_V_c:.1f} N")
        if self.pi_V_c >= self.Vu_n:
            shear.append(f"Φ Vc ≥ Vu = {self.Vu_n:.1f} N  ∴ 전단보강 불필요")
        else:
            shear.append(f"Φ Vc < Vu = {self.Vu_n:.1f} N  ∴ 전단보강 필요")
            shear.append(f"Av_req = {self.av_req:.3f} mm²")
            shear.append(f"Av_use = {self.av_use:.3f} mm² (D{self.av_dia}, {self.av_leg}EA, @{self.av_space})")
            res_v = "O.K" if self.pi_V_n >= self.Vu_n else "N.G"
            shear.append(f"Φ Vn = {self.pi_V_n:.1f} N ───> {res_v} (Vu = {self.Vu_n:.1f} N)")

        # 9) 사용성(균열) 검토 (이미지 템플릿 기반 상세 버전)
        service = []
        service.append("=" * 75)
        service.append(f"{'사용성(균열) 검토':^75}")
        service.append("=" * 75)
        service.append("")
        service.append("11) 균열검토")
        service.append("  ① 응력 산정")
        service.append(f"    fs = M / [As x (d - \u03c7/3)] = {self.Ms_nm:.1f} / [ {self.as_use:.3f} x ( {self.d_eff:.3f} - {self.chi_o:.2f} / 3 )]")
        service.append(f"       = {self.f_s:.3f} MPa")
        service.append(f"    \u03c7 = -n x As / b + n x As / b x \u221a [ 1 + 2 x b x d / ( n x As ) ]")
        service.append(f"      = -{self.nr:.1f} x {self.as_use:.1f} / {self.beam_b} + {self.nr:.1f} x {self.as_use:.1f} / {self.beam_b} x \u221a [1 + 2 x {self.beam_b} x {self.d_eff:.3f} / ({self.nr:.1f} x {self.as_use:.1f})]")
        service.append(f"      = {self.chi_o:.3f} mm")
        service.append(f"    사용철근량 = {self.as_use:.3f} mm\u00b2  (최외단 철근도심 : {self.dc_1:.1f} mm)")
        service.append(f"      1단 : D {self.as_dia1} - {self.as_num1} EA, 2단 : D {self.as_dia2} - {self.as_num2} EA, 3단 : D {self.as_dia3} - {self.as_num3} EA )")
        service.append("")
        service.append("  \u2461 철근의 최대 중심간격")
        service.append(f"    강재의 부식에 대한 환경조건은 \u300e {self.cr_index} \u300f 적용")
        service.append(f"    Cc = {self.dc_1:.1f} - {self.as_dia1} / 2 = {self.c_c:.2f} mm")
        service.append("    여기서 Cc ; 인장철근이나 긴장재의 표면과 콘크리트 표면사이의 두께(mm)")
        service.append("")
        service.append(f"    Smin : 375 x (Kcr / fs) - 2.5 x Cc = 375 x ({self.k_cr} / {self.f_s:.3f}) - 2.5 x {self.c_c:.3f} = {self.s_min_1:.3f} mm")
        service.append(f"           300 x (Kcr / fs) = 300 x ({self.k_cr} / {self.f_s:.3f}) = {self.s_min_2:.3f} mm")
        service.append(f"    여기서 Kcr = {self.k_cr} ( 철근 간격을 통한 균열 검증에서 철근의 노출 조건을 고려한 계수 )")
        service.append(f"    \u2234 Sa는 작은 값인 {self.s_min:.3f} mm 를 적용")
        res_s = "O.K" if self.s_min >= self.s_use else "N.G"
        service.append(f"    Sa = {self.s_min:.3f} mm  \u2265 suse = {self.s_use:.3f} mm  \u2234 {res_s}")

        total = []
        total.extend(flexure_all)
        total.append(""); total.append("")
        total.extend(shear)
        total.append(""); total.append("")
        total.extend(service)

        return {
            "total": "\n".join(total),
            "flexure": "\n".join(flexure_all),
            "shear": "\n".join(shear),
            "service": "\n".join(service)
        }

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())
        mode = input_data.get("mode", "calc") # 'calc', 'export', or 'report'
        material = input_data.get("material", {})
        
        if mode == "export":
            # Export mode: generate a single excel with multiple sheets
            from openpyxl import Workbook
            import os
            import tempfile
            
            wb = Workbook()
            # Remove default sheet
            wb.remove(wb.active)
            
            for i, row in enumerate(input_data.get("rows", [])):
                calc = CalcReinfoeceConcrete({"material": material, "row": row})
                sheet_name = row.get('name') if row.get('name') else f"Beam_{row.get('id', i+1)}"
                # Sheet names are limited to 31 chars
                calc.add_to_excel_workbook(wb, sheet_name[:31])
            
            temp_dir = tempfile.gettempdir()
            out_path = os.path.join(temp_dir, "Calc_As_Output.xlsx")
            wb.save(out_path)
            wb.close()
            print(json.dumps({"success": True, "file": out_path}))
        elif mode == "report":
            # Report mode: generate text for a single row
            rows = input_data.get("rows", [])
            if not rows:
                print(json.dumps({"error": "No rows provided"}))
            else:
                calc = CalcReinfoeceConcrete({"material": material, "row": rows[0]})
                print(json.dumps(calc.generate_text_report()))
        else:
            # Standard calculation mode
            results = []
            for row in input_data.get("rows", []):
                calc = CalcReinfoeceConcrete({"material": material, "row": row})
                results.append(calc.calculate())
            print(json.dumps(results))
            
    except Exception as e:
        print(json.dumps([{"error": str(e)}]))
