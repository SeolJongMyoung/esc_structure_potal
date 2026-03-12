import sys
import os
import math

# Add the scripts directory to path
sys.path.append(os.path.abspath('scripts'))

try:
    from core.rc_section_analyzer import RCSectionAnalyzer
    from reports.text_builder import TextReportBuilder
    from standards import get_standard
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

def verify_detailing():
    print("Testing LSD 2015 with Refined Detailing Report...")
    
    f_ck = 30
    f_y = 400
    standard_name = "한계상태설계법(도로교 설계기준, 2015)"
    beam_h = 500
    beam_b = 1000
    loads = {"Mu": 500, "Vu": 100, "Ms": 300}
    rebar_data = {"dia1": 25, "num1": 8, "dc1": 100}
    phi_f = 0.65
    phi_v = 0.9

    std = get_standard(standard_name)
    ana = RCSectionAnalyzer(f_ck, f_y, standard_name, beam_h, beam_b, loads, rebar_data, phi_f, phi_v)
    ana.analyze()

    print(f"\n[RCSectionAnalyzer Check]")
    print(f"  s_use: {ana.s_use:.1f} mm")
    print(f"  s_detailing_max: {ana.s_detailing_max:.1f} mm (expected: min(2*500, 250) = 250)")
    print(f"  s_detailing_ok: {ana.s_detailing_ok}")
    
    if abs(ana.s_detailing_max - 250) < 0.1:
        print("  => s_detailing_max calculation: OK")
    else:
        print("  => s_detailing_max calculation: FAILED")

    print(f"\n[TextReportBuilder Check]")
    builder = TextReportBuilder(ana, std)
    report = builder.build()
    
    total_text = report["total"]
    
    # Check for new reinforcement check format (using simplified string match)
    if "As_max" in total_text and "As_min" in total_text:
        print("  => As_max/As_min check in report: OK")
    else:
        print("  => As_max/As_min check in report: NOT FOUND")
        
    # Check for spacing check - search for parts of the strings
    if "철근 간격검토" in total_text and "s_max = min( 2h, 250 )" in total_text:
        print("  => Spacing check in report: OK")
    else:
        print("  => Spacing check in report: NOT FOUND")

if __name__ == "__main__":
    verify_detailing()
