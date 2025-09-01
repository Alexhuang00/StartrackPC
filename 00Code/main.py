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
from figure import center_distrubute, solve_time, earthloc_distrubute

image_paths = glob.glob('/home/alex/Startrack/01Image/*.jpg')

image_paths.sort(key=lambda x: os.path.basename(x))

#storage
actual_center = []
theory_center = []
actual_earthloc = []
corrected_earthloc = []
lulin_earthloc = (120.872624, 23.469447)
solving_time = []

#parameter
threshold = 5
croplength = 200

#main loop
n=0
for path in image_paths:


    #pre-process
    cut_path = f"/home/alex/Startrack/03Cropped/cropped{n+1}.jpg"

    img, center = basedealing(path, n, threshold, croplength)
    actual_center.append(center)
    UtTime = find_UT_time(img)

    cropbox = (int(center[0]-0.5*croplength), int(center[1]-0.5*croplength), int(center[0]+0.5*croplength), int(center[1]+0.5*croplength))
    crop_image(path, cut_path, cropbox)

    #astrometry.net
    wsl_input = cut_path
    objs_output = f"/home/alex/Startrack/04.1 Objs"
    wcs_output = f"/home/alex/Startrack/04.2 Wcs"
    corr_output = f"/home/alex/Startrack/04.3 Corr"

    t1 = time.time()

    solve_field(wsl_input, wcs_output, corr_output, objs_output)

    t1e = time.time()

    solving_time.append(abs(t1e-t1))

    #resulting
    x, y = find_theo_center(n, UtTime, croplength, cropbox[0], cropbox[1], img)
    theory_center.append((x, y))

    lon, lat = zenith_to_earth_location(center[0]-cropbox[0], center[1]-cropbox[1], n, UtTime)
    actual_earthloc.append((lon, lat))

    clon, clat = zenith_to_earth_location(center[0]-cropbox[0]-1.338, center[1]-cropbox[1]-9.558, n, UtTime)
    corrected_earthloc.append((clon, clat))

    n+=1
    
#analyzing

#center obs vs theo
center_distrubute(actual_center, theory_center)


#solve time
solve_time(solving_time)

#locating
earthloc_distrubute(actual_earthloc, lulin_earthloc, correct=False)
earthloc_distrubute(corrected_earthloc, lulin_earthloc, correct=True)