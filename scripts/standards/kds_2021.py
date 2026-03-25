from .kci_2017 import KCI2017

class KDS2021(KCI2017):
    @property
    def name(self):
        return "강도설계법(콘크리트구조 설계기준, 2021)"

    def get_phi_f(self, epsilon_t, epsilon_y):
        # KDS 2021 uses different limits sometimes, for now keeping similar to USD 2010
        if epsilon_t >= 0.005:
            return 0.85, "인장지배단면"
        elif epsilon_t <= epsilon_y:
            return 0.70, "압축지배단면" # Often 0.70 in KDS for tied columns
        else:
            phi = 0.70 + (0.85 - 0.70) * (epsilon_t - epsilon_y) / (0.005 - epsilon_y)
            return phi, "변화구역단면"
    def get_phi_v(self):
        return 0.8

    def get_beta_1(self, f_ck):
        return super().get_beta_1(f_ck)

    def get_k_cr(self, crack_case):
        # Kcr values might differ in KDS 2021
        return super().get_k_cr(crack_case)
