
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
from scipy.optimize import minimize

import pandas as pd
import random
import numpy as np
import math

import os

from astropy.io import ascii

from numpy.lib import recfunctions as rfn
from astropy import wcs
from astropy import units as u
from astropy.coordinates import SkyCoord

import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
import glob
import pathlib





Corr_paths = glob.glob('/home/user/StartrackPC/04.3 Corr/*.corr')

def natural_key(filename):
    # Split string into chunks: ['picture', 1, '', '.png']
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', filename)]
Corr_paths.sort(key=lambda path: natural_key(os.path.basename(path)))

n=0

plt.figure(figsize=(8, 8))



class MeasureDistortion:
    def __init__(self, x, y, fid, x_mm, y_mm, fiducialId, nsigma=None, alphaRot=0.0):
        """x, y: measured positions in pfi coordinates
        fid: fiducial ids for (x, y) (-1: unidentified)
        x_mm, y_mm : true positions in pfi coordinates
        fiducialId: fiducial ids for (x_mm, y_mm)
        nsigma: clip the fitting at this many standard deviations (None => 5).  No clipping if <= 0
        alphaRot: coefficient for the dtheta^2 term in the penalty function
        """
        self.nsigma = 5 if nsigma is None else nsigma
        self.alphaRot = alphaRot

        _x = []
        _y = []
        _x_mm = []
        _y_mm = []
        #
        # The correct number of initial values; must match code in __call__()
        # Set initial center to (640, 512)
        #9.60585641e+01  9.27788429e+01 -2.71551676e-03 -3.10836522e-03 3.99827691e-07
        x0, y0, theta, dscale, scale2 = np.array([ 9.60585641e+01,  9.27788429e+01, -2.71551676e-03, -3.10836522e-03, 3.99827691e-07], dtype=float)
        self._args = np.array([x0, y0, theta, dscale, scale2])
        self.frozen = np.zeros(len(self._args), dtype=bool)

        for fi in fiducialId:
            ix = np.where(fi == fid)[0]
            if len(ix) > 0:
                _x.append(x[ix][0])
                _y.append(y[ix][0])
                _x_mm.append(x_mm[fiducialId == fi][0])
                _y_mm.append(y_mm[fiducialId == fi][0])

        self.x = np.array(_x)
        self.y = np.array(_y)

        self.x_mm = np.array(_x_mm)
        self.y_mm = np.array(_y_mm)

    @staticmethod
    def clip(d, nsigma):
        if len(d) == 0:
            return np.ones_like(d, dtype=bool)

        q25, q50, q75 = np.percentile(d, [25, 50, 75])
        std = 0.741*(q75 - q25)

        return np.abs(d - q50) < nsigma*std

    def __call__(self, args):
        tx, ty = self.distort(self.x, self.y, *args)

        d = np.hypot(tx - self.x_mm, ty - self.y_mm)

        if self.nsigma > 0:
            d = d[self.clip(d, self.nsigma)]

        penalty = np.sum(d**2)
        penalty += self.alphaRot*(args[2] - 0.0)**2 # include a prior on the rotation, args[2]

        return penalty

    def getArgs(self):
        return self._args

    def setArgs(self, *args):
        not_frozen = np.logical_not(np.array(self.frozen))
        self._args[not_frozen] = np.array(args[0])[not_frozen]

    def distort(self, x, y, *args, **kwargs):
        if args:
            args = np.array(args)
        else:
            args = self._args

        args[self.frozen] = self._args[np.array(self.frozen)]

        x0, y0, theta, dscale, scale2 = args  # must match length of self._args in __init__
        inverse = kwargs.get("inverse", False)

        theta = np.deg2rad(theta)
        c, s = np.cos(theta), np.sin(theta)

        # Calculate radius from the specified center (x0, y0)
        r = np.hypot(x - x0, y - y0) if inverse else np.hypot(x - x0, y - y0)
        scale = (1 + dscale) + scale2*r**2

        if inverse:
            x_centered = x - x0   # don't modify x
            y_centered = y - y0
            s = -s    # change sign of theta
            tx = x0 + ( c*x_centered + s*y_centered)/scale
            ty = y0 + (-s*x_centered + c*y_centered)/scale
        else:
            x_centered = x - x0
            y_centered = y - y0
            tx = x0 + scale*( c*x_centered + s*y_centered)
            ty = y0 + scale*(-s*x_centered + c*y_centered)

        return tx, ty

#-----------------------------------------main code--------------------------------

