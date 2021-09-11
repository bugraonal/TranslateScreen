import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pystray import MenuItem
import win32gui


class MainWindow:
    def __init__(self, master, data):
        self.master = master
        self.data = data
        self.master.wm_attributes('-transparentcolor', self.master['bg'])
        self.master.geometry('300x300')
        self.master.resizable()
        self.master.title('Capture')
        self.master.attributes('-topmost', 'true')
        #self.master.overrideredirect(1)
        self.mainFrame = tk.Frame(self.master)
        self.configure()
        self.mainFrame.pack()
        self.optionsVisible = False

    def configure(self):
        self.mainFrame.pack_forget()
        self.mainFrame = tk.Frame(self.master)
        optionButton = tk.Button(self.mainFrame, text='Options', command=self.options_window, bg='white')
        optionButton.place(x=0, y=0)
        quitButton = tk.Button(self.mainFrame, text='Quit', command=self.master.quit, bg='white')
        quitButton.place(x=40, y=0)

    def options_window(self):
        self.optionsVisible = True
        self.window = tk.Toplevel(self.master)
        self.options = OptionsWindow(self.window, self.data)
        self.window.protocol("WM_DELETE_WINDOW", self.close_options)
    
    def close_options(self):
        self.optionsVisible=False
    
    def put_texts(self, boxes, translations):
        self.configure()
        for box, trans in zip(boxes, translations):
            label = tk.Label(self.mainFrame, text=trans, bg='white')
            label.place(x=box[0], y=box[1], width=box[2] - box[0], height=box[3] - box[1])
        self.mainFrame.pack(fill=tk.BOTH, expand=1)
        


