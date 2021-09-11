import cv2
import numpy as np
try:
    from PIL import ImageFont, ImageDraw, Image
except ImportError:
    import Image
import pytesseract
from googletrans import Translator


dir = r'C:\Users\onalb\Desktop\TranslateScreen\references'

img = cv2.imread(dir + r'\..\resources\images\test6.png')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# lower threshhold
# filter text color loosley
ret, low_thresh = cv2.threshold(gray,145,255,cv2.THRESH_BINARY)
cv2.imshow('', low_thresh)
cv2.waitKey(0)

# higher threshhold
# filter text color more tightly
ret,high_thresh = cv2.threshold(gray, 200,255,cv2.THRESH_BINARY)
kernel = np.ones((10, 10), dtype=np.uint8)

# dilate higher threshold to get text area
high_dilate = cv2.dilate(high_thresh, kernel, iterations=1)

# combine lower and higher binaries
combined = cv2.bitwise_and(low_thresh, high_dilate)
cv2.imshow('', combined)
cv2.waitKey(0)

# Find text bounding boxes
kernel = np.ones((10, 30), dtype=np.uint8)
dilation = cv2.dilate(combined, kernel, iterations=1)
cv2.imshow('', dilation)
cv2.waitKey(0)

ctrs, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
drawn_boxes = cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)
boxes = []
for ctr in ctrs:
    x,y,w,h = cv2.boundingRect(ctr)
    boxes.append((x, y, x + w, y + h))
    cv2.rectangle(drawn_boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
cv2.imshow('', drawn_boxes)
cv2.waitKey(0)

# median filter
med = cv2.medianBlur(combined, 3)
cv2.imshow('', med)
cv2.waitKey(0)

# closing
kernel = np.ones((3,3),np.uint8)
closing = cv2.morphologyEx(med, cv2.MORPH_CLOSE, kernel)
cv2.imshow('', closing)
cv2.waitKey(0)

# invert black/white
inv = cv2.bitwise_not(closing)
cv2.imshow('', inv)
cv2.waitKey(0)

# Annotate translation on original image
annotated = img.copy()
text_offset = 10

fontpath = r'C:\Windows\Fonts\YuGoTHB.ttc'
img_pil = Image.fromarray(annotated)
draw = ImageDraw.Draw(img_pil)

translator = Translator()
for box in boxes:
    text_img = inv[box[1]:box[3], box[0]:box[2]]
    cv2.imshow('', text_img)
    cv2.waitKey(0)
    ocr = pytesseract.image_to_string(text_img, lang='jpn')
    ocr = ocr.replace('\n', '')
    if len(ocr) == 1:
        continue
    trans = translator.translate(ocr, dest='en', src='ja').text
    print(trans)
    if len(trans) > 1:
        font = ImageFont.truetype(fontpath, int(3 * w // len(trans)**0.5))
    else:
        font = ImageFont.truetype(fontpath, 14)
    draw.rectangle((box[0], box[1], box[2], box[3]), fill = (200, 200, 200, 0))
    draw.text((box[0], box[1]), trans, font = font, fill = (0,0,0,0), anchor='lt')

annotated = np.array(img_pil)
cv2.imshow('', annotated)
cv2.waitKey(0)

print(pytesseract.image_to_data(inv, lang='jpn', config='--psm 6'))

















