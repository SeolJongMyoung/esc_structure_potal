import sys
import os

# Add the scripts directory to path
sys.path.append(os.path.abspath('scripts'))

try:
    from core.rc_section_analyzer import RCSectionAnalyzer
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

def test_lsd_2015():
    print("--- Testing LSD 2015 Logic ---")
    
    # KDS 24 based test case
    f_ck = 30
    f_y = 400
    # LSD 2015 (KDS 24)
    standard_name = "한계상태설계법(도로교 설계기준, 2015)"
    
    data = {
        "H": 800, "B": 1000, "Mu": 500, "Ms": 300, "Vu": 200,
        "dc1": 80, "dia1": 25, "num1": 6,
        "crack_case": "일반환경"
    }
    
    analyzer = RCSectionAnalyzer(f_ck, f_y, standard_name, data["H"], data["B"], data, data, phi_s=0.85)
    analyzer.analyze()
    
    print(f"Standard: {analyzer.standard.name}")
    print(f"Method:   {analyzer.method}")
    print(f"Phi_c:    {analyzer.phi_c}, Phi_s: {analyzer.phi_s}")
    print(f"f_cd:     {analyzer.f_cd} MPa (Expected: {30*0.65})")
    print(f"f_yd:     {analyzer.f_yd} MPa (Expected: {400*0.90})")
    print(f"Alpha:    {analyzer.alpha_fac:.3f}, Beta: {analyzer.beta_fac:.3f}")
    print(f"as_req:   {analyzer.as_req:.1f} mm2")
    print(f"M_r:      {analyzer.M_r/1e6:.1f} kNm")
    
    # Verify USD comparison
    usd_standard = "강도설계법(콘크리트구조 설계기준, 2021)"
    analyzer_usd = RCSectionAnalyzer(f_ck, f_y, usd_standard, data["H"], data["B"], data, data, phi_s=0.85)
    analyzer_usd.analyze()
    print("\n--- Comparison with USD 2021 ---")
    print(f"Standard: {analyzer_usd.standard.name}")
    print(f"Method:   {analyzer_usd.method}")
    print(f"f_cd:     {analyzer_usd.f_cd} MPa (Expected: 30)")
    print(f"f_yd:     {analyzer_usd.f_yd} MPa (Expected: 400)")
    print(f"as_req:   {analyzer_usd.as_req:.1f} mm2")

if __name__ == "__main__":
    test_lsd_2015()
