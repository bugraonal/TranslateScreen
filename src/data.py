import numpy as np
from PIL import Image


class DataController:
    def __init__(self, dataMutex):
        self.params = {
            'lower': 145,
            'higher': 200,
            'higher_kernel_size': (10, 10),
            'box_kernel_size': (10, 30),
            'median_size': 3,
            'closing_kernel_size': (3,3),
            'hwnd': ''
            }
        self.dataMutex = dataMutex
        self.previewProcessed = Image.open('../resources/images/test6.png').convert('LA')
        self.previewBoxes = Image.open('../resources/images/test6.png')

    def set_param(self, name, value):
        self.dataMutex.acquire()
        self.params[name] = value
        self.dataMutex.release()

    def get_param(self, name):
        self.dataMutex.acquire()
        ret = self.params[name]
        self.dataMutex.release()
        return ret

    def set_previews(self, processed, boxes):
        self.dataMutex.acquire()
        self.previewProcessed = processed
        self.previewBoxes = boxes
        self.dataMutex.release()

    def get_previews(self):
        return self.previewProcessed, self.previewBoxes