"""
Provides Offset Calculations for Two Concatenated Circles
Shows offset information for an entire panel registration (4 images)

files need to be in format:
P##AA_###.jpg or png
P and two panel number slots
Image position - BL, BR, TL, TR (bottom or top, left or right)
_ underscore
### two or three digits for drill diameter

@author: JoshuaJ
"""

import cv2
import numpy as np
import math
import os





def loadImg(path, rotate=0):
    # Load image you want offset calculations for
    # img will get iterated on. Will not stay the same
    img = cv2.imread(path)

    # rotate 180 deg, if necessary
    if rotate:
        img = cv2.rotate(img, cv2.ROTATE_180)

    # Copy image for side-by-side display at end
    #origImg = img.copy()

    # Convert original image to gray. Could also do this in the imread function
    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img, grayImg


def threshMask(grayImage):
    # Use a GaussianBlur to smoothen xray artifacts
    blur = cv2.GaussianBlur(grayImage, (7,7), 0)

    # threshold with an adaptive mean due to narrow histogram
    # binary inverse threshold due to the way contours are found and our original image color
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 21, 2)

    # Perform a one iteration opening operation under a 5x5 elliptical kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 1)

    return opening



def imgCont_Hier(threshold):
    # Find all contours, hierarchies. Retain only the hierarchy value
    contours,hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    hierarchy = hierarchy[0]

    # filtering non circles and very small shapes
    contourList = []
    hierarchyList = []
    i=0
    for con in contours:
        epsilon = 0.009*cv2.arcLength(con, True)
        approx = cv2.approxPolyDP(con, epsilon, True)
        area = cv2.contourArea(con)
        if (len(approx) > 8) & (area > 30):
            # rect is (center (x,y), (width, height), angle of rotation)
            rect = cv2.minAreaRect(con)
            width = rect[1][0]
            height = rect[1][1]
            if (width/height >= .85) and (width/height <= 1.15):
                contourList.append(con)
                hierarchyList.append(hierarchy[i])
        i+=1

    return contourList, hierarchyList




def drawConcatCircles(image, contours, hierarchy):
    cnt = []
    inners = {}
    holeDiams = {}
    # Draw all detected contours on image in green with a thickness of 1 pixel
    # loop looks at inner two tiers, 2nd and 3rd hierarchy tier
    for i in range(len(hierarchy)):
        currentH = hierarchy[i]
        #filled, no child, yes parent
        if currentH[2] == -1 and currentH[3] >= 0:
            # Holes
            # finding equivalent diameter. To be used later for offset calcs
            area = cv2.contourArea(contours[i])
            equDiam = np.sqrt(4*area/(np.pi))
            holeDiams[f'{i}'] = equDiam

            drawConCir_Helper(image, contours, i, cnt, inners, 0)

        # unfilled, yes child, yes parent
        elif currentH[2] >= 0 and currentH[3] >= 0:
            # annular ring
            drawConCir_Helper(image, contours, i, cnt, inners, 1)

    return cnt, inners, holeDiams



def drawConCir_Helper(image, contours, index, cntList, innersDict, boolInfo):
    cntList.append(contours[index])
    detect_contours(image, index, contours)
    innersDict[f'{index}'] = boolInfo




def detect_contours(imgFile, loopIndex, contours):
        '''
        detect_contour function draws specified contours onto the original image
        imgFile - numpy array converted from file URL
        loopIndex - (i). Integer. Is the current loop index
        contours - list array. default parameter
        hierarchy - list array of one. default parameter. 
        '''
        nstring = str(loopIndex)
        cv2.drawContours(imgFile, contours, loopIndex, color=(0,200,0), thickness=1)
        cv2.putText(imgFile, nstring, contours[loopIndex][0][0],
            cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,255,255),1,cv2.LINE_AA)
        


def centroids(image, cntList):
    centers = []
    # Find centroid of all remaining contours
    for j in cntList:
        M = cv2.moments(j)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        centers.append([cx,cy])

        pts = np.array([[cx-3,cy],[cx+3,cy],[cx,cy],[cx,cy+3],[cx,cy-3]], np.int32)
        cv2.polylines(image,[pts],False,(0,0,255))
    return centers





