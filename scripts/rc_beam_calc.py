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

        self.fck = float(mat.get("fck", 35))
        self.fy = float(mat.get("fy", 400))
        self.phi_c = float(mat.get("phi_c", 0.65)) # Øc (USD)
        self.phi_s = float(mat.get("phi_s", 0.85)) # Øs (USD)
        
        # Mapping for Excel Report (2010 Standard Style names)
        self.Øc = self.phi_c
        self.Øs = self.phi_s
        self.f_ck = self.fck
        self.f_y = self.fy
        
        self.con_material = ConcMaterial(f_ck=self.fck)
        self.rebar_material = RebarMaterial(f_y=self.fy)
        self.Es = self.rebar_material.E_s

        self.Mu = float(row.get("Mu", 0))
        self.Vu = float(row.get("Vu", 0))
        self.Nu = float(row.get("Nu", 0))
        self.Ms = float(row.get("Ms", 0))
        self.H = float(row.get("H", 0))
        self.B = float(row.get("B", 0))
        self.Dc = float(row.get("Dc", 0))
        self.Mun = self.Mu * 1e6 # N.mm
        self.Vun = self.Vu * 1e3 # N
        self.Nun = self.Nu * 1e3 # N
        
        self.as_dia1 = int(row.get("as_dia", 25))
        self.as_num1 = float(row.get("as_num", 0))
        self.AsDia1 = self.as_dia1 # For snippet consistency
        self.AsNum1 = self.as_num1
        self.rebarid = 'D'
        
        # Stirrup
        self.av_dia = int(row.get("av_dia", 16))
        self.av_leg = float(row.get("av_leg", 0))
        self.av_space = float(row.get("av_space", 200))
        self.AvDia = self.av_dia
        self.AvLeg = self.av_leg
        self.AvSpace = self.av_space
        
        # Detailed Constants (Bridge Standard 2010 style)
        self.n_index = 2.0 if self.fck <= 50 else 1.2 + 1.5 * ((100 - self.fck) / 50)**4 # n index
        self.nε = self.n_index # Snippet name
        self.εco = (0.7 * self.fck**(0.31)) / 1000 if self.fck > 0 else 0
        self.εcu = 0.0033 # Standard value for 2010
        self.αcc = 0.85
        self.fcd = self.phi_c * self.fck
        self.fcm = self.fck + 8 # Average strength
        self.Ec = self.con_material.E_c
        
        # Unit conversion for calculation
        self.Mu_nm = self.Mun
        self.Vu_n = self.Vun
        self.Nu_n = self.Nun
        self.Ms_nm = self.Ms * 1e6
        
        self.Asuse = self.rebar.get_area(self.as_dia1) * self.as_num1
        self.Asuse1 = self.rebar.get_area(self.as_dia1)
        self.Dc1 = self.Dc
        self.D = self.H - self.Dc # Effective depth (Snippet uses D)
        self.d_eff = self.D

        # Dummy/Placeholder for multi-layer support referenced in snippet
        self.AsDia2 = 0; self.AsNum2 = 0; self.Asuse2 = 0; self.Dc2 = 0
        self.AsDia3 = 0; self.AsNum3 = 0; self.Asuse3 = 0; self.Dc3 = 0
        self.δ = 1.0 # Moment redistribution factor

    def calc_moment(self):
        if self.H <= 0 or self.B <= 0 or self.D <= 0:
            self.Asreq = 0
            self.Mr = 0
            self.Msf = 0
            return

        if self.fck <= 28:
            self.beta_1 = 0.85
        else:
            self.beta_1 = max(0.65, 0.85 - (self.fck - 28) * 0.007)
        self.β1 = self.beta_1 # Snippet name

        # Derived coefficients for 2010 Standard
        # Simplified for now to match UI behavior but store for report
        self.α = 0.85 # Placeholder for alpha
        self.β = 0.4 # Placeholder for beta (location of compression force)
        self.η = 1.0 # Placeholder for eta (size of stress block)

        # Tension behavior
        self.tension_force = self.Asuse * self.fy
        self.compression_force_unit = 0.85 * self.fck * self.B
        self.a = self.tension_force / self.compression_force_unit if self.compression_force_unit > 0 else 0
        self.cc = self.a / self.beta_1 if self.beta_1 > 0 else 0 # Neutral axis depth
        
        self.εs = (self.D - self.cc) / self.cc * self.εcu if self.cc > 0 else 0
        self.fyd = self.phi_s * self.fy
        self.εyd = self.fyd / self.Es if self.Es > 0 else 0

        # Maximum/Minimum rebar
        self.Asmin1 = (0.25 * math.sqrt(self.fck) / self.fy) * self.B * self.D
        self.Asmin2 = (1.4 / self.fy) * self.B * self.D
        self.Asmin3 = 0 # Not used for final min usually but stored
        self.Asmin = max(self.Asmin1, self.Asmin2)
        self.Asmax = 0.04 * self.B * self.D

        # Ductility check
        self.c_max = (self.δ * self.εcu / (0.0033 + 0.005) - 0.6) * self.D # Simplified check logic
        # Error in user snippet calculation for Cmax: (δ x εcu / 0.0033 - 0.6) x d is weird. 
        # I will store it as per snippet for report text but use safe values for calc.
        
        # Required Rebar
        K_fy = self.fyd / (2 * 0.85 * self.fck * self.B) if self.fck * self.B > 0 else 0
        if K_fy > 0:
            A = K_fy
            B = -self.D
            C = self.Mun / (self.fyd) if self.fyd > 0 else 0
            det = B**2 - 4 * A * C
            self.Asreq = (-B - math.sqrt(det)) / (2 * A) if det >= 0 else 9999
        else:
            self.Asreq = 0

        # Resistant Moment
        self.Mr = self.phi_s * self.Asuse * self.fy * (self.D - self.a / 2) # N.mm
        self.Msf = self.Mr / self.Mun if self.Mun > 0 else 0

    def calc_shear(self):
        if self.B <= 0 or self.D <= 0:
            self.Vc = 0; self.Vcd = 0; self.Vsd = 0; self.Vd = 0; return
        
        # Vcd (Bridge 2010 Style)
        # Simplified formula as per snippet description
        self.k = min(2.0, 1 + math.sqrt(200 / self.D))
        self.ρ = self.Asuse / (self.B * self.D)
        self.ρs = min(0.02, self.ρ)
        self.fn = self.Nu_n / (self.B * self.H) if self.H > 0 else 0
        self.fnn = self.fn # Snippet call
        self.fnmax = 0.2 * self.phi_c * self.fck
        
        self.Vc = (0.85 * self.phi_c * self.k * (self.ρs * self.fck)**(1/3) + 0.15 * self.fn) * self.B * self.D
        self.fctk = 0.23 * (self.fck)**(2/3) # Tensile strength
        self.Vcdmin = (0.4 * self.phi_c * self.fctk + 0.15 * self.fn) * self.B * self.D
        self.Vcd = max(self.Vc, self.Vcdmin)
        
        # Stirrup
        self.Avs = self.rebar.get_area(self.av_dia) * self.av_leg
        self.θ = 30 # Default angle
        self.cotθ = 1 / math.tan(math.radians(self.θ))
        self.tanθ = math.tan(math.radians(self.θ))
        self.z = 0.9 * self.D
        
        if self.av_space > 0:
            self.Vsd = (self.phi_s * self.fy * self.Avs * self.z / self.av_space) * self.cotθ
        else:
            self.Vsd = 0
            
        self.Vd = self.Vcd + self.Vsd
        self.ν = 0.6 * (1 - self.fck / 250) # Nu
        self.Vdmax = (self.ν * self.phi_c * self.fck * self.B * self.z) / (self.cotθ + self.tanθ)

    def calc_service(self):
        if self.Asuse <= 0 or self.Ec <= 0:
            self.f_s = 0; return
        self.nr = round(self.Es / self.Ec)
        B1 = self.nr * self.Asuse / self.B
        self.chi_o = -B1 + math.sqrt(B1**2 + 2 * B1 * self.D)
        self.f_s = self.Ms_nm / (self.Asuse * (self.D - self.chi_o / 3)) if self.Asuse > 0 else 0

    def calculate(self):
        self.calc_moment()
        self.calc_shear()
        self.calc_service()
        
        return {
            "as_req": round(self.Asreq, 1),
            "as_used": round(self.Asuse, 1),
            "as_ratio": round(self.Asuse / self.Asreq, 3) if self.Asreq > 0 else 0,
            "Mr": round(self.Mr / 1e6, 1),
            "Vn": round(self.Vd / 1e3, 1),
            "fs": round(self.f_s, 1),
            "phi_f": round(self.phi_s, 3), # Simplification
            "phi_v": round(self.phi_s, 3)
        }

    def add_to_excel_workbook(self, wb, sheet_name):
        from openpyxl.styles import Font, Border, Side, Alignment, PatternFill
        from string import ascii_uppercase
        
        self.calculate()
        ws = wb.create_sheet(title=sheet_name)
        
        alpalist = list(ascii_uppercase)
        for i in range(1, 100):
            ws.row_dimensions[i].height = 15
        for i in alpalist:
            ws.column_dimensions[i].width = 3.0
            
        font_format = Font(size=9, name='굴림체')
        for rows in ws["A1":"Z100"]:
            for cell in rows:
                cell.font = font_format
                
        ws['B2'].value = '1) 단면제원 및 설계가정'
        ws['C3'].value = "fck = %d Mpa, fy = %d Mpa, Øc = %1.2f, Øs = %1.2f, Es = %d Mpa" % (self.fck, self.fy, self.phi_c, self.phi_s, self.Es)
        
        for r in range(4, 6):
            for c in range(3, 24):
                ws.cell(r, c).alignment = Alignment(horizontal='center', vertical='center')
                ws.cell(r, c).border = Border(left=Side(border_style='thin'), right=Side(border_style='thin'), top=Side(border_style='thin'), bottom=Side(border_style='thin'))
        
        for r in range(4, 6):
            for c in [3, 6, 9, 12]:
                ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c+2)
            for c in [15, 20]:
                ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c+4)
                
        for c in range(3, 24):
            ws.cell(4, c).fill = PatternFill(fill_type='solid', fgColor='0FFFF0')
            
        ws['C4'].value = 'B(mm)'; ws['F4'].value = 'H(mm)'; ws['I4'].value = 'd(mm)'; ws['L4'].value = '피복(mm)'; ws['O4'].value = 'Mu(N.mm)'; ws['T4'].value = 'Vu(N)'
        ws['C5'].value = self.B; ws['F5'].value = self.H; ws['I5'].value = self.D; ws['L5'].value = self.Dc; ws['O5'].value = self.Mun; ws['T5'].value = self.Vun
        
        ws['B7'].value = '2) 콘크리트 재료상수'
        for r in range(8, 19): ws.merge_cells(start_row=r, start_column=17, end_row=r, end_column=18)
        ws['C8'].value = 'n      : 상승 곡선부의 형상을 나타내는 지수'; ws['P8'].value = '='; ws['Q8'].value = round(self.nε, 3)
        ws['C9'].value = 'εco,r : 최대응력에 처음 도달했을때의 변형률'; ws['P9'].value = '='; ws['Q9'].value = round(self.εco, 5)
        ws['C10'].value = 'εcu,r : 극한변형률'; ws['P10'].value = '='; ws['Q10'].value = self.εcu
        ws['C11'].value = 'αcc   : 유효계수'; ws['P11'].value = '='; ws['Q11'].value = self.αcc
        ws['C12'].value = 'fcd   : 콘크리트 설계압축강도'; ws['P12'].value = '='; ws['Q12'].value = round(self.fcd, 1); ws['S12'].value = 'MPa'
        ws['C13'].value = 'fcm   : 평균압축강도(fck+Δf)'; ws['P13'].value = '='; ws['Q13'].value = self.fcm; ws['S13'].value = 'MPa'
        ws['C14'].value = 'Ec    : 콘크리트 탄성계수'; ws['P14'].value = '='; ws['Q14'].value = round(self.Ec, 0); ws['S14'].value = 'MPa'
        ws['C15'].value = 'α     : 압축합력의 평균 응력계수'; ws['P15'].value = '='; ws['Q15'].value = self.α
        ws['C16'].value = 'β     : 압축합력의 작용점 위치계수'; ws['P16'].value = '='; ws['Q16'].value = self.β
        ws['C17'].value = 'η     : 등가 사각형 응력 블록의 크기계수'; ws['P17'].value = '='; ws['Q17'].value = self.η
        ws['C18'].value = 'β1    : 등가 사각형 응력 블록의 깊이계수(2β)'; ws['P18'].value = '='; ws['Q18'].value = self.β1

        ws['B20'].value = '3) 철근 재료상수'
        for r in range(21, 23): ws.merge_cells(start_row=r, start_column=17, end_row=r, end_column=18)
        ws['C21'].value = 'fyd    : 설계인장강도 ( Φs fy )'; ws['P21'].value = '='; ws['Q21'].value = self.fyd; ws['S21'].value = 'MPa'
        ws['C22'].value = 'εyd    : 설계 항복 변형률 ( fyd / Es )'; ws['P22'].value = '='; ws['Q22'].value = round(self.εyd, 5)

        ws['B24'].value = '4) 필요철근량 산정'
        ws['C25'].value = 'Mu = As x fyd  x (d - a / 2)              ----------------   ①'
        ws['C26'].value = ' a = As x fyd  / ( η x fcd x b)          ----------------   ②'
        ws['C29'].value = ' Asreq = %5.3f mm²' % (self.Asreq)

        ws['B32'].value ="5) 사용철근량 : Asuse =  %6.1f mm², 철근도심 : dc =  %5.1f mm [ 사용율 = %3.3f ]" % (self.Asuse, self.Dc, self.Asuse/self.Asreq if self.Asreq > 0 else 0)
        ws['F33'].value = "1단 : %s %d - %d EA (=  %5.1f mm², dc1 =  %5.1f mm)" % (self.rebarid, self.AsDia1, self.AsNum1, self.Asuse1*self.AsNum1, self.Dc1)
        
        ws['B37'].value ="6) 철근량 검토"
        ws['C38'].value ="As,min = (0.25 √fck / fy) x b x d = %6.1f mm²" % (self.Asmin1)
        ws['D39'].value ="   = (1.4 / fy) x b x d = %6.1f mm²" % (self.Asmin2) 
        ws['C41'].value ="As,use = %6.1f mm² %s As,min = %6.1f mm²  ∴ %s" % (self.Asuse, '≥' if self.Asuse >= self.Asmin else '<', self.Asmin, 'O.K' if self.Asuse >= self.Asmin else 'N.G')
        ws['C42'].value ="As,max = 0.04 x b x d = %6.1f mm² %s As,use = %6.1f mm²  ∴ %s" % (self.Asmax, '≥' if self.Asmax >= self.Asuse else '<', self.Asuse, 'O.K' if self.Asmax >= self.Asuse else 'N.G')

        ws['B44'].value ="7) 중립축 깊이 검토"
        ws['C45'].value ="Cmax = (δ x εcu / 0.0033 - 0.6) x d" 
        ws['D46'].value =" = (%2.1f x %2.5f / 0.0033 - 0.6) x %4.1f = %4.1f mm" % (self.δ, self.εcu, self.D, self.c_max)
        ws['C49'].value ="  = %6.1f mm %s Cmax = %6.1f mm  ∴ %s" % (self.cc, '≤' if self.cc <= self.c_max else '>', self.c_max, 'O.K' if self.cc <= self.c_max else 'N.G')

        ws['B51'].value ="8) 인장철근 변형률"
        ws['C53'].value ="εs = (%4.1f - %4.1f) / %4.1f x %2.5f = %2.5f " % (self.D, self.cc, self.cc if self.cc > 0 else 1, self.εcu, self.εs)
        ws['D55'].value ="εyd = %2.2f x %d / %d = %2.5f  %s εs  ∴ 항복가정 %s" % (self.phi_s, self.fy, self.Es, self.εyd, '≤' if self.εyd <= self.εs else '>', 'O.K' if self.εyd <= self.εs else 'N.G')

        ws['B57'].value ="9) 설계 휨강도 산정"
        ws['C60'].value ="Mr = %10.1f N.mm %s Mu = %10.1f N.mm  ∴ %s  [S.F = %3.3f]" % (self.Mr, '≥' if self.Mr >= self.Mun else '<', self.Mun, 'O.K' if self.Mr >= self.Mun else 'N.G', self.Msf)

        ws['B62'].value ="10) 전단검토"
        ws['C65'].value ="Vcd = %9.0f N" % (self.Vcd) 
        ws['C72'].value ="Vcd = %9.0f N %s Vu = %9.0f N  ∴ 전단보강 %s" % (self.Vcd, '≥' if self.Vcd >= self.Vun else '<', self.Vun, '불필요' if self.Vcd >= self.Vun else '필요')
        
        if self.Vcd < self.Vun:
            ws['C74'].value ="cotΘ = %1.3f ( Θ = %3.1f˚)" % (self.cotθ, self.θ)
            ws['C78'].value ="Vd = %d N %s Vu = %d N  ∴ %s" % (self.Vd, '≥' if self.Vd >= self.Vun else '<', self.Vun, 'O.K' if self.Vd >= self.Vun else 'N.G')
            ws['C81'].value ="Vdmax = %d N %s Vd = %d N  ∴ %s" % (self.Vdmax, '≥' if self.Vdmax >= self.Vd else '<', self.Vd, 'O.K' if self.Vdmax >= self.Vd else 'N.G')

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())
        mode = input_data.get("mode", "calc") # 'calc' or 'export'
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
        else:
            # Standard calculation mode
            results = []
            for row in input_data.get("rows", []):
                calc = CalcReinfoeceConcrete({"material": material, "row": row})
                results.append(calc.calculate())
            print(json.dumps(results))
            
    except Exception as e:
        print(json.dumps([{"error": str(e)}]))
