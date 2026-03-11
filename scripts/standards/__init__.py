from .usd_2010 import USD2010
from .kds_2021 import KDS2021
from .lsd_2015 import LSD2015
from .lsd_2012 import LSD2012
from .kci_2017 import KCI2017

def get_standard(standard_name):
    if "2021" in standard_name:
        return KDS2021()
    elif "2015" in standard_name:
        return LSD2015()
    elif "2012" in standard_name:
        return LSD2012()
    elif "콘크리트" in standard_name or "KCI" in standard_name:
        return KCI2017()
    else:
        return USD2010()
