import os
import glob
from astropy.io import fits


dir_name = os.path.dirname(__file__)
modules_path = os.path.join(dir_name,"*.py")
modules = glob.glob(modules_path)


__all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]

def get_all_modules():
    return __all__

basic_header = fits.PrimaryHDU().header


if __name__=="__main__":
    print(get_all_modules())