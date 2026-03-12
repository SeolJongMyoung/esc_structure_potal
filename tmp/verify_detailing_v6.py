import sys
import os
import math

# Add the scripts directory to path
sys.path.append(os.path.abspath('scripts'))

try:
    from core.rc_section_analyzer import RCSectionAnalyzer
    from reports.text_builder import TextReportBuilder
    from standards.lsd_2015 import LSD2015
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

def verify_detailing():
    print("Testing LSD 2015 with Refined Detailing Report...")
    
    # Sample data
    row = {
        "fck": 30, "fy": 400, "b": 1000, "h": 500,
        "as_dia1": 25, "as_num1": 8, "dc_1": 100,
        "as_dia2": 0, "as_num2": 0, "dc_2": 0,
        "as_dia3": 0, "as_num3": 0, "dc_3": 0,
        "Mu": 500, "Vu": 100, "Ms": 300,
        "method": "LSD",
        "crack_case": "일반환경"
    }

    std = LSD2015()
    ana = RCSectionAnalyzer(row, std)
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
    
    # Check for new reinforcement check format
    if "As_max" in total_text and "As_min" in total_text:
        print("  => As_max/As_min check in report: OK")
    else:
        print("  => As_max/As_min check in report: NOT FOUND")
        
    # Check for spacing check
    if "철근 간격검토" in total_text and "s_max = min( 2h, 250 )" in total_text:
        print("  => Spacing check in report: OK")
    else:
        print("  => Spacing check in report: NOT FOUND")

    print("\n[ExcelReportBuilder Verification]")
    print("  (Manual verification required for Excel layout, but offsets are logically set)")

if __name__ == "__main__":
    verify_detailing()
