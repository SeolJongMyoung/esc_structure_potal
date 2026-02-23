import json
import subprocess
import os

material = {"fck": 35, "fy": 400}
row = {"id": 1, "name": "StandardTest", "Mu": 1000, "Vu": 50, "Ms": 80, "H": 800, "B": 1000, "Dc": 80, "as_dia": 25, "as_num": 8, "av_dia": 16, "av_leg": 2, "av_space": 400, "crack_case": "일반환경"}
standards = [
    "강도설계법(도로교 설계기준, 2010)",
    "강도설계법(콘크리트구조 설계기준, 2021)",
    "한계상태설계법(도로교 설계기준, 2015)"
]

print("--- Multi-Standard Verification ---")
for std in standards:
    input_data = {
        "mode": "report",
        "design_standard": std,
        "material": material,
        "rows": [row]
    }
    
    # Ensure standards package is found (it's in the same scripts dir)
    process = subprocess.Popen(['python', 'scripts/rc_beam_calc.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    stdout, stderr = process.communicate(input=json.dumps(input_data, ensure_ascii=False))
    
    if stderr:
        print(f"[{std}] Error: {stderr}")
        continue
        
    try:
        report = json.loads(stdout)
        service_text = report.get("service", "")
        # Check if the standard name is in the output header
        if std in service_text:
            print(f"[{std}] OK: Standard name found in report.")
        else:
            print(f"[{std}] FAILED: Standard name NOT found in report.")
            # print(service_text[:200]) # Debug
    except Exception as e:
        print(f"[{std}] Failed to parse: {e}")
