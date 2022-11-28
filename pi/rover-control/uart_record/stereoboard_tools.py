import numpy as np
import sys
import linecache
# import matplotlib.pyplot as plt
# import matplotlib.colors as matcol
# import Tkinter as tk
import threading
from time import sleep

# from matplotlib.widgets import Button

# from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
# from matplotlib._png import read_png
# from matplotlib.cbook import get_sample_data
SONAR_DISTANCES = {0: 15, 1: 10, 2: 9, 3: 8, 4: 7, 5: 2, 6: 1.8, 7: 1.7, 8: 1.4, 9: 1.2, 10: 1.0, 11: 0.8, 12: 0.5,
                   13: 0.3, 14: 0.2, 15: 0.1, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0}
AVERAGE_DATA = False
MAX_DATA = True
startedThreadDrawDrone = False
drawDroneOverSonar = False

stereoboardCommand = None


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def callback():
    print('pressed button')


drawDroneOverSonar = False


def changeDrawDrone():
    global drawDroneOverSonar
    drawDroneOverSonar = ~drawDroneOverSonar


def threadmain():
    t = tk.Tk()
    b = tk.Button(text='test', command=changeDrawDrone)
    b.grid(row=0)
    t.mainloop()


def changeFunctionBoardOne():
    global v
    v = 1


def changeFunctionBoardTwo():
    global v
    v = 2


def treadChooseFunction():
    global v
    t = tk.Tk()
    b = tk.Button(text='test', command=changeDrawDrone)
    c = tk.Radiobutton(t, text="One", command=changeFunctionBoardOne, value=1)
    d = tk.Radiobutton(t, text="Two", command=changeFunctionBoardTwo, value=2)
    b.grid(row=0)
    c.grid(row=1)
    d.grid(row=2)

    t.mainloop()


def draw_sonar_visualisation(matrix, height):
    global startedThreadDrawDrone
    if not startedThreadDrawDrone:
        thread.start_new_thread(threadmain, ())
        startedThreadDrawDrone = True
    try:
        plt.ion()
        r = matrix[1, :]
        r = (map(abs, map(int, r)))
        theta = np.arange(0, 2 * np.pi, (2 * np.pi) / len(r))

        ax = plt.subplot(111, polar=True)
        ax.clear()
        colors = []

        for element in matcol.cnames:
            colors.append(element)

        colors = colors[30::]
        if MAX_DATA:
            toPlot = np.zeros((1, matrix.shape[1]))
            for x in range(0, matrix.shape[1]):
                for y in range(0, matrix.shape[0]):
                    if matrix[y, x] > toPlot[0, x]:
                        toPlot[0, x] = matrix[y, x]

            colors = colors[30::]
            distances = np.array(toPlot[0, :])

            theta = np.append(theta, theta[0])
            distances = np.append(distances, distances[0])
            print('theta: ', theta.shape, ' distances: ', distances.shape)
            ax.plot(theta, distances, color=colors[0], linewidth=5)
        elif AVERAGE_DATA:
            toPlotSum = np.array(matrix[0])
            for i in range(1, height):
                toPlotSum += np.array(matrix[i])
            toPlotSum /= height
            toPlotSum = map(int, toPlotSum)
            distances = []
            for element in toPlotSum:
                distances.append(SONAR_DISTANCES[element])
            colors = colors[30::]

            theta = np.append(theta, theta[0])
            distances = np.append(distances, distances[0])
            ax.plot(theta, distances, color=colors[0], linewidth=5)
        else:
            for i in range(0, height):
                r = matrix[i, :]
                r = (map(abs, map(int, r)))
                ax.plot(theta, r, color=colors[i % len(colors)], linewidth=3)
        ax.set_rmax(20.0)
        ax.grid(True)

        if drawDroneOverSonar:
            print('drawing drone')
            arr_lena = read_png("ardrone2.png")
            xy = [0.3, 0.55]
            imagebox = OffsetImage(arr_lena, zoom=0.2)

            ab = AnnotationBbox(imagebox, xy,
                                xybox=(1.1, 1.1),
                                xycoords='data',
                                boxcoords="offset points")
            ax.add_artist(ab)

        plt.draw()
    except Exception as ex:
        PrintException()


