import numpy as np
import matplotlib.pyplot as plt
import json
import os
from scipy.stats import norm

folder = f"/home/user/StartrackPC/00Code/starlist/"
count = len([f for f in os.listdir(folder) if f.endswith(".json")])

sdx = []
sdy = []
sx = []
sy = []
fit = []
nfit = []


for n in range(count):

    with open(f"/home/user/StartrackPC/00Code/starlist/starinfo{n+1}.json", "r") as f:
        starinf = json.load(f)

    sdx.append(starinf[0][0])
    sdy.append(starinf[0][1])
    sx.append(starinf[0][2])
    sy.append(starinf[0][3])
    fit.append(starinf[0][4])
    nfit.append(starinf[0][5])

dx = [x for sublist in sdx for x in sublist]
dy = [x for sublist in sdy for x in sublist]
x = [x for sublist in sx for x in sublist]
y = [x for sublist in sy for x in sublist]
mag = [x for sublist in fit for x in sublist]
nmag = [x for sublist in nfit for x in sublist]

fit_mag = np.array(mag)
nfit_mag = np.array(nmag)

bin_width = 0.2
min_mag = min(min(fit_mag), min(nfit_mag))
max_mag = max(max(fit_mag), max(nfit_mag))

bins = np.arange(min_mag-bin_width, max_mag + bin_width, bin_width)
counts, bin_edges = np.histogram(fit_mag, bins=bins)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

ncounts, nbin_edges = np.histogram(nfit_mag, bins=bins)
nbin_centers = (nbin_edges[:-1] + nbin_edges[1:]) / 2
    
plt.figure(figsize=(8, 6))
plt.bar(bin_centers, counts, width=bin_width, alpha=0.6,color='green', label='fit')
plt.bar(nbin_centers, ncounts, width=bin_width, alpha=0.6,color='red', label='not fit', bottom=counts)

plt.title("mag vs fit model")
plt.xlabel("mHip")
plt.ylabel("Count")
plt.legend()
plt.grid()
plt.xlim(-2, 8)  # Fix x-axis limits to your known range

plt.savefig("/home/user/StartrackPC/06Figure/mag-fitable.png", dpi=300)

#-----------------------------------------------------------------------------------

# 統計各 bin 的數量
a_counts, _ = np.histogram(fit_mag, bins)
total_counts, _ = np.histogram(np.concatenate([fit_mag, nfit_mag]), bins)

# 避免除以0
with np.errstate(divide='ignore', invalid='ignore'):
    ratios = np.true_divide(a_counts, total_counts)*100
    ratios[~np.isfinite(ratios)] = 0  # 把 inf 或 NaN 變成 0

# 畫圖
plt.figure(figsize=(8, 5))
plt.bar(bin_centers, ratios, width=bin_width * 0.9, color='green', alpha=0.7)
plt.xlabel("mHip")
plt.ylabel("fit %")
plt.ylim(0, 105)
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig("/home/user/StartrackPC/06Figure/mag-fitable_ratio.png", dpi=300)

#----------------------------------------------------------------------------------------------------------

#cv2.imwrite("cropped1-arrowed.png", img)

plt.figure(figsize=(8, 6))
plt.scatter(x, y, color='green',label = "field", alpha=0.7)
plt.scatter(0, 0, color='red', label = "Hipparcos", alpha=0.7)

plt.xlabel('Ra-axis')
plt.ylabel('Dec-axis')
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig("/home/user/StartrackPC/06Figure/delta_ra_dec(hip).png", dpi=300)
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
plt.savefig("/home/user/StartrackPC/06Figure/delta_ra_dec(index).png", dpi=300)
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

plt.savefig("/home/user/StartrackPC/06Figure/RA_distribution.png", dpi=300)
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

plt.savefig("/home/user/StartrackPC/06Figure/DEC_distribution.png", dpi=300)
#plt.show()