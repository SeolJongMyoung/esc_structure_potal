
import sys
import os

# Add the scripts directory to path to import the module
sys.path.append(os.path.abspath('scripts'))

try:
    from rc_beam_calc import CalcReinfoeceConcrete
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

def test_s_use():
    print("--- Testing s_use logic ---")
    
    # Case 1: Same cover (dc1=80, dc2=80) 
    # expected: eff_num = num1 + num2 = 4 + 4 = 8
    # s_use = 1000 / 8 = 125.0
    data_same_cover = {
        "material": {"fck": 35, "fy": 400},
        "design_standard": "강도설계법(도로교 설계기준, 2010)",
        "row": {
            "B": 1000, "H": 800, "Mu": 500, "Ms": 300,
            "dc1": 80, "dia1": 25, "num1": 4,
            "dc2": 80, "dia2": 25, "num2": 4,
            "dc3": 0, "dia3": 13, "num3": 0,
            "crack_case": "일반환경"
        }
    }
    
    calc1 = CalcReinfoeceConcrete(data_same_cover)
    calc1.calc_service()
    print(f"Case 1 (dc1=80, dc2=80, dc3=0):")
    print(f"  Expected s_use: 125.0")
    print(f"  Result s_use:   {calc1.s_use}")

    # Case 2: Different cover (dc1=80, dc2=150)
    # expected: eff_num = num1 = 4
    # s_use = 1000 / 4 = 250.0
    data_diff_cover = {
        "material": {"fck": 35, "fy": 400},
        "design_standard": "강도설계법(도로교 설계기준, 2010)",
        "row": {
            "B": 1000, "H": 800, "Mu": 500, "Ms": 300,
            "dc1": 80, "dia1": 25, "num1": 4,
            "dc2": 150, "dia2": 25, "num2": 4,
            "dc3": 0, "dia3": 13, "num3": 0,
            "crack_case": "일반환경"
        }
    }
    
    calc2 = CalcReinfoeceConcrete(data_diff_cover)
    calc2.calc_service()
    print(f"Case 2 (dc1=80, dc2=150, dc3=0):")
    print(f"  Expected s_use: 250.0")
    print(f"  Result s_use:   {calc2.s_use}")

if __name__ == "__main__":
    test_s_use()
