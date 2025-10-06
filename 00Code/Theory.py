from astropy.io import fits
from astropy.wcs import WCS
import astropy.units as u
from datetime import datetime, timezone
import cv2

def ut_to_gmst(dt_utc):
    
    if dt_utc.tzinfo != timezone.utc:
        raise ValueError("Input datetime must be timezone-aware and in UTC.")

    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day
    hour = dt_utc.hour
    minute = dt_utc.minute
    second = dt_utc.second + dt_utc.microsecond/1e6

    #print(year, month, day, hour, minute, second)
    
    if month <= 2:
        year -= 1
        month += 12
    
    A = year // 100
    B = 2 - A + (A // 4)
    
    JD_day = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    
    # Fractional day in UT
    day_fraction = (hour + minute/60 + second/3600) / 24.0
    
    JD = JD_day + day_fraction
    
    # Julian centuries since J2000.0
    T = (JD - 2451545.0) / 36525.0
    
    # GMST in seconds using IAU 1982 formula
    GMST_sec = 67310.54841 + (876600*3600 + 8640184.812866)*T + 0.093104*(T**2) - 6.2e-6*(T**3)
    
    # Normalize GMST_sec to [0,86400) seconds (one sidereal day)
    GMST_sec = GMST_sec % 86400.0
    
    # Convert to hours
    gmst_hours = GMST_sec / 3600.0
    
    return gmst_hours % 24

def gmst_time(ut_time):

# 拆開成日期和時間
    pre, date_part, time_part, suf = ut_time.split(" ")

# 把 "_" 換成 "-" 或 ":"
    date_part = date_part.split("/")
    time_part = time_part.split(":")

    suf = suf.strip().upper()
    
    if suf == f"PM" or suf == f"PM.":
        time_part[0] = 12 + int(time_part[0])
    else:
        print("failed")

# 組合起來
    dt = datetime(int(date_part[2]), int(date_part[0]), int(date_part[1]), int(time_part[0]), int(time_part[1]), int(time_part[2]), tzinfo=timezone.utc)
    gmst = ut_to_gmst(dt)

    #print(f"GMST:{gmst}hr")

    return gmst

def theory_skycoord(ut_time):

    latitude = 23.469447       
    longitude = 120.872624
    time = gmst_time(ut_time)

    Dec = latitude
    Ra = (time + longitude/15)%24 #hour

    Ra *= 15 #degree

    return Ra, Dec

def find_theo_center(n, ut_time, croplength, x_shift, y_shift, img):

    st_ra, st_dec = theory_skycoord(ut_time)

    # Open the FITS file with WCS header
    hdulist = fits.open(f'/home/user/StartrackPC/04.2 Wcs/cropped{n+1}.new')  # This should have the WCS solution
    w = WCS(hdulist[0].header)

    cm_x = 0
    cm_y = 0
    dist = 114514.0
    # Specify pixel coordinate (X, Y) -- remember, FITS uses 1-based indexing!
    for x in range(croplength):
        for y in range(croplength):

           x_pixel = int(x)
           y_pixel = int(y)
    # Convert pixel to sky (RA, DEC)
    
           ra, dec = w.wcs_pix2world(x_pixel, y_pixel, 1)  # '1' means 1-based index

           d = (ra - st_ra)**2 + (dec - st_dec)**2

           if(d < dist):
                dist = d
                cm_x = x_pixel
                cm_y = y_pixel
    
    
            

    Ra, Dec = w.wcs_pix2world(cm_x, cm_y, 1)
    Ra1, Dec1 = w.wcs_pix2world(cm_x+1, cm_y, 1)
    Ra2, Dec2 = w.wcs_pix2world(cm_x, cm_y+1, 1)

    vecC = (st_ra - Ra, st_dec - Dec)
    vecA = (Ra1 - Ra, Dec1 - Dec)
    vecB = (Ra2 - Ra, Dec2 - Dec)

    #print(f"A:{vecA}, B:{vecB}, C:{vecC}")

    i = (vecA[0]*vecC[0]+vecA[1]*vecC[1])/(pow(vecA[0], 2)+pow(vecA[1], 2))
    j = (vecB[0]*vecC[0]+vecB[1]*vecC[1])/(pow(vecB[0], 2)+pow(vecB[1], 2))

    #print(f"i:{i}, j:{j}")

    print("Theory :")
    print(f"standard:({st_ra}, {st_dec})")
    print(f"calculated:({Ra+i*vecA[0]+j*vecB[0]}, {Dec+i*vecA[1]+j*vecB[1]})")
    print(f"center:({cm_x+i+x_shift}, {cm_y+j+y_shift})")

    cv2.circle(img, (round(cm_x+i+x_shift), round(cm_y+j+y_shift)), 2, (0, 0, 255), 3)
    cv2.imwrite(f"/home/user/StartrackPC/05 Result/result{n+1}.jpg", img)

    return cm_x+i+x_shift, cm_y+j+y_shift

