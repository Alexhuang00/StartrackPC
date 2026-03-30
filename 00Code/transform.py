import numpy as np
import matplotlib

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