for path in Corr_paths:

    #if n >= 1:
        #break
        #n+=1
        #continue

    detected_x = []
    detected_y = []
    actual_x = []
    actual_y = []

    print(f"solving corr{n+1} ......")

    hdul = fits.open(path)
    data = hdul[1].data  # 通常表格在 Extension 1

    x1 = data['field_x']
    y1 = data['field_y']

    x2 = data['index_x']
    y2 = data['index_y']

    for i in range(len(x1)):

        dx = (x2[i] - x1[i])
        dy = (y2[i] - y1[i])
        dist = dx**2 + dy**2

        if dist >= 1:
            plt.quiver(x1[i], y1[i], dx, dy, angles='xy', scale_units='xy', scale=1)

    detected_x = np.append(detected_x, x1)
    detected_y = np.append(detected_y, y1)
    actual_x = np.append(actual_x, x2)
    actual_y = np.append(actual_y, y2)

    matched_detected_x = [] 
    matched_detected_y = [] 
    matched_actual_x = [] 
    matched_actual_y = [] 
    matched_detected_idx = [] # Store indices of matched detected points 
    matched_actual_idx = [] # Store indices of matched actual points

    for i in range(len(detected_x)): 
        dist = np.sqrt((detected_x[i] - actual_x)**2 + (detected_y[i] - actual_y)**2) 
        if min(dist) < 20: # Threshold for matching 
            idx = np.argmin(dist) 
            matched_detected_x.append(detected_x[i]) 
            matched_detected_y.append(detected_y[i]) 
            matched_actual_x.append(actual_x[idx]) 
            matched_actual_y.append(actual_y[idx]) 
            matched_detected_idx.append(i) # Index in detected points 
            matched_actual_idx.append(idx) # Index in actual points

    matched_detected_x = np.array(matched_detected_x)
    matched_detected_y = np.array(matched_detected_y)
    matched_actual_x = np.array(matched_actual_x)
    matched_actual_y = np.array(matched_actual_y)
    matched_detected_idx = np.array(matched_detected_idx)
    matched_actual_idx = np.array(matched_actual_idx)

    fid_for_detected = matched_actual_idx  # Each detected point gets the ID of its matched actual point
    fiducial_ids = matched_actual_idx

    distortion = MeasureDistortion(
        x=matched_detected_x,           # measured positions
        y=matched_detected_y,           # measured positions
        fid=fid_for_detected,          # fiducial IDs for measured points
        x_mm=matched_actual_x,         # true positions
        y_mm=matched_actual_y,         # true positions
        fiducialId=fiducial_ids        # fiducial IDs for true positions
    )

    #fig, ax = plt.subplots(figsize=(10,8))
    #ax.scatter(actual_x, actual_y, color='red', label='Actual Points', s=10)
    #ax.scatter(matched_detected_x, matched_detected_y, color='green', label='Extracted Points', s=10)

    distortion = MeasureDistortion(
        x=matched_detected_x,           # measured positions
        y=matched_detected_y,           # measured positions
        fid=fid_for_detected,          # fiducial IDs for measured points
        x_mm=matched_actual_x,         # true positions
        y_mm=matched_actual_y,         # true positions
        fiducialId=fiducial_ids)     # fiducial IDs for true positions

    # Add labels and legend
    #ax.set_xlabel('X Coordinate')
    #ax.set_ylabel('Y Coordinate')
    #ax.set_title('Image with Extracted Points and Grid Overlay')
    #ax.legend()


    #plt.savefig("/home/user/StartrackPC/06Figure/Image with Extracted Points and Grid Overlay.png", dpi=400)
    #plt.clf()

    # Optimize distortion parameters
    result = minimize(distortion, distortion.getArgs(), method='Powell')

    # Get optimized parameters
    optimized_args = result.x
    print("Optimized Parameters:", optimized_args)

    # Apply the distortion model
    transformed_x, transformed_y = distortion.distort(matched_detected_x, matched_detected_y, *optimized_args)

    shape = (200, 200)

    sigma = 1.0

    img = np.zeros(shape, dtype=np.float64)

    height, width = shape

        # Limit computation to small window (important for speed)
    r = int(3 * sigma)  # 3-sigma window

    for (x, y) in zip(transformed_x, transformed_y):
        y = height - y
        x0, y0 = int(x), int(y)

            # local patch bounds
        x_min = max(0, x0 - r)
        x_max = min(width, x0 + r + 1)
        y_min = max(0, y0 - r)
        y_max = min(height, y0 + r + 1)

            # coordinate grid
        X, Y = np.meshgrid(np.arange(x_min, x_max),
                            np.arange(y_min, y_max))

            # Gaussian centered at (x, y) (float!)
        patch = np.exp(-((X - x)**2 + (Y - y)**2) / (2 * sigma**2))

        img[y_min:y_max, x_min:x_max] += patch

        plt.imshow(img, cmap='gray', origin='lower')
        plt.axis('off')  # remove axes
        plt.savefig(f"/home/user/StartrackPC/03.1Trans_cropped/cropped{n+1}.jpg", bbox_inches='tight', pad_inches=0)
        plt.clf()
    # Plot the results

    #fig, ax = plt.subplots(figsize=(10, 8))
    #ax.scatter(matched_actual_x, matched_actual_y, color='blue', label='Actual Points', s=10)
    #ax.scatter(transformed_x, transformed_y, color='red', label='Transformed Points', s=10)
    #ax.set_xlabel('X Coordinate')
    #ax.set_ylabel('Y Coordinate')
    #ax.set_title('Distortion Measurement')
    #ax.legend()
    #plt.savefig("/home/user/StartrackPC/06Figure/Distortion Measurement.png", dpi=400)

    #plt.show()

    #plt.clf()

    n+=1

