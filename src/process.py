import cv2
import numpy as np
import pytesseract
from googletrans import Translator


class ImageProcessor:

    def __init__(self, data):
        self.data = data
    
    def process(self, img):
        gs = self.gray(img)
        bin = self.threshold(gs , self.data.get_param('lower'),
            self.data.get_param('higher'), self.data.get_param('higher_kernel_size'))
        coords, drawn_boxes = self.find_bounding_boxes(bin, img, self.data.get_param('box_kernel_size'))
        med = self.median_filter(bin, self.data.get_param('median_size'))
        close = self.closing(med, self.data.get_param('closing_kernel_size'))
        processed = self.invert(close)
        
        translations = self.ocr(processed, coords)
        
        return translations, coords, processed, drawn_boxes
    
    def process_v2(self, img):
        gs = self.gray(img)
        bin = self.threshold(gs , self.data.get_param('lower'),
            self.data.get_param('higher'), self.data.get_param('higher_kernel_size'))
        med = self.median_filter(bin, self.data.get_param('median_size'))
        close = self.closing(med, self.data.get_param('closing_kernel_size'))
        processed = self.invert(close)
        coords, drawn_boxes, lines = self.find_lines_v2(processed, img)
        
        translations = self.translate(lines)
       
        return translations, coords, processed, drawn_boxes
    
    def gray(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def threshold(self, img, lower, higher, kernel_size):
        # lower threshhold
        # filter text color loosley
        ret, low_thresh = cv2.threshold(img, lower, 255, cv2.THRESH_BINARY)

        # higher threshhold
        # filter text color more tightly
        ret,high_thresh = cv2.threshold(img, higher, 255, cv2.THRESH_BINARY)
        
        # dilate higher threshold to get text area
        kernel = np.ones(kernel_size, dtype=np.uint8)
        high_dilate = cv2.dilate(high_thresh, kernel, iterations=1)

        # combine lower and higher binaries
        return cv2.bitwise_and(low_thresh, high_dilate)

    def find_bounding_boxes(self, processed, original, kernel_size):
        # Find text bounding boxes
        drawn = original.copy()
        kernel = np.ones(kernel_size, dtype=np.uint8)
        dilation = cv2.dilate(processed, kernel, iterations=1)

        ctrs, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for ctr in ctrs:
            x,y,w,h = cv2.boundingRect(ctr)
            boxes.append((x, y, x + w, y + h))
            cv2.rectangle(drawn, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return boxes, drawn

    def find_lines(self, processed, original):
        # Find text bounding boxes
        drawn = original.copy()
        characters = pytesseract.image_to_boxes(processed, lang='jpn').split('\n')
        print(characters)
        tolerance = 10
        char, x1, y1, x2, y2, _ = characters[0].split(' ')
        x1, y1, x2, y2 = int(x1), processed.shape[0] - int(y1), int(x2), processed.shape[0] - int(y2)
        currentBox = [x1, y1, x2, y2]
        boxes = []
        lines = [char]
        prevY = y2
        for line in characters[1:]:
            if line.count(' ') < 5:
                continue
            char, x1, y1, x2, y2, _ = line.split(' ')
            x1, y1, x2, y2 = int(x1), processed.shape[0] - int(y1), int(x2), processed.shape[0] - int(y2)
            if abs(y2 - prevY) <= tolerance:
                lines[-1] += char
                if x1 < currentBox[0]:
                    currentBox[0] = x1
                if y1 < currentBox[1]:
                    currentBox[1] = y1
                if x2 > currentBox[2]:
                    currentBox[2] = x2
                if y2 > currentBox[3]:
                    currentBox[3] = y2
            else:
                lines.append(char)
                boxes.append(tuple(currentBox))
                currentBox = [x1, y1, x2, y2]
            prevY = y2            
        boxes.append(tuple(currentBox))
        for box in boxes:
            cv2.rectangle(drawn, (box[0], box[1]), (box[1], box[2]), (0, 255, 0), 2)
        return boxes, drawn, lines
    
    def find_lines_v2(self, processed, original):
        # Find text bounding boxes
        drawn = original.copy()
        boxes = []
        characters = pytesseract.image_to_data(processed, lang='jpn').split('\n')
        lines = []
        for line in characters[1:]:
            entry = line.split()
            if len(entry) == 11:
                level, _, _, par_num, _, _, left, top, width, height, _ = entry
                text = ' '
            elif len(entry) == 12:
                level, _, _, par_num, _, _, left, top, width, height, _, text = entry
            else:
                continue
            level, par_num, left, top, width, height = int(level), int(par_num), int(left), int(top), int(width), int(height)
            if level == 3:
                boxes.append((left, top, left + width, top + height))
                cv2.rectangle(drawn, (left, top), (left + width, top + height), (0, 255, 0), 0)
            if level == 5:
                if par_num > len(lines):
                    lines.append(text)
                else:
                    lines[par_num - 1] += text
        return boxes, drawn, lines
    
    def translate(self, lines):
        translations = []
        translator = Translator()
        for line in lines:
            try:
                translations.append(translator.translate(line, dest='en', src='ja').text)
            except:
                translations.append('')
        return translations
    
    def median_filter(self, img, size):
        # median filter
        return cv2.medianBlur(img, size)

    def closing(self, img, kernel_size):
        # closing
        kernel = np.ones(kernel_size, np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    def invert(self, img):
        # invert black/white
        return cv2.bitwise_not(img)

    def ocr(self, processed, box_coords):
        translator = Translator()
        texts = []
        for coord in box_coords:
            text_img = processed[coord[1]:coord[3], coord[0]:coord[2]]
            ocr = pytesseract.image_to_string(text_img, lang='jpn', config='--psm 7')
            ocr = ocr.replace('\n', '')
            if len(ocr) == 1:
                texts.append("")
                continue
            try:
                trans = translator.translate(ocr, dest='en', src='ja').text
                texts.append(trans)
            except:
                texts.append('')
        return texts