class OptionsWindow:
    def __init__(self, master, data):
        self.master = master
        self.data = data
        self.master.geometry('500x650')
        self.master.title('Options')
        self.get_processes()
        self.configure()

    def update_preview(self):
        processed, boxes = self.data.get_previews()
        processedImg = processed.convert('RGB').resize((250, 250), Image.ANTIALIAS)
        processedImg = ImageTk.PhotoImage(processedImg)
        self.processedPanel = tk.Label(self.previewFrame, image=processedImg)
        self.processedPanel.image = processedImg

        boxesImg = boxes.resize((250, 250), Image.ANTIALIAS)
        boxesImg = ImageTk.PhotoImage(boxesImg)
        self.boxesPanel = tk.Label(self.previewFrame, image=boxesImg)
        self.boxesPanel.image = boxesImg
        
        self.processedPanel.grid(row=0, column=0)
        self.boxesPanel.grid(row=0, column=1)
        self.previewFrame.grid(row=1, column=0)

    def get_processes(self):
        entries = []
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                entries.append((hwnd, win32gui.GetWindowText(hwnd)))

        win32gui.EnumWindows(winEnumHandler, None)
        self.processes = entries
    
    def update_hwnd(self):
        self.get_processes()
        self.hwndCombo['values'] = [p[1] for p in self.processes]
    
    def configure(self):
        mainFrame = tk.Frame(self.master)
        mainFrame.pack()
        
        hwndFrame = tk.Frame(mainFrame)
        hwndVar = tk.StringVar()
        self.hwndCombo = ttk.Combobox(hwndFrame, textvariable = hwndVar)
        self.hwndCombo.bind('<<ComboboxSelected>>',
            lambda _ : self.data.set_param('hwnd', self.processes[self.hwndCombo.current()][0]))
        self.hwndCombo.pack(side=tk.LEFT)
        self.update_hwnd()
        hwndRefreshButton = tk.Button(hwndFrame, text='Refresh', command=self.update_hwnd)
        hwndRefreshButton.pack(side=tk.RIGHT)
        hwndFrame.grid(row=0, column=0)
        
        self.previewFrame = tk.Frame(mainFrame)
        self.update_preview()
        
        lowerFrame = tk.Frame(mainFrame)
        lowerLabel = tk.Label(lowerFrame, text='Lower Threshold')
        lowerVar = tk.IntVar(value=self.data.get_param('lower'))
        lowerScale = tk.Scale(lowerFrame, from_=0, to=255,
            variable=lowerVar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('lower', lowerVar.get()))
        lowerLabel.pack(side=tk.LEFT)
        lowerScale.pack(side=tk.RIGHT)
        lowerFrame.grid(row=2, column=0)

        higherFrame = tk.Frame(mainFrame)
        higherLabel = tk.Label(higherFrame, text='Higher Threshold')
        higherVar = tk.IntVar(value=self.data.get_param('higher'))
        higherScale = tk.Scale(higherFrame, from_=0, to=255,
            variable=higherVar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('higher', higherVar.get()))
        higherLabel.pack(side=tk.LEFT)
        higherScale.pack(side=tk.RIGHT)
        higherFrame.grid(row=3, column=0)

        higherKernelFrame = tk.Frame(mainFrame)
        higherKernelLabel = tk.Label(higherKernelFrame, text='Higher Kernel Size')
        higherKernelXvar = tk.IntVar(value=self.data.get_param('higher_kernel_size')[0])
        higherKernelYvar = tk.IntVar(value=self.data.get_param('higher_kernel_size')[1])
        higherKernelXscale = tk.Scale(higherKernelFrame, from_=1, to=50, resolution=2,
            variable=higherKernelXvar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('higher_kernel_size',
                (higherKernelXvar.get(), self.data.get_param('higher_kernel_size')[1])))
        higherKernelYscale = tk.Scale(higherKernelFrame, from_=1, to=50, resolution=2,
            variable=higherKernelYvar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('higher_kernel_size',
                (self.data.get_param('higher_kernel_size')[0], higherKernelYvar.get())))
        higherKernelLabel.pack(side=tk.LEFT)
        higherKernelXscale.pack(side=tk.RIGHT)
        higherKernelYscale.pack(side=tk.RIGHT)
        higherKernelFrame.grid(row=4, column=0)

        boxKernelFrame = tk.Frame(mainFrame)
        boxKernelLabel = tk.Label(boxKernelFrame, text='Box Kernel Size')
        boxKernelXvar = tk.IntVar(value=self.data.get_param('box_kernel_size')[0])
        boxKernelYvar = tk.IntVar(value=self.data.get_param('box_kernel_size')[1])
        boxKernelXscale = tk.Scale(boxKernelFrame, from_=1, to=50, resolution=2,
            variable=boxKernelXvar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('box_kernel_size',
                (boxKernelXvar.get(), self.data.get_param('box_kernel_size')[1])))
        boxKernelYscale = tk.Scale(boxKernelFrame, from_=1, to=50, resolution=2,
            variable=boxKernelYvar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('box_kernel_size',
                (self.data.get_param('box_kernel_size')[0], boxKernelYvar.get())))
        boxKernelLabel.pack(side=tk.LEFT)
        boxKernelXscale.pack(side=tk.RIGHT)
        boxKernelYscale.pack(side=tk.RIGHT)
        boxKernelFrame.grid(row=5, column=0)

        medianFrame = tk.Frame(mainFrame)
        medianLabel = tk.Label(medianFrame, text='Median Size')
        medianVar = tk.IntVar(value=self.data.get_param('median_size'))
        medianScale = tk.Scale(medianFrame, from_=1, to=20, resolution=2,
            variable=medianVar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('median_size', medianVar.get()))
        medianLabel.pack(side=tk.LEFT)
        medianScale.pack(side=tk.RIGHT)
        medianFrame.grid(row=6, column=0)

        closingKernelFrame = tk.Frame(mainFrame)
        closingKernelLabel = tk.Label(closingKernelFrame, text='Closing Kernel Size')
        closingKernelXvar = tk.IntVar(value=self.data.get_param('closing_kernel_size')[0])
        closingKernelYvar = tk.IntVar(value=self.data.get_param('closing_kernel_size')[1])
        closingKernelXscale = tk.Scale(closingKernelFrame, from_=1, to=50, resolution=2,
            variable=closingKernelXvar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('closing_kernel_size',
                (closingKernelXvar.get(), self.data.get_param('closing_kernel_size')[1])))
        closingKernelYscale = tk.Scale(closingKernelFrame, from_=1, to=50, resolution=2,
            variable=closingKernelYvar, orient=tk.HORIZONTAL,
            command=lambda _ : self.data.set_param('closing_kernel_size',
                (self.data.get_param('closing_kernel_size')[0], closingKernelYvar.get())))
        closingKernelLabel.pack(side=tk.LEFT)
        closingKernelXscale.pack(side=tk.RIGHT)
        closingKernelYscale.pack(side=tk.RIGHT)
        closingKernelFrame.grid(row=7, column=0)