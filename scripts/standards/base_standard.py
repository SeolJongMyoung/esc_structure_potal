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

    @abstractmethod
    def get_beta_1(self, f_ck):
        """등가 사각형 응력 블록 깊이 계수 산정"""
        if f_ck <= 28:
            return 0.85
        else:
            return max(0.65, 0.85 - (f_ck - 28) * 0.007)

    @abstractmethod
    def get_k_cr(self, crack_case):
        """균열 검토용 Kcr 계수 산정"""
        mapping = {
            "건조한 환경": 250,
            "일반환경": 210,
            "부식성 환경": 170,
            "극심한 부식성 환경": 150
        }
        return mapping.get(crack_case, 210)
