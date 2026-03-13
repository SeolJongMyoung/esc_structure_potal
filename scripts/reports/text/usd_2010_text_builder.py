"""
usd_2010_text_builder.py
강도설계법(도로교 설계기준, 2010) 전용 텍스트 보고서 빌더.
철근비 검토는 ρmin/ρmax 간략 방식을 사용한다.
"""
from .base_text_builder import BaseTextBuilder


class USD2010TextBuilder(BaseTextBuilder):
    """강도설계법(도로교 설계기준, 2010) 전용 텍스트 보고서 빌더."""

    def _build_sec6(self):
        """6) 철근비 검토 — USD 2010 간략 방식 (ρmin / ρmax)."""
        ana = self.analyzer
        sec = []
        sec.append("   * 철근비 검토")
        sec.append(f"   \u03c1min : 1.4 / fy          = {ana.lo_min_1:.6f}")
        sec.append(f"          0.25 \u00d7 \u221afck / fy  = {ana.lo_min_2:.6f}, \u03c1min = {ana.lo_min:.6f} 적용")
        sec.append(f"   \u03c1max = 0.75 \u00d7 \u03c1b = {ana.lo_max:.6f}")
        sec.append(f"   \u03c1use = As / ( b \u00d7 d ) = {ana.lo_use:.6f}")

        if ana.lo_use >= ana.lo_min:
            if ana.lo_use <= ana.lo_max:
                check_msg = "\u03c1max \u2265 \u03c1use \u2265 \u03c1min --> 최소철근비, 최대철근비 만족   \u2234 O.K"
            else:
                check_msg = "\u03c1max < \u03c1use \u2265 \u03c1min --> 최소철근비 만족, 최대철근비 초과(NG)   \u2234 N.G"
        else:
            if ana.lo_use >= ana.lo_min_3:
                check_msg = f"\u03c1use < \u03c1min 이나, \u03c1use \u2265 4/3 \u00d7 \u03c1req ({ana.lo_min_3:.6f}) 만족   \u2234 O.K"
            else:
                check_msg = f"\u03c1use < \u03c1min 이며, \u03c1use < 4/3 \u00d7 \u03c1req ({ana.lo_min_3:.6f}) 불만족   \u2234 N.G"
        sec.append(f"   {check_msg}")
        return sec
