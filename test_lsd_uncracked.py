
import sys
import os

# Add the scripts directory to path
sys.path.append(os.path.abspath('scripts'))

from core.rc_section_analyzer import RCSectionAnalyzer
from reports.text.lsd_text_builder import LSDTextBuilder

def test_uncracked_lsd():
    print("--- Testing LSD Uncracked Split Case ---")
    
    f_ck = 35
    f_y = 400
    standard_name = "한계상태설계법(도로교 설계기준, 2015)"
    
    loads = {
        "Mu": 1000,
        "Vu": 50,
        "Nu": 0,
        # Uncracked: Z ~ 1.66e8, M1=100kNm -> ft ~ 0.6 < 3.2 OK
        "Ms1": 100, 
        "Ms5": 200
    }
    
    rebar_data = {
        "dc1": 80, "dia1": 25, "num1": 8,
        "dc2": 0, "dia2": 0, "num2": 0,
        "dc3": 0, "dia3": 0, "num3": 0,
        "crack_case": "E",
        "av_dia": 13, "av_leg": 2, "av_space": 200
    }
    
    # H=1000, B=1000
    ana = RCSectionAnalyzer(f_ck, f_y, standard_name, 1000, 1000, loads, rebar_data, phi_f=0.65, phi_v=0.90)
    ana.analyze()
    
    sd = ana.service_details
    print(f"Is Uncracked Flag: {sd.get('is_uncracked')}")
    print(f"ft = {sd.get('ft'):.3f} MPa (Ms1 application)")
    print(f"fctm = {sd.get('fctm'):.3f} MPa")
    print(f"Uncracked Neutral Axis c = {sd.get('c_na'):.3f} mm")
    print(f"Concrete Stress fc = {sd.get('fc'):.3f} MPa (Derived from Ms5)")
    print(f"Steel Stress fs = {sd.get('fs'):.3f} MPa")
    
    assert sd.get('is_uncracked') == True, "Fail: Expected uncracked"
    print("Assertions PASSED.\n")

    # Check Text Report Builder
    builder = LSDTextBuilder(ana)
    report = builder.generate()
    print("--- Text Report Snippet ---")
    lines = report['service'].split('\n')
    for line in lines[:20]:
        print(line)

if __name__ == "__main__":
    test_uncracked_lsd()
