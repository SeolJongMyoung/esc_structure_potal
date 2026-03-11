import sys
import os

sys.path.append(os.path.abspath('scripts'))

from core.rc_section_analyzer import RCSectionAnalyzer

def test_lsd_2012():
    print("--- Testing LSD 2012 Logic (Sec_back replication) ---")
    f_ck = 30
    f_y = 400
    standard_name = "한계상태설계법(도로교 설계기준, 2012)"
    
    data = {
        "H": 800, "B": 1000, "Mu": 500, "Ms": 300, "Vu": 200,
        "dc1": 80, "dia1": 25, "num1": 6,
        "crack_case": "일반환경",
        "av_dia": 13, "av_leg": 2, "av_space": 200
    }
    
    analyzer = RCSectionAnalyzer(f_ck, f_y, standard_name, data["H"], data["B"], data, data)
    analyzer.analyze()
    
    from reports.text_builder import TextReportBuilder
    builder = TextReportBuilder(analyzer)
    report = builder.generate()
    
    print(report["total"])
    
    if hasattr(analyzer, 'v_theta'):
        print(f"Shear Theta: {analyzer.v_theta:.1f} deg")

if __name__ == "__main__":
    test_lsd_2012()
