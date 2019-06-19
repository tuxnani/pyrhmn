import cv2
import numpy as np
import glob
base_dir = './'
final_dir = './'
i = 27
def mergeContour(intervals):
    merged = []
    
    mergedIntervalIndex = []
    for i, higher in enumerate(intervals):
        if not merged:
            merged.append(higher)
            mergedIntervalIndex.append([i])
        else:
            lower = merged[-1]
            # test for intersection between lower and higher:
            # we know via sorting that lower[0] <= higher[0]
            if higher[0] <= lower[1] and higher[1]<=lower[1]:
                upper_bound = max(lower[1], higher[1])
                merged[-1] = (lower[0], upper_bound)
                mergedIntervalIndex[-1].append(i)
                # replace by merged interval
            else:
                merged.append(higher)
                mergedIntervalIndex.append([i])
    
    #print (merged_interval_index)
    return mergedIntervalIndex

l = [(3, 4), (5, 7), (6, 12), (10, 12), (11, 116) ]
mergeContour(l)


def addBorder(img, bordersize):
    return cv2.copyMakeBorder(img, top=bordersize, bottom=bordersize,
                              left=bordersize, right=bordersize,
                              borderType= cv2.BORDER_CONSTANT, 
                              value=[255,255,255] )

def segmentImage(baseImage, imFloodfillInv, mask, name):
    
    _, thresh = cv2.threshold(imFloodfillInv, 127, 255, 0)
    _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)
    
    contoursWithRect = []
    countourBoundary = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        contoursWithRect.append(((x, x+w), (y, y+h), contour))
        
    
    #sort according to occurance of contours
    #The format of each element is : ((x, x+w), (y, y+h), contour)
    contoursWithRect = sorted(contoursWithRect, key = lambda x : x[0][0])
    
    #contains Bounding Interval of countours
    #The format of each element is : (x, x+w)
    countourBoundary = [x[0] for x in contoursWithRect]
    
    #contours in sorted order 
    contours = [x[-1] for x in contoursWithRect]
    
    #Contains list of merged countours
    mergeContourBoundary = mergeContour(countourBoundary)
    
    #add border to base Image to make it size of contours generated
    bordersize=1
    baseImageWithBorder = addBorder(baseImage, bordersize)
    
    baseImageWithBorderInv = 255 - baseImageWithBorder
    
    
    for interval in mergeContourBoundary:
        color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        cont = [contours[i] for i in interval]
        imgContour = cv2.drawContours(color, 
                                       cont, -1, (255,255,255), -1,8)
       
        res = cv2.bitwise_and(baseImageWithBorderInv,
                              imgContour)
        #change dir location to segmented image folder                      
        cv2.imwrite("sampleWordImageBB/contour/"+name.split('.')[0]+
                    '_'+str(interval)+'.png',res)

def boundingBox(img, imFloodfillInv, name):
    connectivity = 8
    #output = cv2.connectedComponentsWithStats(im_floodfill_inv, connectivity)
    labelnum, _, contours, _ = cv2.connectedComponentsWithStats(
        imFloodfillInv, connectivity)
    
    label_range = range(1, labelnum)
    contours = sorted(contours, key = lambda x : x[0])
    bb_img = img.copy()
      
    for label in xrange(1,labelnum):
        x,y,w,h,size = contours[label]
        bb_img = cv2.rectangle(bb_img, (x,y), (x+w,y+h), (0,0,255), 1)
        
    
    #change it to BB image folder
    cv2.imwrite("sampleWordImageBB/BB/"+name,bb_img)

def arabicTextProcessing(path):
    name = path.split('/')[-1]
    base_image = cv2.imread(path)
    gray_image = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
    gray_image = gray_image.astype('uint8')
    Iedge = cv2.Canny(gray_image, 100, 200)
    
    #print(image.shape, gray_image.shape)
    #dilation : small size of kernel- can segment between much closer objects and accurately
    #according to experiment and trying several values for kernel:
    #large value of first emlement of kernel such as (15, 3) helps in dilate image
    #vertically. Large value of first element of kernel is useful for
    #creating bounding box for text so that we can include the dots
    #present in text in one Bounding Box. 
    #small values of both elements of kernel such as (3, 3)helps in segmenting and
    #creating bounding box for number 
    kernel = np.ones((20,3), np.uint8)
    img_dilation = cv2.dilate(Iedge, kernel, iterations=1)
    #cv2.imwrite("sampleWordImageBB/"+name.split('.')[0]+"dilate.png",img_dilation)
    
    
    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    th, im_th = cv2.threshold(img_dilation, 220, 255, 
                              cv2.THRESH_BINARY_INV);
    #print(im_th.shape)
    #cv2.imwrite("sampleWordImageBB/"+name.split('.')[0]+"dilate.png",im_th)
    #im_th = img_dilation
    
    # Copy the thresholded image.
    im_floodfill = im_th.copy()
    
    h, w = im_th.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    mask1 = np.zeros((h+10, w+10), np.uint8)
    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (0,0), 255)
    
    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    
    
    
    #cv2.imwrite("sampleWordImageBB/dilate/"+name,im_floodfill_inv)
    
    segmentImage(base_image, im_floodfill_inv, mask, name)
    
    
    boundingBox(base_image, im_floodfill_inv, name)

name = "3.jpg"
arabicTextProcessing(base_dir+name)


