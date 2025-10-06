from astroquery.vizier import Vizier
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from scipy.stats import norm
import cv2
import json

Vizier.ROW_LIMIT = 3
viz = Vizier(columns=["*", "+_r"], catalog="I/311/hip2")

input_folder = "/home/user/StartrackPC/04.1 Objs"

Corr_paths = glob.glob('/home/user/StartrackPC/04.3 Corr/*.corr')
image_paths = glob.glob(os.path.join(input_folder, "*.png"))
def natural_key(filename):
    # Split string into chunks: ['picture', 1, '', '.png']
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', filename)]
Corr_paths.sort(key=lambda path: natural_key(os.path.basename(path)))
image_paths.sort(key=lambda path: natural_key(os.path.basename(path)))

thres = 0.5
slope = 0.1



n=0
for path,input_path in zip(Corr_paths, image_paths):

    if n <= 121:
        #break
        n+=1
        continue

    dx = []
    dy = []

    x=[]
    y=[]

    fit_mag = np.array([])
    nfit_mag = np.array([])
    
    print(f"solving corr{n+1} ......")

    img = cv2.imread(input_path)

    hdul = fits.open(path)
    data = hdul[1].data  # 通常表格在 Extension 1

    in_ra = data['index_ra']
    in_dec = data['index_dec']
    Ra = data['field_ra']
    Dec = data['field_dec']
    flux = data['FLUX']

    x1 = data['field_x']
    y1 = data['field_y']

    x2 = data['index_x']
    y2 = data['index_y']

    m = []
    mHip = []
    xnn = []
    ynn = []

    starinfo = []

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
            m.append(-2.5 * math.log(flux[i], 10) + 7.5)
            mHip.append(hip_table["Hpmag"][0])
            xnn.append(x1[i])
            ynn.append(y1[i])
        else:
            print("not found")

    from RAMSAC import fit_line_ransac

    nm = np.array(m)
    nmHip = np.array(mHip)
    nx = np.array(xnn)
    ny = np.array(ynn)

    

    model, inliers, inlier_count = fit_line_ransac(nm, nmHip, k=4000, threshold=thres, slope_tol=slope, n=int(0.5*len(m)))

    w = inlier_count

    plt.figure(figsize=(8, 6))

    if model is not None:
        a, b = model
        x_line = np.linspace(0, 7, 100)
        y_line = a * x_line 
        plt.plot(x_line, y_line, 'g-', label=f'RANSAC fit: y={a:.2f}x')
        plt.fill_between(x_line, y_line - thres*math.sqrt(1+a*a), y_line + thres*math.sqrt(1+a*a), color='lightgreen', alpha=0.5, label=f'±{thres} range')
    else:
        plt.plot((0, 6), (0, 6), 'r--', marker = 'o')

    if inliers is not None:
        inliers = np.array(inliers, dtype=bool)
        plt.scatter(nm[inliers]+(b/a), nmHip[inliers], label='Inliers', c='green')
        plt.scatter(nm[~inliers]+(b/a), nmHip[~inliers], label='Outliers', c='red')
        fit_mag = np.append(fit_mag, nmHip[inliers])
        nfit_mag = np.append(nfit_mag, nmHip[~inliers])
        for xf, yf in zip(nx[inliers], ny[inliers]):
            cv2.circle(img,(int(xf), int(yf)), 1, (0,255,0), 1)
    
        for xn, yn in zip(nx[~inliers], ny[~inliers]):
            cv2.circle(img,(int(xn), int(yn)), 1, (0,0,255), 1)
    else:
        plt.scatter(m, mHip, color='red', alpha=0.7)
        nfit_mag = np.append(nfit_mag, nmHip)

    cv2.imwrite(f"/home/user/StartrackPC/05.3_Arrowed/arrowed{n+1}.png", img)

    plt.title(f'inlier : {w}/{len(m)} stars',loc='right')
    plt.title(f'allowed thres : {thres},slope range : 1±{slope}', loc='left')
    plt.xlabel('m-axis')
    plt.ylabel('mHip-axis')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.savefig(f"/home/user/StartrackPC/05.2_Mag/mag{n+1}.png", dpi=300)
    #plt.show()

    def convert(o):
        if isinstance(o, np.ndarray):
            return o.tolist()

    starinfo.append([dx, dy, x, y, fit_mag, nfit_mag])

    with open(f"/home/user/StartrackPC/00Code/starlist/starinfo{n+1}.json", "w") as f:
        json.dump(starinfo, f, default=convert)

    n+=1







