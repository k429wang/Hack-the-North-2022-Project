import cv2
import numpy as np
coordinates = [[0.2,0.3],[0.7,0.8]]
img = 'gcloud/images/unknown.png'

def crop(img, x1, y1, x2, y2):
    img = cv2.imread(img)
    cv2.imshow("original", img)
    cropped_image = img[x1:x2, y1:y2]
    cv2.imshow("cropped", cropped_image)
    cv2.waitKey(0)

crop(img, int(coordinates[0][0]*1280-50), int(coordinates[0][1]*720)-50, int(coordinates[1][0]*1280+50), int(coordinates[1][1]*720)+50)