# matrix=np.array([[0, 1, 2], [3, 4, 5]])
# draw_sonar_visualisation(matrix,2)


def fill_image_array(startSync, raw, width, height):
    try:
        line = 0

        # Initialise image
        img = np.zeros((height, width), dtype="uint8")

        # Fill the image arrays
        try:
            for i in range(startSync + 4, startSync + 4 + (width + 8) * height):
                if (raw[i] == 255) and (raw[i + 1] == 0) and (raw[i + 2] == 0):
                    if (raw[i + 3] == 128):  # Start Of Line
                        startOfLine = i + 4
                        endOfLine = (i + 4 + width)
                        img[line, :] = raw[startOfLine:endOfLine]
                        line += 1
                        i += width + 4
        except Exception:
            print('ended before end')
        return img
    except Exception as ecsfsf:
        PrintException()


def readDivergenceFromSerial(ser, currentBuffer):
    readSize = ser.inWaiting()
    while readSize == 0:
        readSize = ser.inWaiting()

    raw = bytearray(ser.read(readSize))

    for byte in raw:
        currentBuffer.append(int(byte))
    # print 'read: ',int(byte)
    startPosition = None
    lastResult = (-1, -1)

    try:
        for i in range(0, len(currentBuffer) - 3):
            # print currentBuffer[i]
            if (currentBuffer[i] == 255) and (currentBuffer[i + 1] == 0) and (currentBuffer[i + 2] == 0):
                # if (currentBuffer[i + 3] == 171):# End of Image
                #     return currentBuffer, i+4
                # print 'i: ', i, ' len currentBuffer: ', len(currentBuffer)
                if (currentBuffer[i + 3] == 171 and startPosition != None):  # End of Image
                    lastResult = (startPosition, i + 4)
                if currentBuffer[i + 3] == 175:  # Start of image
                    startPosition = i
    except Exception as e:
        PrintException()
    return currentBuffer, lastResult


def readPartOfImage(ser, currentBuffer):
    import struct
    global stereoboardCommand
    # Send data if needed
    if not stereoboardCommand == None:
        ser.write(struct.pack('!B', stereoboardCommand))
        stereoboardCommand = None

    # Read all available bytes
    readSize = ser.inWaiting()
    while readSize == 0:
        readSize = ser.inWaiting()

    raw = bytearray(ser.read(readSize))

    # Add all bytes to our total collection of bytes
    for byte in raw:
        currentBuffer.append(int(byte))
        # print 'read: ', int(byte)
    startPosition = None
    lastResult = (-1, -1)
    endOfImagesFound = 0
    startOfImagesFound = 0
    try:
        for i in range(0, len(currentBuffer) - 3):
            if (currentBuffer[i] == 255) and (currentBuffer[i + 1] == 0) and (currentBuffer[i + 2] == 0):
                if (currentBuffer[i + 3] == 171 and startPosition != None):  # End of Image
                    lastResult = (startPosition, i + 4)
                    endOfImagesFound += 1
                    break
                if currentBuffer[i + 3] == 175:  # Start of image
                    startPosition = i
                    startOfImagesFound += 1
    except Exception as e:
        PrintException()
    return currentBuffer, lastResult, endOfImagesFound


## Determines the start, length of one image, and the length of one line and the width and height
def determine_image_and_line_length(raw):
    startPosition = None
    lineLength = 0
    startLine = 0
    lineCount = 0
    startCounting = False
    for i in range(0, len(raw) - 3):
        if (raw[i] == 255) and (raw[i + 1] == 0) and (raw[i + 2] == 0):
            if (raw[i + 3] == 171 and startPosition != None):  # End of Image
                return startPosition, (i - startPosition), lineLength, lineCount
            if raw[i + 3] == 175:  # Start of image
                startPosition = i
                startLine = None
                startCounting = True
            if raw[i + 3] == 128:  # Start of line
                startLine = i
            if raw[i + 3] == 218 and startCounting:  # End of line
                lineLength = i - startLine - 4
                lineCount += 1
    return -1, -1, -1, -1


