
import numpy as np
import random
import matplotlib.pyplot as plt
import math

def fit_line_ransac(x, y, k=500, threshold=1.0, min_inliers=0.5, slope_tol=0.1, n=10):
    """
    slope_tol: 允許的斜率偏差範圍。當預期斜率為1時，模型斜率必須在[1 - slope_tol, 1 + slope_tol]。
    """
    best_model = None
    best_inlier_count = 0
    best_inliers = None

    n_samples = len(x)
    min_samples = n  # 對直線而言，只需要兩點就足夠

    for _ in range(k):
        # 隨機挑選兩個點
        indices = random.sample(range(n_samples), min_samples)
        x_sample, y_sample = x[indices], y[indices]

        # 擬合線性模型 y = a*x + b
        A = np.vstack([x_sample, np.ones(len(x_sample))]).T
        model_params = np.linalg.lstsq(A, y_sample, rcond=None)[0]
        a, b = model_params

        # 斜率預先檢查：若斜率不在[1-slope_tol, 1+slope_tol]內則跳過
        if abs(a - 1) > slope_tol:
            continue

        # 使用該模型計算所有點的誤差
        y_pred = a * x + b
        errors = np.abs((a * x - y + b) / math.sqrt(a * a + 1))

        # 判斷內點（誤差低於threshold的點）
        inliers = errors < threshold
        inlier_count = np.sum(inliers)

        # 更新最佳模型（必須滿足最小內點比例）
        if inlier_count > best_inlier_count and inlier_count > min_inliers * n_samples:
            best_model = (a, b)
            best_inlier_count = inlier_count
            best_inliers = inliers

    #print(f"best_model:{best_model}, best_inliers:{best_inliers is not None}, best_inlier_count:{best_inlier_count}")

    return best_model, best_inliers, best_inlier_count
