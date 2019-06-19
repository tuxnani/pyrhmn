import cv2
import pytesseract

filename = '3.jpg'


img = cv2.imread(filename)
h, w, _ = img.shape 


boxes = pytesseract.image_to_boxes(img) 


for b in boxes.splitlines():
    b = b.split(' ')
    img = cv2.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 0), 2)


cv2.imshow(filename, img)
cv2.waitKey(0)
