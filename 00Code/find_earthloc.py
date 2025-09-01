from astropy.io import fits
from astropy.wcs import WCS
from datetime import datetime, timezone

from Theory import gmst_time


def zenithcoord(x, y, n):

    hdulist = fits.open(f'/home/alex/Startrack/04.2 Wcs/cropped{n+1}.new')  # This should have the WCS solution
    w = WCS(hdulist[0].header)

    O_x = int(x)
    O_y = int(y)

    ra0, dec0 = w.wcs_pix2world(O_x, O_y, 1)
    rax, decx = w.wcs_pix2world(O_x+1, O_y, 1)
    ray, decy = w.wcs_pix2world(O_x, O_y+1, 1)

    vec1ra = (rax - ra0)*(x-int(x))
    vec1dec = (decx - dec0)*(x-int(x))

    vec2ra = (ray - ra0)*(y-int(y))
    vec2dec = (decy - dec0)*(y-int(y))

    zenith = (ra0+vec1ra+vec2ra, dec0+vec1dec+vec2dec)
    return zenith

def zenith_to_earth_location(x, y, n, ut_time):
    
    gmst = gmst_time(ut_time)
    Ra, Dec = zenithcoord(x, y, n)

    


    lat = Dec

    prelon = (Ra/15.0 - gmst) * 15 #+-360

    if prelon <= -180:
        lon = prelon + 360

    elif prelon >= 180:
        lon = prelon - 360

    else:
        lon = prelon

    print(lon, lat)

    return lon, lat

    