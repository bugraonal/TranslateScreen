from process import ImageProcessor
from ui import MainWindow
from data import DataController
from capture import ScreenCapture
from process import ImageProcessor
import tkinter as tk
from threading import Thread, Lock
import time
from PIL import Image
import numpy as np
import cv2

def process_image():
    img = cv2.imread('../resources/images/test6.png')
    while running:
        prev = img
        img = capture.capture_v2(data.get_param('hwnd'))
        img = np.array(img)
        if img.shape == prev.shape:
            if cv2.absdiff(img, prev).sum() == 0:
                continue
        else:
            continue
        translations, coords, processed, drawn_boxes = processor.process_v2(img)
        data.set_previews(Image.fromarray(processed), Image.fromarray(drawn_boxes))
        window.put_texts(coords, translations)
        if window.optionsVisible:
            window.options.update_preview()
        time.sleep(0.005)

def stop():
    running = False

if __name__ == "__main__":
    root = tk.Tk()
    dataMutex = Lock()
    data = DataController(dataMutex)
    capture = ScreenCapture()
    processor = ImageProcessor(data)
    window = MainWindow(root, data)
    running = True
    
    backgroundThread = Thread(target=process_image)
    backgroundThread.start()
    
    root.mainloop()
    #root.protocol("WM_DELETE_WINDOW", stop)
    running = False