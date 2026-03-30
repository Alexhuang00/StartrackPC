import os
import glob
import re
from astropy.io import fits
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors


def plot_distortion_map(data_list):
    # 1. Convert to a NumPy array first to handle np.float64 types correctly
    # Then wrap it in a DataFrame
    data_array = np.array(data_list)
    
    # Check if the array has 3 columns (x, y, distortion)
    if data_array.ndim == 1:
        # If your list was flat [x1, y1, d1, x2, y2, d2...]
        data_array = data_array.reshape(-1, 3)
        
    df = pd.DataFrame(data_array, columns=['x', 'y', 'distortion'])

    # 2. Now rounding will work without needing pd.to_numeric
    df['x_10px'] = (df['x'] / 10).round().astype(int) * 10
    df['y_10px'] = (df['y'] / 10).round().astype(int) * 10

    # 3. Aggregate
    avg_dist = df.groupby(['y_10px', 'x_10px'])['distortion'].mean().reset_index()

    # 4. Pivot for the heatmap
    pivot_table = avg_dist.pivot(index='y_10px', columns='x_10px', values='distortion')

    # 5. Plotting
    plt.figure(figsize=(12, 10))
    
    # cmap='magma' or 'viridis' are great for this
    max_val = pivot_table.max().max()
    boundaries = np.arange(0, max_val + 0.5, 0.5)
    
    # 2. Create a colormap with the number of colors matching our bins
    # We use 'Reds_r' as you requested
    base_cmap = plt.get_cmap('viridis')
    colors = base_cmap(np.linspace(0, 1, len(boundaries) - 1))
    cmap = mcolors.ListedColormap(colors)
    
    # 3. Create a Norm that maps data to these specific boundaries
    norm = mcolors.BoundaryNorm(boundaries, cmap.N)

    ax = sns.heatmap(
        pivot_table, 
        cmap=cmap, 
        norm=norm,
        cbar_kws={
            'label': 'Avg Distortion',
            'ticks': boundaries, # This ensures the numbers 0.5, 1.0, etc. appear
            'spacing': 'proportional'
        }
    )

    plt.title('Distortion Map (10-Pixel Resolution)', fontsize=15)
    plt.xlabel('X Coordinate (pixels)', fontsize=12)
    plt.ylabel('Y Coordinate (pixels)', fontsize=12)
    
    # Ensure the Y-axis points upward like a standard coordinate system
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    plt.show()


Corr_paths = glob.glob('/home/user/StartrackPC/04.3 Corr/*.corr')

def natural_key(filename):
    # Split string into chunks: ['picture', 1, '', '.png']
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', filename)]
Corr_paths.sort(key=lambda path: natural_key(os.path.basename(path)))

n=0

distor = []
maxdis = 0
coord = (0, 0)

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
        dist = min(dx**2 + dy**2, 10)
        distor.append([x1[i]-100, y1[i]-100, dist])
        if dist > maxdis:
            maxdis = dist
            coord = (x1[i], y1[i])

    n+=1

#print(maxdis, coord)
#print(distor)
# Call the function with your data
plot_distortion_map(distor)


