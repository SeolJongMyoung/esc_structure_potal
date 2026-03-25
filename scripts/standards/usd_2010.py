from .base_standard import BaseDesignStandard

class USD2010(BaseDesignStandard):
    @property
    def name(self):
        return "강도설계법(도로교 설계기준, 2010)"

    def get_phi_f(self, epsilon_t, epsilon_y):
        if epsilon_t >= 0.005:
            return 0.85, "인장지배단면"
        elif epsilon_t <= epsilon_y:
            return 0.65, "압축지배단면"
        else:
            phi = 0.65 + (0.85 - 0.65) * (epsilon_t - epsilon_y) / (0.005 - epsilon_y)
            return phi, "변화구역단면"
    def get_phi_v(self):
        return 0.8

    def get_beta_1(self, f_ck):
        return super().get_beta_1(f_ck)

    def get_k_cr(self, crack_case):
        return super().get_k_cr(crack_case)
