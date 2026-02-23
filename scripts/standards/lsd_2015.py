from .base_standard import BaseDesignStandard

class LSD2015(BaseDesignStandard):
    @property
    def name(self):
        return "한계상태설계법(도로교 설계기준, 2015)"

    def get_phi_f(self, epsilon_t, epsilon_y):
        # LSD uses Material Factor (gamma) instead of Phi, 
        # but for compatibility with current structure, we return 1.0 or equivalent.
        return 1.0, "한계상태검토"

    def get_phi_v(self):
        return 1.0

    def get_beta_1(self, f_ck):
        return super().get_beta_1(f_ck)

    def get_k_cr(self, crack_case):
        return super().get_k_cr(crack_case)
