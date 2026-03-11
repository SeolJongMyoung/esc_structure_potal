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

    def get_concrete_method(self):
        return "LSD"

    def get_material_factors(self):
        return 0.65, 0.90

    def get_flexure_factors(self, f_ck):
        # KDS 14 20 24 : 4.2.1.3 (3) - Equiv. Rectangular Stress Block
        if f_ck <= 50:
            eta = 1.0
            lambda_fac = 0.8
        else:
            eta = 1.0 - (f_ck - 50) / 200
            lambda_fac = 0.8 - (f_ck - 50) / 400
            
        eta = max(0.67, eta)
        lambda_fac = max(0.65, lambda_fac)
        
        # In rectangular block: alpha = eta * lambda, beta = lambda / 2
        return eta * lambda_fac, lambda_fac / 2

    def get_beta_1(self, f_ck):
        return super().get_beta_1(f_ck)

    def get_k_cr(self, crack_case):
        return super().get_k_cr(crack_case)
