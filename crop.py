import cv2, os
import numpy as np
coordinates = [[624.0955200195312, 155.08224487304688],[797.5823974609375, 446.6824645996094]]
img = 'images/img.jpeg'
def crop(img, x1, y1, x2, y2):
    img = cv2.imread(img)
    cv2.imshow("original", img)
    cropped_image = img[x1:x2, y1:y2]
    cv2.imshow("cropped", cropped_image)
    cv2.waitKey(0)

crop(img, int(coordinates[0][0]), int(coordinates[0][1]), int(coordinates[1][0]), int(coordinates[1][1]))