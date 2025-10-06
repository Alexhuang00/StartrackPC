import glob
import numpy as np
import time
import matplotlib.pyplot as plt
import os

from basic_deal import basedealing
from cut import crop_image
from solving import solve_field
from Ut_time import find_UT_time
from Theory import find_theo_center
from find_earthloc import zenith_to_earth_location


image_paths = glob.glob('/home/user/StartrackPC/01Image/*.jpg')

image_paths.sort(key=lambda x: os.path.basename(x))

#storage
actual_center = []
theory_center = []
actual_earthloc = []
corrected_earthloc = []
lulin_earthloc = (120.872624, 23.469447)
solving_time = []
Utime = []
correction = []

#parameter
threshold = 5
croplength = 200

#main loop
n=0
for path in image_paths:

    #if n == 200:
        #break
        #n+=1
        #continue

    #pre-process
    cut_path = f"/home/user/StartrackPC/03Cropped/cropped{n+1}.jpg"

    img, center = basedealing(path, n, threshold, croplength)
    actual_center.append(center)
    UtTime = find_UT_time(img)
    Utime.append(UtTime)

    cropbox = (int(center[0]-0.5*croplength), int(center[1]-0.5*croplength), int(center[0]+0.5*croplength), int(center[1]+0.5*croplength))
    crop_image(path, cut_path, cropbox)

    #astrometry.net
    wsl_input = cut_path
    objs_output = f"/home/user/StartrackPC/04.1 Objs"
    wcs_output = f"/home/user/StartrackPC/04.2 Wcs"
    corr_output = f"/home/user/StartrackPC/04.3 Corr"

    t1 = time.time()

    solve_field(wsl_input, wcs_output, corr_output, objs_output)

    t1e = time.time()

    solving_time.append(abs(t1e-t1))

    #resulting

    print("resulting ......")

    x, y = find_theo_center(n, UtTime, croplength, cropbox[0], cropbox[1], img)
    theory_center.append((x, y))

    lon, lat = zenith_to_earth_location(center[0]-cropbox[0], center[1]-cropbox[1], n, UtTime)
    actual_earthloc.append((lon, lat))
    correction.append((center[0]-cropbox[0], center[1]-cropbox[1]))

    n+=1
    
#analyzing
from figure import center_distrubute, solve_time, earthloc_distrubute
#center obs vs theo
sx, sy = center_distrubute(actual_center, theory_center)


#solve time
solve_time(solving_time)

#locating

print()
print("Finding earthloc ......")

for i in range(len(actual_earthloc)):
    clon, clat = zenith_to_earth_location(correction[i][0]+sx, correction[i][1]+sy, i, Utime[i])
    corrected_earthloc.append((clon, clat))

earthloc_distrubute(actual_earthloc, lulin_earthloc, correct=False)
earthloc_distrubute(corrected_earthloc, lulin_earthloc, correct=True)