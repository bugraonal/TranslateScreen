import win32gui
import win32ui
import win32con
from PIL import Image
import numpy as np
from ctypes import windll

class ScreenCapture:

    def __init__(self):
        return

    def capture(self, hwnd): 
        self.capture_hwnd = win32gui.FindWindow(None, 'Capture')
        if hwnd == '':
            return Image.open('../resources/images/test6.png')
        # Get capture window bounds
        cleft, ctop, cright, cbot = win32gui.GetWindowRect(self.capture_hwnd)
        
        # Get target window bounds
        tleft, ttop, tright, tbot = win32gui.GetWindowRect(hwnd)

        # find intersection relative to target
        x = max(0, cleft - tleft)
        y = max(0, ctop - ttop)
        w = min(tright, cright) - max(tleft, cleft)
        h = min(tbot, cbot) - max(ttop, ctop)

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0,0),(w, h) , dcObj, (x,y), win32con.SRCCOPY | win32con.CAPTUREBLT)

        #dataBitMap.SaveBitmapFile(cDC, 'screenshot.bmp')

        bmp_info = dataBitMap.GetInfo()
        bmp_str = dataBitMap.GetBitmapBits(True)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        return Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_str, 'raw', 'BGRX', 0, 1)
    
    def capture_v2(self, hwnd):
        self.capture_hwnd = win32gui.FindWindow(None, 'Capture')
        if hwnd == '':
            return Image.open('../resources/images/test6.png')
        # Get capture window bounds
        cleft, ctop, cright, cbot = win32gui.GetWindowRect(self.capture_hwnd)
        
        # Get target window bounds
        tleft, ttop, tright, tbot = win32gui.GetWindowRect(hwnd)

        # find intersection relative to target
        x = max(0, cleft - tleft)
        y = max(0, ctop - ttop)
        w = min(tright, cright) - max(tleft, cleft)
        h = min(tbot, cbot) - max(ttop, ctop)

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, tright - tleft, tbot - ttop)
        cDC.SelectObject(dataBitMap)
        
        result = windll.user32.PrintWindow(hwnd, cDC.GetSafeHdc(), 2)
        
        bmp_info = dataBitMap.GetInfo()
        bmp_str = dataBitMap.GetBitmapBits(True)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        
        return Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_str, 'raw', 'BGRX', 0, 1).crop((x, y, min(tright, cright) - tleft, min(tbot, cbot) - ttop))
        
        