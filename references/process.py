import cv2
import numpy as np

img = cv2.imread('../images/test3.png')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite('gray.png', gray)

# threshhold
ret,bin = cv2.threshold(gray,145,255,cv2.THRESH_BINARY)
cv2.imwrite('bin.png', bin)

# closing
kernel = np.ones((3,3),np.uint8)
closing = cv2.morphologyEx(bin, cv2.MORPH_CLOSE, kernel)
cv2.imwrite('closing.png', closing)

# invert black/white
inv = cv2.bitwise_not(closing)
cv2.imwrite('inv.png', inv)
