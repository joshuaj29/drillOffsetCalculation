import cv2
import numpy as np
import math

img = cv2.imread('xray photos/xray9.jpg')
origImg = img.copy()

image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Equalized histogram
# create a CLAHE object (Arguments are optional).
#clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
#cl1 = clahe.apply(blur2)

blur = cv2.GaussianBlur(image, (7,7), 0)

thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY_INV, 21, 3)


kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 1)
#closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations = 1)

# Find contours
contours,hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
hierarchy = hierarchy[0]



def detect_contours(imgFile, loopIndex, contours=contours, hierarchy=hierarchy):
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
# centroid
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






# Show the image
#cv2.imshow('Detected Contours', img)
#cv2.imshow('closing', opening)
#cv2.imshow('thresh', thresh)
#cv2.imshow('histEqual', cl1)

#show images side by side
display = np.concatenate((origImg, img), axis=1)
cv2.imshow('Input | Detected Contours', display)
cv2.waitKey(0)
cv2.destroyAllWindows()




# use RETR_EXTERNAL and aspect ratio to only get full pads then perform
# another image processing on result?



