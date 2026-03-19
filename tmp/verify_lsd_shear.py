
import sys
import os
import json

# Ensure scripts directory is in path
project_root = r"c:\Gemina_code\esc_structure_potal"
sys.path.append(os.path.join(project_root, 'scripts'))

from core.rc_section_analyzer import RCSectionAnalyzer
from reports.text.lsd_text_builder import LSDTextBuilder

def test_lsd_shear_hiding():
    # Case 1: Shear reinforcement NOT needed (Vu <= Vcd)
    f_ck, f_y = 35.0, 400.0
    std_name = "한계상태설계법(도로교 설계기준, 2015)"
    beam_h, beam_b = 800.0, 1000.0
    loads = {"Mu": 100.0, "Vu": 50.0, "Nu": 0.0, "Ms": 80.0} # Low Vu
    rebar_data = {"dc1": 80.0, "dia1": 25, "num1": 8.0, "av_dia": 10, "av_leg": 2.0, "av_space": 200.0}
    
    analyzer_low = RCSectionAnalyzer(f_ck, f_y, std_name, beam_h, beam_b, loads, rebar_data)
    analyzer_low.analyze()
    
    builder_low = LSDTextBuilder(analyzer_low)
    report_low = builder_low.generate()
    
    print("--- Testing Low Shear (Vu <= Vcd) ---")
    print(f"Vu: {analyzer_low.Vu_n/1e3:.1f} kN, Vcd: {analyzer_low.pi_V_c/1e3:.1f} kN")
    if "* 전단철근량 검토" in report_low["total"]:
        print("FAIL: '* 전단철근량 검토' should NOT be in report")
    else:
        print("PASS: '* 전단철근량 검토' is hidden")
        
    # Case 2: Shear reinforcement IS needed (Vu > Vcd)
    loads_high = {"Mu": 100.0, "Vu": 1000.0, "Nu": 0.0, "Ms": 80.0} # High Vu
    analyzer_high = RCSectionAnalyzer(f_ck, f_y, std_name, beam_h, beam_b, loads_high, rebar_data)
    analyzer_high.analyze()
    
    builder_high = LSDTextBuilder(analyzer_high)
    report_high = builder_high.generate()
    
    print("\n--- Testing High Shear (Vu > Vcd) ---")
    print(f"Vu: {analyzer_high.Vu_n/1e3:.1f} kN, Vcd: {analyzer_high.pi_V_c/1e3:.1f} kN")
    if "* 전단철근량 검토" in report_high["total"]:
        print("PASS: '* 전단철근량 검토' is present")
    else:
        print("FAIL: '* 전단철근량 검토' should be in report")

if __name__ == "__main__":
    test_lsd_shear_hiding()
