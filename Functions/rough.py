from Functions.extract_from_fits import extract_from_fits
from sunpy.map import Map as sm


file1 = "./data/Fido/AIA/171/aia.lev1_euv_12s.2024-02-22T200247Z.171.image.fits"
file2 = "./data/Fido/AIA/171/aia.lev1_euv_12s.2024-02-22T200223Z.171.image.fits"
file3 = "./data/Fido/AIA/171/aia.lev1_euv_12s.2024-02-22T200023Z.193.image.fits"
file4 = "./data/Fido/AIA/171/aia.lev1_euv_12s.2024-02-22T195959Z.211.image.fits"
file5 = "./data/Fido/hmi1/hmi.m_45s.20240222_200300_TAI.2.magnetogram.fits"

m = sm(file4)
m1 = sm(file5)
m1 = m1.rotate(order=3)
# m.quicklook()
m1.quicklook()
# m1.peek()

