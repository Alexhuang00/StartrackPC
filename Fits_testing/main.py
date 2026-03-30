from astropy.io import fits
import numpy as np
import cv2
from astropy.wcs import WCS

# --- Step 1: Load FITS ---
hdul = fits.open("image_20250716_01_01_34_00.fits")
data = hdul[0].data

print(f"影像維度：{data.shape}")
    
    
for i in range(10, 11):
    threshold = i
    mask = data > threshold

    #for i in range(1400, 1410, 1):
        #for j in range(1400, 1405, 1):
            #print(mask[i][j],end=' ')
        
        #print()

    thres = np.where(mask, 255, 0).astype(np.uint8)

    contours, _ = cv2.findContours(thres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)

    (xc, yc), radius = cv2.minEnclosingCircle(largest_contour)

    print(f"Circle center: ({xc:.2f}, {yc:.2f}), radius: {radius:.2f}")
    # --- Step 2: Compute the image center ---

    x_center = int(xc)
    y_center = int(yc)

    # --- Step 3: Define crop size ---
    crop_size = 300  # e.g. 200x200 pixels
    x_min = x_center - crop_size // 2
    x_max = x_center + crop_size // 2
    y_min = y_center - crop_size // 2
    y_max = y_center + crop_size // 2

    # --- Step 4: Crop and save ---
    cropped_data = data[int(y_min):int(y_max), int(x_min):int(x_max)]

    fits.writeto("cropped_center.fits", cropped_data, hdul[0].header, overwrite=True)

    print(f"✅ Cropped to center ({x_center}, {y_center}) — saved as cropped_center.fits")

    import matplotlib.pyplot as plt
    
    plt.clf()
    
    thres_color = cv2.cvtColor(thres, cv2.COLOR_GRAY2BGR)

    # Draw all contours in green
    #cv2.drawContours(thres_color, contours, -1, (0, 255, 0), 1)

    # Draw the largest contour in red
    cv2.drawContours(thres_color, [largest_contour], -1, (0, 0, 255), 2)

    # Show result using Matplotlib
    plt.imshow(cv2.cvtColor(thres_color, cv2.COLOR_BGR2RGB), origin='lower')
    circle_plot = plt.Circle((xc, yc), radius, color='red', fill=False, lw=2)
    plt.gca().add_patch(circle_plot)
    
    

import subprocess

subprocess.run(["cp", "cropped_center.fits", "/home/user/astrometry.net-0.97/demo/"], check=True)

cmd = (
    "source /home/user/anaconda3/bin/activate && "
    "conda activate StarTracker && "
    f"solve-field /home/user/astrometry.net-0.97/demo/cropped_center.fits --overwrite"
)

subprocess.run(["bash", "-c", cmd], check=True)
subprocess.run(["cp", f"/home/user/astrometry.net-0.97/demo/cropped_center-objs.png", f"/home/user/StartrackPC/Fits_testing/"])
subprocess.run(["cp", f"/home/user/astrometry.net-0.97/demo/cropped_center-indx.png", f"/home/user/StartrackPC/Fits_testing/"])
subprocess.run(["cp", f"/home/user/astrometry.net-0.97/demo/cropped_center-ngc.png", f"/home/user/StartrackPC/Fits_testing/"])
subprocess.run(["cp", f"/home/user/astrometry.net-0.97/demo/cropped_center.new", f"/home/user/StartrackPC/Fits_testing/"])
subprocess.run(["cp", f"/home/user/astrometry.net-0.97/demo/cropped_center.corr", f"/home/user/StartrackPC/Fits_testing/"])

from datetime import datetime, timezone

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

    latitude = 25.1775      
    longitude = 121.5475
    time = gmst_time(ut_time)

    Dec = latitude
    Ra = (time + longitude/15)%24 #hour

    Ra *= 15 #degree

    print(f"({Ra}, {Dec})")

    return Ra, Dec

def find_theo_center(ut_time, croplength, x_shift, y_shift):

    st_ra, st_dec = theory_skycoord(ut_time)

    # Open the FITS file with WCS header
    hdulist = fits.open(f'/home/user/StartrackPC/Fits_testing/cropped_center.new')  # This should have the WCS solution
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

    return cm_x+i+x_shift, cm_y+j+y_shift

theox, theoy = find_theo_center("UT 7/15/2025 5:01:34 PM", 300, x_min, y_min)

print(f"{x_center}, {y_center}")
print(f"{theox}, {theoy}")

plt.scatter(x_center, y_center, color='red', s=2)
plt.scatter(theox, theoy, color='green', s=2)
plt.title("Threshold + Contours")
plt.savefig(f'thres{i}+contour.jpg')

from astroquery.vizier import Vizier
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import cv2


Vizier.ROW_LIMIT = 3
viz = Vizier(columns=["*", "+_r"], catalog="I/311/hip2")

