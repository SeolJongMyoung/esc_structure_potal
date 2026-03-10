from abc import ABC, abstractmethod
import math

class BaseDesignStandard(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def get_phi_f(self, epsilon_t, epsilon_y):
        """휨 강도감소계수 산정"""
        pass

    @abstractmethod
    def get_phi_v(self):
        """전단 강도감소계수 산정"""
        pass

    def get_beta_1(self, f_ck):
        """등가 사각형 응력 블록 깊이 계수 산정"""
        if f_ck <= 28:
            return 0.85
        else:
            return max(0.65, 0.85 - (f_ck - 28) * 0.007)

    def get_vs_max(self, f_ck, b, d):
        """최대 전단 보강력 산정 (기본: 2/3 * sqrt(fck) * b * d)"""
        return (2.0/3.0) * math.sqrt(f_ck) * b * d

    def get_k_cr(self, crack_case):
        """균열 검토용 Kcr 계수 산정"""
        mapping = {
            "건조한 환경": 250,
            "일반환경": 210,
            "부식성 환경": 170,
            "극심한 부식성 환경": 150
        }
        return mapping.get(crack_case, 210)

    def check_min_rebar(self, calc_data):
        """최소 철근량 검토 (기본 로직)"""
        f_ck = calc_data['f_ck']
        f_y = calc_data['f_y']
        
        lo_min_1 = 1.4 / f_y
        lo_min_2 = 0.25 * math.sqrt(f_ck) / f_y
        lo_min = max(lo_min_1, lo_min_2)
        
        lo_use = calc_data['as_use'] / (calc_data['b'] * calc_data['d'])
        lo_min_3 = (4/3) * (calc_data['as_req'] / (calc_data['b'] * calc_data['d']))
        
        is_ok = (lo_use >= lo_min) or (lo_use >= lo_min_3)
        return {
            "is_ok": is_ok,
            "lo_min": lo_min,
            "lo_min_3": lo_min_3,
            "details": f"ρmin = {lo_min:.6f}, 4/3ρreq = {lo_min_3:.6f}"
        }

    def check_max_rebar(self, calc_data):
        """최대 철근량 검토 (기본 로직)"""
        f_ck = calc_data['f_ck']
        f_y = calc_data['f_y']
        beta_1 = self.get_beta_1(f_ck)
        
        lo_bal = (0.85 * beta_1 * f_ck / f_y) * (6000 / (6000 + f_y))
        lo_max = 0.75 * lo_bal
        lo_use = calc_data['as_use'] / (calc_data['b'] * calc_data['d'])
        
        is_ok = lo_use <= lo_max
        return {
            "is_ok": is_ok,
            "lo_max": lo_max,
            "lo_bal": lo_bal,
            "details": f"ρmax = {lo_max:.6f}"
        }
