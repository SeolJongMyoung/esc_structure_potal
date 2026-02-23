import json
import subprocess

material = {"fck": 35, "fy": 400}
cases = ["건조한 환경", "일반환경", "부식성 환경", "극심한 부식성 환경"]
row_template = {"id": 1, "Mu": 1000, "Vu": 50, "Ms": 80, "H": 800, "B": 1000, "Dc": 80, "as_dia": 25, "as_num": 8}

for case in cases:
    row = row_template.copy()
    row["crack_case"] = case
    input_data = {"mode": "report", "material": material, "rows": [row]}
    
    process = subprocess.Popen(['python', 'scripts/rc_beam_calc.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=json.dumps(input_data))
    
    if stderr:
        print(f"Error in {case}: {stderr}")
        continue
    
    result = json.loads(stdout)
    service_report = result.get("service", "")
    print(f"--- Case: {case} ---")
    # Search for Kcr in the report
    for line in service_report.split('\n'):
        if "Kcr =" in line:
            print(line.strip())
