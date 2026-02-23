from .usd_2010 import USD2010
from .kds_2021 import KDS2021
from .lsd_2015 import LSD2015

def get_standard(standard_name):
    if "2021" in standard_name:
        return KDS2021()
    elif "2015" in standard_name:
        return LSD2015()
    else:
        return USD2010()
