import tkinter as tk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import cv2
import numpy as np
from matplotlib.pyplot import show
from PIL import ImageTk ,Image
import matplotlib.pyplot as plt
import subprocess
from preprocess import *

#----------------------------------------------------------------------------------------------------------------------------------

UI = tk.Tk()

intro = tk.Frame(UI)
intro.grid(row=0,column=0,sticky='nsew')
mode = tk.Frame(UI)
mode.grid(row=0,column=0,sticky='nsew')

UI.title("FINAL IMAGE PROCESSING PROJECT")
UI.geometry("1200x750")
UI.resizable(False, False)
cam_label = None  # camlabel start is none 
result_label = None
capture = False

def captured_image_process(image):
    preprocessed_image, contours = preprocess(image)
    maze_corner_tl, maze_corner_tr, maze_corner_bl, maze_corner_br = find_maze_corners(preprocessed_image, contours)
    warped_image = apply_perspective_warp(preprocessed_image, maze_corner_tl, maze_corner_tr, maze_corner_bl, maze_corner_br)
    return warped_image

def draw_rectangle(frame, x, y, width, height):
    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
    
def raise_frame(frame):
    frame.tkraise()
    global cam_label
    if frame == mode and cam_label is None:
        cam_label = tk.Label(mode)
        cam_label.place(x= 200, y = 80)
        def update_frame():
            nonlocal cap
            ret, frame = cap.read()
            draw_rectangle(frame, 20, 20, 600, 440)
            if ret:
                # Convert the frame from BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize 
                frame_resized = cv2.resize(frame_rgb, (800, 600))
                # Convert the resized frame to ImageTk format
                img = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
                # Update the image in the Tkinter label widget
                cam_label.config(image=img)
                cam_label.image = img
                global capture
                if capture:
                    captured_img = frame[20:20+440, 20:20+600]
                    cv2.imwrite("cap0.jpg", captured_img)
                    cv2.imshow("captured image", captured_img)
                    captured_img = captured_image_process(captured_img)
                    cv2.imshow("preprocess image", captured_img)
                    cv2.imwrite("cap.jpg", captured_img)
                    capture=False

            cam_label.after(10, update_frame)
        cap = cv2.VideoCapture(0)
        update_frame()
        
def capture_realtime():
    global capture
    capture = True

modebg= Image.open("mode.jpg")
bgmode= ImageTk.PhotoImage(modebg)
backgroundModeLabel = tk.Label(mode, image= bgmode)
backgroundModeLabel.image = bgmode
backgroundModeLabel.place(x=0, y=0, relwidth=1, relheight=1)

realtime = tk.Button(mode , fg = ('black'), bg = ('green') , text= "Capture", font = ('arial'),height= 2 , width= 10, activebackground= ('red'), command= capture_realtime)
realtime.place(x= 200, y = 10)

solve_maze = lambda:subprocess.Popen(args=['python', r'MazeIO.py'])
browsimg = tk.Button(mode , fg = ('black'), bg = ('green') , text= "Select Img", font = ('arial'),height= 2 , width= 10, activebackground= ('red'), command= solve_maze)
browsimg.place(x= 400, y = 10)

home = Button(mode, fg = ('black'), bg = ('green') , text= "Back", font = ('arial'),height= 2 , width= 10, activebackground= ('red'), command=lambda:raise_frame(intro))
home.place(x= 5, y = 10)
    
raise_frame(intro)
bgIMG= Image.open("background label.png")
bg= ImageTk.PhotoImage(bgIMG)
backgroundLabel = Label(intro, image= bg)
backgroundLabel.image = bg
backgroundLabel.grid(row=0,column=0,sticky='nsew')

start = Button(intro, fg = ('white'), bg = ('green') , text= "START", font = ('arial', 20),height= 2 , width= 10, activebackground= ('red'), command=lambda:raise_frame(mode))
start.place(x= 800, y = 350)

#------------------------------------------------------------------------------------------------------------------------------------------------------------

# Define an event to close the window
def close_win(e):
   UI.destroy()
   
UI.bind('<Escape>', lambda e: close_win(e))
UI.mainloop() 