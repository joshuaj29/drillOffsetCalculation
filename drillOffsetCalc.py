"""
Provides Offset Calculations for Two Concatenated Circles

@author: JoshuaJ
"""

import cv2
import numpy as np
import math


# Load image you want offset calculations for
# img will get iterated on. Will not stay the same
img = cv2.imread('xray photos/xray9.jpg')
# Copy image for side-by-side display at end
origImg = img.copy()

# Convert original image to gray. Could also do this in the imread function
image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Use a GaussianBlur to smoothen xray artifacts
blur = cv2.GaussianBlur(image, (7,7), 0)

# threshold with an adaptive mean due to narrow histogram
# binary inverse threshold due to the way contours are found and our original image color
thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY_INV, 21, 3)


# Perform a one iteration opening operation under a 5x5 elliptical kernel
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 1)



# Find all contours, hierarchies. Retain only the hierarchy value
contours,hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
hierarchy = hierarchy[0]



def detect_contours(imgFile, loopIndex, contours=contours, hierarchy=hierarchy):
    '''
    detect_contour function draws specified contours onto the original image
    imgFile - numpy array converted from file URL
    loopIndex - (i). Integer. Is the current loop index
    contours - list array. default parameter
    hierarchy - list array of one. default parameter. 
    '''
    nstring = str(i)
    cv2.drawContours(img, contours, i, color=(0,255,0), thickness=1)
    cv2.putText(img, nstring, contours[i][0][0],
        cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,255,255),1,cv2.LINE_AA)   

cnt = []
inners = []
# Draw all detected contours on image in green with a thickness of 1 pixel
# loop looks at inner two tiers, 2nd and 3rd hierarchy tier
for i in range(len(hierarchy)):
    currentH = hierarchy[i]
    #filled, no child, yes parent
    if currentH[2] == -1 and currentH[3] >= 0:
        cnt.append(contours[i])
        detect_contours(img, i)
        inners.append(0)
    
    # unfilled, yes child, yes parent
    elif currentH[2] >= 0 and currentH[3] >= 0:
        cnt.append(contours[i])
        detect_contours(img, i)
        inners.append(1)




centers = []
# Find centroid of all remaining contours
for j in cnt:
    M = cv2.moments(j)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    centers.append([cx,cy])

    pts = np.array([[cx-3,cy],[cx+3,cy],[cx,cy],[cx,cy+3],[cx,cy-3]], np.int32)
    cv2.polylines(img,[pts],False,(0,0,255))


# distance from parent to child
for k in range(len(inners)):
    if inners[k] == True:
        print(math.dist(centers[k],centers[k+1]))


#show images side by side
display = np.concatenate((origImg, img), axis=1)
cv2.imshow('Input | Detected Contours', display)
cv2.waitKey(0)
cv2.destroyAllWindows()