def drawOffset(directoryPath, file, drDiameter, rotation=0):
    #path = directoryPath + '/' + file
    path = file

    img, grayImg = loadImg(path, rotation)

    opening = threshMask(grayImg)

    contours, hierarchy = imgCont_Hier(opening)

    cnt, inners, holeDiams = drawConcatCircles(img, contours, hierarchy)
    
    centers = centroids(img, cnt)


    # distance from parent to child
    i = 0
    hDiamKeys = list(holeDiams.keys())
    offsetDiff = []
    for k,v in inners.items():

        if v == False:
            concatDist = math.dist(centers[i-1],centers[i])
            if k in hDiamKeys:
                drillDiam = drDiameter
                distMils = concatDist * drillDiam / holeDiams[k]
                offsetDiff.append(distMils)
            else:
                print(f'{k} {concatDist}pix')
                pass
        i+=1

    avgOff = np.mean(offsetDiff)
    minOff = min(offsetDiff)
    maxOff = max(offsetDiff)

    statText = (f'Avg Offset: {round(avgOff,2)}mils     Min Offset: {round(minOff,2)}mils     Max Offset: {round(maxOff,2)}mils     Hole Diam: {drillDiam}mils')

    cv2.putText(img, statText, (60,25),
            cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,255,255),1,cv2.LINE_AA)

    cv2.putText(img, f'File: {file}', (60,40),
            cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,255,255),1,cv2.LINE_AA)
    

    return img, offsetDiff



def onePanel(fileDictionary, key):
    for item in fileDictionary[key]:
        position = item[3:5]
        if position == 'TR':
            file1 = item
            diam1 = bitDiameter(item)
        elif position == 'TL':
            file2 = item
            diam2 = bitDiameter(item)
        elif position == 'BL':
            file3 = item
            diam3 = bitDiameter(item)
        elif position == 'BR':
            file4 = item
            diam4 = bitDiameter(item)
    
    return file1, file2, file3, file4, diam1, diam2, diam3, diam4


def bitDiameter(file):
    hDiam = file[6:9]
    if hDiam[-1] == '.':
        hDiam = hDiam[:-1]

    hDiam = float(hDiam)/10

    return hDiam




def xrayFiles(directoryPath):
    dPath = directoryPath
    directory = os.fsencode(dPath)
    fileList = os.listdir(directory)

    fileDict = {}
    for i in range(len(fileList)):
        panel = fileList[i][1:3]
        if panel in fileDict.keys():
            fileDict[panel].append(fileList[i].decode())
        else:
            fileDict[panel] = [fileList[i].decode()]

    return fileDict
     




def main():
    directoryPath = 'C:/Users/joshuaj/Documents/Extra/Learning/opencv/Xray photos/PlTesting'
    fileDict = xrayFiles(directoryPath)

    # dict for storing image files - for saving
    allFiles = {}

    for key in fileDict:
        # panel number
        pNum = key.decode()

        # resetting the active directory - changes when saving
        os.chdir(directoryPath)
        file1, file2, file3, file4, drDiam1, drDiam2, drDiam3, drDiam4 = onePanel(fileDict, key)

        img, offDiff1 = drawOffset(directoryPath, file1, drDiam1)
        img2, offDiff2 = drawOffset(directoryPath, file2, drDiam2)
        img3, offDiff3 = drawOffset(directoryPath, file3, drDiam3, 1)
        img4, offDiff4 = drawOffset(directoryPath, file4, drDiam4, 1)


        offDiff_all = offDiff1 + offDiff2 + offDiff3 + offDiff4
        meanOffDiff = np.mean(offDiff_all)
        minOffDiff = min(offDiff_all)
        maxOffDiff = max(offDiff_all)

        imgHeight, imgWidth = img.shape[:2]
        bigImage = np.zeros([imgHeight*2, imgWidth*2,3], dtype=np.uint8)

        #quadrant 1
        bigImage[0:imgHeight,imgWidth:] = img

        # quadrant 2
        bigImage[0:imgHeight,0:imgWidth] = img2

        #quadrant 3
        bigImage[imgHeight:, 0:imgWidth] = img3

        #quadrant 4
        bigImage[imgHeight:, imgWidth:] = img4


        cv2.putText(bigImage, f'Panel {pNum}', (imgHeight+125,imgWidth-265),
                cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1,cv2.LINE_AA)
        cv2.putText(bigImage, f'Overall Avg: {round(meanOffDiff,2)}mils', (imgHeight+80,imgWidth-250),
                cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1,cv2.LINE_AA)
        cv2.putText(bigImage, f'Overall Min: {round(minOffDiff,2)}mils', (imgHeight+80,imgWidth-235),
                cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1,cv2.LINE_AA)
        cv2.putText(bigImage, f'Overall Max: {round(maxOffDiff,2)}mils', (imgHeight+80,imgWidth-220),
                cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1,cv2.LINE_AA)



        #show images side by side
        #display = np.concatenate((origImg, img), axis=1)
        #cv2.imshow('Input | Detected Contours', display)
        #cv2.imshow(f'Panel {key.decode()} Registration', bigImage)

        # change path for saving
        os.chdir('C:/Users/joshuaj/Documents/Extra/Learning/opencv/Xray photos/PlOutput')

        # save new images to specified directory
        print(f'Saving file for Panel {pNum}')
        newFile = f'Panel {pNum} Registration.png'
        cv2.imwrite(newFile, bigImage)

        
    '''
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''





if __name__ == "__main__":
    main()



