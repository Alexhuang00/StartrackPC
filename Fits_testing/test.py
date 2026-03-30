from astropy.io import fits

hdul = fits.open("cropped_center.new")
print(len(hdul))   # 查看有多少個 HDU
hdul.info()