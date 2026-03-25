import sys
import json
import os

# Ensure the scripts directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.rc_section_analyzer import RCSectionAnalyzer
from reports.text_builder import TextReportBuilder
from reports.excel_builder import ExcelReportBuilder

if __name__ == "__main__":
    try:
        # Use UTF-8 for stdin/stdout on Windows
        if sys.platform == "win32":
            import io
            sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

        input_data = json.loads(sys.stdin.read())
        mode = input_data.get("mode", "calc") # 'calc', 'export', or 'report'
        material = input_data.get("material", {})
        design_standard = input_data.get("design_standard", "강도설계법(도로교 설계기준, 2010)")
        
        f_ck = material.get("fck", 35)
        f_y = material.get("fy", 400)
        phi_f = material.get("phi_f", 0.85)
        phi_v = material.get("phi_v", 0.8)
        
        if mode == "export":
            # Export mode: generate a single excel with multiple sheets
            from openpyxl import Workbook
            import tempfile
            
            wb = Workbook()
            # Remove default sheet
            wb.remove(wb.active)
            
            for i, row in enumerate(input_data.get("rows", [])):
                beam_h = row.get("H", 0)
                beam_b = row.get("B", 0)
                analyzer = RCSectionAnalyzer(f_ck, f_y, design_standard, beam_h, beam_b, row, row, phi_f=phi_f, phi_v=phi_v)
                analyzer.analyze()
                builder = ExcelReportBuilder(analyzer)
                sheet_name = row.get('name') if row.get('name') else f"Beam_{row.get('id', i+1)}"
                builder.add_to_workbook(wb, sheet_name[:31])
            
            temp_dir = tempfile.gettempdir()
            out_path = os.path.join(temp_dir, "Calc_As_Output.xlsx")
            wb.save(out_path)
            wb.close()
            print(json.dumps({"success": True, "file": out_path}, ensure_ascii=False))
            
        elif mode == "report":
            # Report mode: generate text for a single row
            rows = input_data.get("rows", [])
            if not rows:
                print(json.dumps({"error": "No rows provided"}, ensure_ascii=False))
            else:
                row = rows[0]
                beam_h = row.get("H", 0)
                beam_b = row.get("B", 0)
                analyzer = RCSectionAnalyzer(f_ck, f_y, design_standard, beam_h, beam_b, row, row, phi_f=phi_f, phi_v=phi_v)
                analyzer.analyze()
                builder = TextReportBuilder(analyzer)
                print(json.dumps(builder.generate(), ensure_ascii=False))
                
        else:
            # Standard calculation mode
            results = []
            for row in input_data.get("rows", []):
                beam_h = row.get("H", 0)
                beam_b = row.get("B", 0)
                analyzer = RCSectionAnalyzer(f_ck, f_y, design_standard, beam_h, beam_b, row, row, phi_f=phi_f, phi_v=phi_v)
                analyzer.analyze()
                results.append(analyzer.get_summary_result())
            print(json.dumps(results, ensure_ascii=False))
            
    except Exception as e:
        print(json.dumps([{"error": str(e)}], ensure_ascii=False))
