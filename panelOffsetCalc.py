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

    return thresh



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




def getConcatCircles(contours, hierarchy):
    hContours = {}
    arContours = {}
    # finds and differentiates potential holes and annular-ring contours
    # loop looks at inner two tiers, 2nd and 3rd hierarchy tier
    # i is the contour counter
    for i in range(len(hierarchy)):
        currentH = hierarchy[i]
        # filled, no child, yes parent
        if currentH[2] == -1 and currentH[3] >= 0:
            # holes, bool is 0
            hContours[f'{i}'] = [contours[i], 0]
        elif currentH[2] >= 0 and currentH[3] == -1:
            # annular ring, bool is 1
            arContours[f'{i}'] = [contours[i], 1]
    return hContours, arContours



def getCirclePair(contours, hierarchy):
    hContours = {}
    arContours = {}
    # finds and differentiates potential holes and annular-ring contours
    # loop looks at inner two tiers, 2nd and 3rd hierarchy tier
    # i is the contour counter
    for i in range(len(hierarchy)):
        currentH = hierarchy[i]
        # filled, no child, yes parent
        if currentH[2] == -1 and currentH[3] >= 0:
            # holes, bool is 0
            hContours[f'{i}'] = [contours[i], 0]
        elif currentH[2] >= 0 and currentH[3] >= 0:
            # annular ring, bool is 1
            arContours[f'{i}'] = [contours[i], 1]
    return hContours, arContours



def filterCC(hContours, arContours, outsideAR = 2):
    hole_AR = {}
    holeDiams = {}
    for key in arContours:
        arIndex = int(key)
        print(outsideAR)
        holeIndex = arIndex + outsideAR
        # check for outside annular-ring hole pair
        if str(holeIndex) in hContours:
            holeIndex = str(holeIndex)
            hole_AR[key] = arContours[key]
            hole_AR[holeIndex] = hContours[holeIndex]

            # find equivalent diameter of holes. Used in offset calcs
            area = cv2.contourArea(hContours[holeIndex][0])
            equDiam = np.sqrt(4*area/(np.pi))
            holeDiams[holeIndex] = equDiam

    return hole_AR, holeDiams



def centroids(hole_AR):
    centers = []
    centerPts = []
    # Find centroid of all remaining contours
    for key, value in hole_AR.items():
        M = cv2.moments(value[0])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        centers.append([cx,cy])

        pts = np.array([[cx-3,cy],[cx+3,cy],[cx,cy],[cx,cy+3],[cx,cy-3]], np.int32)
        centerPts.append(pts)
    return centers, centerPts



def parChildDist(hole_AR, holeDiams, centers, drDiameter):
    # distance from parent to child
    i = 0
    hDiamKeys = list(holeDiams.keys())
    offsetDiff = []
    for k,v in hole_AR.items():

        if v[1] == False:
            concatDist = math.dist(centers[i-1],centers[i])
            if k in hDiamKeys:
                distMils = concatDist * drDiameter / holeDiams[k]

                if distMils <= 20:

                    offsetDiff.append(distMils)
            else:
                print(f'{k} {concatDist}pix')
                pass
        i+=1
    return offsetDiff


def offsetStats(offsetDiff):
    if len(offsetDiff) == 0:
        avgOff = 'N/A'
        minOff = 'N/A'
        maxOff = 'N/A'
    else:
        avgOff = np.mean(offsetDiff)
        minOff = min(offsetDiff)
        maxOff = max(offsetDiff)
    return avgOff, minOff, maxOff


def drawOnImage(image, hole_AR, centerPts):
    colorDict = {'blue': (255,255,0), 'green': (0,200,0), 'red': (0,0,255), 'yellow': (0,255,255)}
    for pts in centerPts:
        cv2.polylines(image,[pts],False,colorDict['red'])
    
    for key, value in hole_AR.items():
        contours = value[0]
        if value[1]:
            clr = colorDict['blue']
        else:
            clr = colorDict['green']
        
        nstring = key
        cv2.drawContours(image, contours, -1, color=clr, thickness=1)
        cv2.putText(image, nstring, contours[0][0],
            cv2.FONT_HERSHEY_SIMPLEX,0.35,colorDict['yellow'],1,cv2.LINE_AA)
    





def drawOffset(file, drDiameter, arType, rotation=0):
    img, grayImg = loadImg(file, rotation)

    opening = threshMask(grayImg)

    contours, hierarchy = imgCont_Hier(opening)

    if arType:
        hContours, arContours = getConcatCircles(contours, hierarchy)
        hole_AR, holeDiams = filterCC(hContours, arContours)
    else:
        hContours, arContours = getCirclePair(contours, hierarchy)
        hole_AR, holeDiams = filterCC(hContours, arContours, outsideAR=1)

    centers, centerPts = centroids(hole_AR)
    offsetDiff = parChildDist(hole_AR, holeDiams, centers, drDiameter)
    avgOff, minOff, maxOff = offsetStats(offsetDiff)
    drawOnImage(img, hole_AR, centerPts)



    if type(avgOff) is str:
        statText = (f'Avg Offset: {avgOff}     Min Offset: {minOff}     Max Offset: {maxOff}     Hole Diam: {drDiameter}mils')
    else:
        statText = (f'Avg Offset: {round(avgOff,2)}mils     Min Offset: {round(minOff,2)}mils     Max Offset: {round(maxOff,2)}mils     Hole Diam: {drDiameter}mils')

    cv2.putText(img, statText, (60,25),
            cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,255,255),1,cv2.LINE_AA)

    cv2.putText(img, f'File: {file}', (60,40),
            cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,255,255),1,cv2.LINE_AA)
    

    return img, offsetDiff



