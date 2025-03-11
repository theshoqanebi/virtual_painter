import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
import HandTrackingModule as HTM

folderPath = "images"
myList = os.listdir(folderPath)

brushThickness = 12

overlayList = []
thicknessOptions = [5, 10, 15, 20, 25]

for imgPath in myList:
    image = cv2.imread(f'{folderPath}/{imgPath}')
    overlayList.append(image)

header = overlayList[0]
colors = {
    "Red": (0, 0, 255),
    "Yellow": (0, 255, 255),
    "Purple": (125, 0, 125),
    "Black": (0, 0, 0)
}
drawColor = colors["Red"]
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
imgCanvas = np.zeros((720, 1280, 3), np.uint8)
detector = HTM.HandDetector(detection_con=0.85)
xp, yp = 0, 0

ShapeSquare = 1
ShapeRectangle = 2
ShapeEllipse = 3
ShapeCircle = 4

showOptions = False
fullscreen = False
drawShape = False
shapeStarted = False
shapeP1 = None
shapeType = None

# Create the main window
root = tk.Tk()
root.title("Virtual Painter")

# Set initial window size
window_width = 1280
window_height = 720
root.geometry(f"{window_width}x{window_height}")

# Create a Tkinter Canvas widget
canvas = Canvas(root, width=window_width, height=window_height)
canvas.pack()


# Function to handle window resizing
def on_resize(event):
    global window_width, window_height, canvas
    window_width = event.width
    window_height = event.height
    canvas.config(width=window_width, height=window_height)


# Bind window resize event
root.bind("<Configure>", on_resize)


# Function to update the frame
def update_frame():
    global header, drawColor, xp, yp, imgCanvas, shapeType, shapeStarted, shapeP1, brushThickness, showOptions, drawShape, window_width, window_height

    success, img = cap.read()
    img = cv2.flip(img, 1)

    img[0:156, 0:window_width] = header

    img = detector.find_hands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x_middle, y_middle = lmList[12][1:]
        fingers = detector.fingersUp()

        if fingers[1] and fingers[2]:
            showOptions = True
            xp, yp = 0, 0
        else:
            showOptions = False

        if showOptions:
            if y1 < 146:
                if 37 < x1 < 130:
                    shapeType = ShapeEllipse
                    drawShape = True
                    header = overlayList[1]
                elif 170 < x1 < 276:
                    shapeType = ShapeCircle
                    drawShape = True
                    header = overlayList[2]
                elif 302 < x1 < 439:
                    shapeType = ShapeRectangle
                    drawShape = True
                    header = overlayList[3]
                elif 470 < x1 < 560:
                    shapeType = ShapeSquare
                    drawShape = True
                    header = overlayList[4]
                elif 594 < x1 < 757:
                    drawColor = colors["Red"]
                    header = overlayList[5]
                elif 773 < x1 < 936:
                    drawColor = colors["Yellow"]
                    header = overlayList[6]
                elif 961 < x1 < 1119:
                    drawColor = colors["Purple"]
                    header = overlayList[7]
                elif 1126 < x1 < 1264:
                    drawColor = colors["Black"]
                    header = overlayList[8]

            if 1240 - 40 < x1 < 1240 + 40 and 186 - 40 < y1 < 186 + 40:
                imgCanvas = np.zeros((720, 1280, 3), np.uint8)

        # Drawing shapes or freehand
        if fingers[1] and not fingers[2]:
            if drawShape and not shapeStarted:
                shapeStarted = True
                shapeP1 = (x1, y1)  # Set starting point for shape
            elif not drawShape and not shapeStarted:
                cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)

                if xp == 0 and yp == 0:
                    xp, yp = x1, y1


                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                xp, yp = x1, y1
        elif shapeStarted:
            if shapeP1:  # Ensure shapeP1 is not None
                p1 = (shapeP1[0], shapeP1[1])
                p2 = (x1, y1)

                if p2[0] > p1[0]:
                    p3 = p2
                    p2 = p1
                    p1 = p3

                if p2[1] > p1[1]:
                    p3 = (p2[0], p1[1])
                    p4 = (p1[0], p2[1])

                    p1 = p3
                    p2 = p4

                if shapeType == ShapeEllipse:
                    xp = int((p2[0] - p1[0]) / 2)
                    yp = int((p2[1] - p1[1]) / 2)
                    center = (p1[0] + xp, p1[1] + yp)
                    axes = (abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))
                    cv2.ellipse(
                        imgCanvas,
                        center=center,
                        axes=axes,
                        color=drawColor,
                        thickness=brushThickness,
                        angle=0,
                        startAngle=0,
                        endAngle=360
                    )
                elif shapeType == ShapeCircle:
                    axes = (abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))
                    alen = axes[1] if axes[0] > axes[1] else axes[0]
                    center = (int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2))
                    cv2.circle(
                        imgCanvas,
                        center=center,
                        radius=alen,
                        color=drawColor,
                        thickness=brushThickness
                    )

                elif shapeType == ShapeRectangle:
                    cv2.rectangle(imgCanvas, p1, p2, drawColor, brushThickness)
                elif shapeType == ShapeSquare:
                    xlen = p2[0] - p1[0]
                    ylen = p2[1] - p1[1]
                    if xlen > ylen:
                        xlen = ylen
                    elif ylen > xlen:
                        ylen = xlen
                    cv2.rectangle(imgCanvas, p1, (p1[0] + xlen, p1[1] + xlen), drawColor, brushThickness)

                shapeStarted = False
                drawShape = False
                shapeP1 = None
                shapeType = None
                header = overlayList[0]

    img = cv2.add(img, imgCanvas)
    cv2.circle(img, (window_width - 55, 210), 50, (0, 0, 255), -1)
    cv2.putText(img, "Clean", (window_width - 90, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Convert the frame to a format Tkinter can display
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img)

    # Resize the image to fit the window size
    img_resized = img_pil.resize((window_width, window_height), Image.Resampling.LANCZOS)

    img_tk = ImageTk.PhotoImage(img_resized)

    # Update the canvas with the new image
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.image = img_tk

    # Schedule the next frame update
    canvas.after(10, update_frame)


# Start the video stream
update_frame()

# Run the Tkinter event loop
root.resizable(False, False)
root.iconbitmap("images/app_icon.ico")
root.mainloop()

cap.release()
cv2.destroyAllWindows()
