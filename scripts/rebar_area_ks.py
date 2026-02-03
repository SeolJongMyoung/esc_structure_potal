import math

class KoreanRebar:
    def __init__(self):
        # KS D 3504 standard rebar areas (mm2)
        self.rebar_data = {
            10: 71.33,
            13: 126.7,
            16: 198.6,
            19: 286.5,
            22: 387.1,
            25: 506.7,
            29: 642.4,
            32: 794.2,
            35: 956.6,
            38: 1140,
            41: 1340,
            51: 2026
        }

    def get_area(self, diameter):
        # diameter can be int or string like "D13" or "H13"
        if isinstance(diameter, str):
            # Extract numbers if it starts with D or H
            d_str = ''.join(filter(str.isdigit, diameter))
            if d_str:
                d = int(d_str)
            else:
                return 0
        else:
            d = int(diameter)
            
        return self.rebar_data.get(d, (math.pi * d**2) / 4.0)

if __name__ == "__main__":
    rebar = KoreanRebar()
    print(f"D13 area: {rebar.get_area(13)}")
    print(f"D25 area: {rebar.get_area('D25')}")