def onePanel(fileDictionary, key):
    file1, file2, file3, file4, diam1, diam2, diam3, diam4 = False, False, False, False, False, False, False, False
    arType1, arType2, arType3, arType4 = True, True, True, True
    for item in fileDictionary[key]:
        position = item[3:5]
        ar = item[8:11]
        if position == 'TR':
            file1 = item
            diam1 = bitDiameter(item)
            if '_1' in ar:
                arType1 = False
        elif position == 'TL':
            file2 = item
            diam2 = bitDiameter(item)
            if '_1' in ar:
                arType2 = False
        elif position == 'BL':
            file3 = item
            diam3 = bitDiameter(item)
            if '_1' in ar:
                arType3 = False
        elif position == 'BR':
            file4 = item
            diam4 = bitDiameter(item)
            if '_1' in ar:
                arType4 = False
    
    return file1, file2, file3, file4, diam1, diam2, diam3, diam4, arType1, arType2, arType3, arType4


def bitDiameter(file):
    hDiam = file[6:9]
    if (hDiam[-1] == '.') or (hDiam[-1] == '_'):
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
     


def imgDimensions(image):
    imgHeight, imgWidth = image.shape[:2]
    bigImage = np.zeros([imgHeight*2, imgWidth*2,3], dtype=np.uint8)
    return imgHeight, imgWidth, bigImage



def fullOffStat(od1, od2, od3, od4):
    offDiff_all = od1 + od2 + od3 + od4
    for offset in reversed(offDiff_all):
        if offset == 'N/A':
            offDiff_all.pop(offset)

    if len(offDiff_all) != 0:
        meanOffDiff = np.mean(offDiff_all)
        minOffDiff = min(offDiff_all)
        maxOffDiff = max(offDiff_all)
    else:
        meanOffDiff, minOffDiff, maxOffDiff = 'N/A', 'N/A', 'N/A'
    return meanOffDiff, minOffDiff, maxOffDiff



def addTextStats(bigImage, height, width, pNum, mean, min, max):
    if type(mean) is np.float64:
        mean = round(mean,2)
        max = round(max,2)
        min = round(min,2)

    cv2.putText(bigImage, f'Panel {pNum}', (height+125,width-265),
            cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1,cv2.LINE_AA)
    cv2.putText(bigImage, f'Overall Avg: {mean}mils', (height+80,width-250),
            cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1,cv2.LINE_AA)
    cv2.putText(bigImage, f'Overall Min: {max}mils', (height+80,width-235),
            cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1,cv2.LINE_AA)
    cv2.putText(bigImage, f'Overall Max: {min}mils', (height+80,width-220),
            cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1,cv2.LINE_AA)



def main():
    directoryPath = 'C:/Users/joshuaj/Documents/Extra/Learning/opencv/Xray photos/PlTesting'
    fileDict = xrayFiles(directoryPath)

    for key in fileDict:
        # panel number
        pNum = key.decode()

        # resetting the active directory - changes when saving
        os.chdir(directoryPath)
        file1, file2, file3, file4, drDiam1, drDiam2, drDiam3, drDiam4, arType1, arType2, arType3, arType4 = onePanel(fileDict, key)

        blankArr = np.array([None])
        img1, img2, img3, img4 = blankArr, blankArr, blankArr, blankArr

        if file1:
            img1, offDiff1 = drawOffset(file1, drDiam1, arType1)
        if file2:
            img2, offDiff2 = drawOffset(file2, drDiam2, arType2)
        if file3:
            img3, offDiff3 = drawOffset(file3, drDiam3, arType3, 1)
        if file4:
            img4, offDiff4 = drawOffset(file4, drDiam4, arType4, 1)


        meanOffDiff, minOffDiff, maxOffDiff = fullOffStat(offDiff1, offDiff2, offDiff3, offDiff4)

        # logic for when one image is missing
        if img1.any() != None:
            imgHeight, imgWidth, bigImage = imgDimensions(img1)
        elif img2.any() != None:
            imgHeight, imgWidth, bigImage = imgDimensions(img2)
        elif img3.any() != None:
            imgHeight, imgWidth, bigImage = imgDimensions(img3)
        elif img4.any() != None:
            imgHeight, imgWidth, bigImage = imgDimensions(img4)

        #quadrant 1
        if img1.any() != None:
            bigImage[0:imgHeight,imgWidth:] = img1

        # quadrant 2
        if img2.any() != None:
            bigImage[0:imgHeight,0:imgWidth] = img2

        #quadrant 3
        if img3.any() != None:
            bigImage[imgHeight:, 0:imgWidth] = img3

        #quadrant 4
        if img4.any() != None:
            bigImage[imgHeight:, imgWidth:] = img4


        addTextStats(bigImage, imgHeight, imgWidth, pNum, meanOffDiff, minOffDiff, maxOffDiff)



        # change path for saving
        os.chdir('C:/Users/joshuaj/Documents/Extra/Learning/opencv/Xray photos/PlOutput')

        # save new images to specified directory
        print(f'Saving file for Panel {pNum}')
        newFile = f'Panel {pNum} Registration.png'
        cv2.imwrite(newFile, bigImage)






if __name__ == "__main__":
    main()



