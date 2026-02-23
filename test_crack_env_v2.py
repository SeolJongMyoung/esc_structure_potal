import json
import subprocess

material = {"fck": 35, "fy": 400}
cases = ["건조한 환경", "일반환경", "부식성 환경", "극심한 부식성 환경"]
row_template = {"id": 1, "name": "Test", "Mu": 1000, "Vu": 50, "Ms": 80, "H": 800, "B": 1000, "Dc": 80, "as_dia": 25, "as_num": 8, "av_dia": 16, "av_leg": 2, "av_space": 400}

for case in cases:
    row = row_template.copy()
    row["crack_case"] = case
    input_data = {"mode": "report", "material": material, "rows": [row]}
    
    process = subprocess.Popen(['python', 'scripts/rc_beam_calc.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=json.dumps(input_data))
    
    if stderr:
        print(f"Error in {case}: {stderr}")
        continue
    
    try:
        result = json.loads(stdout)
        service_report = result.get("service", "")
        # Look for the environment line and Kcr line
        lines = service_report.split('\n')
        env_line = next((l.strip() for l in lines if "환경조건은" in l), "Not found")
        kcr_line = next((l.strip() for l in lines if "Kcr =" in l), "Not found")
        print(f"[{case}] -> {env_line} | {kcr_line}")
    except Exception as e:
        print(f"Failed to parse {case}: {e}")
