import cv2
import numpy as np

def basedealing(path, n, threshold, croplength):
    img = cv2.imread(path)

    print("-------------------------------------------------------")

    if img is not None:
        print(f"Loaded: {path}")
    else:
        print(f"Failed to load: {path}")

    print(f"image {n+1} :")

    

    img[0, :] = 0

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    ret, thres = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    cv2.imwrite(f"/home/alex/Startrack/02Thres/th{n+1}.jpg", thres)

    contours, _ = cv2.findContours(thres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(img, [largest_contour], -1, (0, 0, 255), 2)
    (x, y), radius = cv2.minEnclosingCircle(largest_contour)

    print(f"minEncloseCircle : center=({x}, {y}), radius={radius}")
    cv2.circle(img, (int(x), int(y)), int(radius), (0, 255, 0), 1)
    cv2.circle(img, (int(x), int(y)), 2, (0, 255, 0), 3)

    cropbox = (int(x-0.5*croplength), int(y-0.5*croplength), int(x+0.5*croplength), int(y+0.5*croplength))
    cv2.rectangle(img, (cropbox[0], cropbox[1]), (cropbox[2], cropbox[3]), (0, 0, 255), 2)

    

    return img, (x, y)