dx = []
dy = []

x=[]
y=[]

fit_mag = np.array([])
nfit_mag = np.array([])

img = cv2.imread("cropped_center-objs.png")

hdul = fits.open("cropped_center.corr")
data = hdul[1].data

in_ra = data['index_ra']
in_dec = data['index_dec']
Ra = data['field_ra']
Dec = data['field_dec']
flux = data['FLUX']

x1 = data['field_x']
y1 = data['field_y']

x2 = data['index_x']
y2 = data['index_y']

print(len(in_ra))

for i in range(len(in_ra)):

        Raa = in_ra[i]
        Decc = in_dec[i]

        print(f"Ra:{Raa}, Dec:{Decc}")

        dx.append(Ra[i] - in_ra[i])
        dy.append(Dec[i] - in_dec[i])

        cv2.arrowedLine(img, (int(x1[i]), int(y1[i])), (int(x2[i]), int(y2[i])), color=(0, 255, 255), thickness=1)

        coord = SkyCoord(ra=Raa*u.deg, dec=Decc*u.deg, frame='icrs')
        result = viz.query_region(coord, radius=600*u.arcsec)

        # 查看查詢結果
        if result:
            print(f"found {i+1}")
            hip_table = result[0]
            x.append(Ra[i] - hip_table["RArad"][0])
            y.append(Dec[i] - hip_table["DErad"][0])
        else:
            print("not found")

plt.figure(figsize=(8, 6))
plt.scatter(x, y, color='green',label = "field", alpha=0.7)
plt.scatter(0, 0, color='red', label = "Hipparcos", alpha=0.7)

plt.xlabel('Ra-axis')
plt.ylabel('Dec-axis')
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig("delta_ra_dec(hip).png", dpi=300)
#plt.show()

#---------------------------------------------------------------------

plt.figure(figsize=(8, 6))
plt.scatter(dx, dy, color='green',label = "field", alpha=0.7)
plt.scatter(0, 0, color='red', label = "index", alpha=0.7)

plt.xlabel('Ra-axis')
plt.ylabel('Dec-axis')
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig("delta_ra_dec(index).png", dpi=300)
#plt.show()

#---------------------------------------------------------------------------

from scipy.optimize import curve_fit

#--------------------------------------------------------------------------------

def gaussian(x, A, mu, sigma):
    return A * np.exp(-((x - mu)**2) / (2 * sigma**2))

bin_width = 0.05
bins = np.arange(min(dx)-bin_width, max(dx) + bin_width, bin_width)
counts, bin_edges = np.histogram(dx, bins=bins)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

mu_est, sigma_est = norm.fit(dx)
initial_guess = [max(counts), mu_est, sigma_est]  # A, mu, sigma
popt, _ = curve_fit(gaussian, bin_centers, counts, p0=initial_guess)
plt.figure(figsize=(8, 6))
plt.bar(bin_centers, counts, width=bin_width, alpha=0.6, label='Histogram')
x_fit = np.linspace(-1.5, 1.5, 1000)
y_fit = gaussian(x_fit, *popt)
plt.plot(x_fit, y_fit, 'r-', label='Gaussian Fit')



A_fit, mu_fit, sigma_fit = popt
plt.title(f"Fit: A={A_fit:.2f}, mu={mu_fit:.2f}, sigma={sigma_fit:.3f}")
plt.xlabel("delta-RA(deg)")
plt.ylabel("Count")
plt.legend()
plt.grid()
plt.xlim(-1.5, 1.5)  # Fix x-axis limits to your known range

plt.savefig("RA_distribution.png", dpi=300)
#plt.show()

#---------------------------------------------------------------------------------------

bin_width = 0.05
bins = np.arange(min(dy)-bin_width, max(dy) + bin_width, bin_width)
counts, bin_edges = np.histogram(dy, bins=bins)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

mu_est, sigma_est = norm.fit(dy)
initial_guess = [max(counts), mu_est, sigma_est]  # A, mu, sigma
popt, _ = curve_fit(gaussian, bin_centers, counts, p0=initial_guess)
plt.figure(figsize=(8, 6))
plt.bar(bin_centers, counts, width=bin_width, alpha=0.6, label='Histogram')
x_fit = np.linspace(-1.5, 1.5, 1000)
y_fit = gaussian(x_fit, *popt)
plt.plot(x_fit, y_fit, 'r-', label='Gaussian Fit')



A_fit, mu_fit, sigma_fit = popt
plt.title(f"Fit: A={A_fit:.2f}, mu={mu_fit:.2f}, sigma={sigma_fit:.3f}")
plt.xlabel("delta-DEC(deg)")
plt.ylabel("Count")
plt.legend()
plt.grid()

plt.xlim(-1.5, 1.5)  # Fix x-axis limits to your known range

plt.savefig("DEC_distribution.png", dpi=300)
#plt.show()