# Fill the image arrays
def fill_image_arrays(raw, startposition, size_of_one_image, width, heigth, disparity_offset_left,
                      disparity_offset_right, disparity_border, horizontalOffset):
    try:
        line = 0
        # Initialise images
        img = np.zeros((heigth + max(abs(disparity_offset_left), abs(disparity_offset_right)) * 3,
                        width * 2 + 2 * abs(horizontalOffset)))
        leftImage = np.zeros((heigth, width))
        rightImage = np.zeros((heigth, width))

        for i in range(startposition, size_of_one_image + startposition - 3):
            try:
                if (raw[i] == 255) and (raw[i + 1] == 0) and (raw[i + 2] == 0):
                    if (raw[i + 3] == 128):  # Start Of Line
                        startOfBuf = i + 4
                        endOfBuf = (i + 4 + width)
                        lineBuffer = raw[startOfBuf:endOfBuf]
                        rightLine = lineBuffer[1::2]
                        leftLine = lineBuffer[::2]

                        halfWay = disparity_border

                        # Line indicates the horizontal line
                        if horizontalOffset > 0:
                            indexStart = 1 + horizontalOffset * 2
                            img[line, 1:2 * halfWay:2] = leftLine[0:halfWay]
                            indexStart = 0
                            img[line + disparity_offset_left, 0:2 * halfWay:2] = rightLine[0:halfWay]
                            indexStart = 2 * halfWay + 1 + horizontalOffset * 2
                            img[line, indexStart:indexStart + width:2] = leftLine[halfWay::]
                            indexStart = 2 * halfWay
                            img[line + disparity_offset_right, indexStart:indexStart + width:2] = rightLine[halfWay::]

                            leftImage[line, :] = leftLine
                            rightImage[line, :] = rightLine
                        else:
                            indexStart = 1
                            img[line, 1:2 * halfWay:2] = leftLine[0:halfWay]
                            indexStart = 0 + abs(horizontalOffset) * 2
                            print(indexStart)
                            img[line + disparity_offset_left, indexStart:indexStart + 2 * halfWay:2] = rightLine[
                                                                                                       0:halfWay]
                            indexStart = 2 * halfWay + 1
                            img[line, indexStart:indexStart + width:2] = leftLine[halfWay::]
                            indexStart = 2 * halfWay + abs(horizontalOffset) * 2
                            print(indexStart)
                            img[line + disparity_offset_right, indexStart:indexStart + width:2] = rightLine[halfWay::]

                            leftImage[line, :] = leftLine
                            rightImage[line, :] = rightLine
                        line += 1
                    else:
                        if (raw[i + 3] == 171):
                            # End of Image
                            print('END OF IMAGE')
            except Exception as esfsfs:
                break
        return img, leftImage, rightImage
    except Exception as e:
        PrintException()


def saveImages(img, leftImage, rightImage, frameNumber, folderName):
    import cv2
    fileNameLeft = folderName + '/imageLeft' + str(frameNumber) + '.png'
    fileNameRight = folderName + '/imageRight' + str(frameNumber) + '.png'
    fileNameBoth = folderName + '/imageBoth' + str(frameNumber) + '.png'
    cv2.imwrite(fileNameBoth, img * 255)
    cv2.imwrite(fileNameLeft, leftImage * 255)
    cv2.imwrite(fileNameRight, rightImage * 255)


def createRedBlueImage(img, lineCount, lineLength):
    try:
        img2 = np.zeros((lineCount, lineLength, 3), dtype=('uint8'))

        for x in range(1, len(img)):
            for y in range(1, len(img[0])):
                if img[x, y] < 255:
                    img2[x, y, 0] = 255 - img[x, y]
                    img2[x, y, 2] = img[x, y]
                else:
                    img2[x, y, 1] = 255

        img2[img == 0, :] = [0, 0, 0]
        return img2
    except Exception as fsfs:
        PrintException()
