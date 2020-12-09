import sys
#import serial
# sys.path.append("C:\\opencv\\build\\python\\2.7") # should fix?
import copy
import numpy as np
import cv2
import math
import time
from time import strftime
import os
from numpy import array
import datetime
from pypylon import pylon
from pip._vendor.distlib.compat import raw_input
from save_to_XLS import Excel_Save_Rytis
from Plotting_light_dark import analysis_Matas


#Experiment parameters ================================
NumberOfMinutes = 1 # 1 means 10 minutes  2 means 20 minutes
Constant_darkness = 0 # 1 means constant darkness  0 means normal light cycles
LightOnDay = 1 # If constant darkenss from above, specify after how many days the light should be turned on. Two (2) means the next next day.
TankWidth = 200 # in mm
FishThreshold = 8 # 10 for 6-9dpf; 12 for 10-20dpf; 15 for > 20dpf

####### For Basler camera framet_rate, and frame resolution should be selected in pylon viewer
set_frame_rate= 15 #Choose from the following 9 fps
#FrameWidth = 2048  # 1280 for Basler camera and 1280 for Logitech camera # 640
#FrameHeight = 2048   # 480 #480
SavingSeconds = NumberOfMinutes*set_frame_rate * 60
n_tanks = 4 # number of tanks measured

## Tank1 ======================================
## Details for saving file
FishName1 = 'Fish-E3-01'
DOB1 = '30-11-2020'
FishType1 = 'TLEK'
#=============================================
## Tank2 ======================================
## Details for saving file
FishName2 = 'Fish-E3-02'
DOB2 = '30-11-2020'
FishType2 = 'TLEK'
#=============================================
## Tank3 ======================================
## Details for saving file
FishName3 = 'Fish-E3-03'
DOB3 = '30-11-2020'
FishType3 = 'TLEK'
#=============================================
## Tank4======================================
## Details for saving file
FishName4 = 'Fish-E3-04'
DOB4 = '30-11-2020'
FishType4 = 'TLEK'
#=============================================
GroupName = raw_input("Enter Group Name: ") # use the condition of the fish (fishtype) in this naming
save1=0
setupbox = 0
cv2.namedWindow('frame')
#=============================================
###### Path where the tracking data will be put
path_to_save = 'C:\\Users\\ASM_lab\\Desktop\\Matas_LightDark'
strt_time = time.strftime("%d_%b_%Y_%Hh%Mmin%Ss", time.localtime())
###### Adjust the trackers for the storage part
track1 = 0
track2 = 0
######
group_path = path_to_save + "\\" + GroupName + "_data_" + strt_time
os.mkdir(group_path)
##### Path where the videos will be stored
data = group_path + "\\videos\\" # This will save in the directory where your pycharm project is and will create a folder called data

tt81 = data + GroupName
tt82 = data + GroupName
tt83 = data + GroupName
tt84 = data + GroupName
tt85 = data + GroupName + "\\"



###### Capture image with specified size and frame rate
# conecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

#print(camera.Width.GetValue())
#print(camera.Height.GetValue())

fourcc = cv2.VideoWriter_fourcc('M','J','P','G') # Assign the fourcc words and initialize the video container
RGB = 0 # 0 if without color; 1 if coloured

#  Initialize for mouse events & time ====================================
# ====================================

boxes=[] # stores the dimensions of the regions of interest (ROI) drawn below
drawing = False # checks whether mouse is clicked and regions of interest are drawn
dummy= 0 # keeps track if 4 ROIs are selected #in if statement records inside those 4 boxes
mode = 0 # keeps track also if 4 ROIs are selected



StartDate = strftime("%y",) + strftime("%m",) + strftime("%d",)
StartDate1 = strftime("%d",)
if Constant_darkness == 1:
    LightOnDay = int(StartDate1) + LightOnDay
StartTime = strftime("%H",) + strftime("%M",) + strftime("%S",)
print('The experiment started from ...ymd & hms ____' + StartDate + ' & ' + StartTime)



def set_up_ROIs(event,x,y,flags,param): # drawing boxes
    if len(boxes) <= 8:
        global boxnumber, drawing, img, gray2, arr, arr1, arr2, arr3, arr4, arr5, dummy, mode, tank1a, tank2a, tank3a, tank4a, tank5a, tank6a # what does this do?
        boxnumner = 0
        if event == cv2.EVENT_LBUTTONDOWN: # record if left mouse button is pressed
            drawing = True
            sbox = [x, y] # records the coordinates of the pressing
            boxes.append(sbox)
        elif event == cv2.EVENT_MOUSEMOVE: #indicates that the mouse moved over the window
            if drawing == True:
                if len(boxes) == 1:
                    arr = array(gray5)
                    cv2.rectangle(arr,(boxes[-1][0],boxes[-1][-1]),(x, y),(0,0,255),1) #on gray5??? array draws a rectangle
                    cv2.imshow('frame',arr)
                    stamp = np.zeros((100,200,3))
                elif len(boxes) == 3:
                    arr1 = array(gray5)
                    cv2.rectangle(arr1,(boxes[-1][0],boxes[-1][-1]),(x, y),(0,0,255),1)
                    cv2.imshow('frame',arr1)
                elif len(boxes) == 5:
                    arr2 = array(gray5)
                    cv2.rectangle(arr2,(boxes[-1][0],boxes[-1][-1]),(x, y),(0,0,255),1)
                    cv2.imshow('frame',arr2)
                elif len(boxes) == 7:
                    arr3 = array(gray5)
                    cv2.rectangle(arr3,(boxes[-1][0],boxes[-1][-1]),(x, y),(0,0,255),1)
                    cv2.imshow('frame',arr3)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = not drawing
            ebox = [x, y]
            boxes.append(ebox)
            cv2.rectangle(gray5,(boxes[-2][-2],boxes[-2][-1]),(boxes[-1][-2],boxes[-1][-1]), (0,0,255),1)
            cv2.imshow('frame',gray5)
            if len(boxes) == 2:
                if not os.path.exists(tt81):
                    os.makedirs(tt81)
            elif len(boxes) == 4:
                if not os.path.exists(tt82):
                    os.makedirs(tt82)
            elif len(boxes) == 6:
                if not os.path.exists(tt83):
                    os.makedirs(tt83)
            elif len(boxes) == 8:
                if not os.path.exists(tt84):
                    os.makedirs(tt84)
            if len(boxes) == 8:
                mode = 1
                dummy = 1
                # cap.set(5,set_frame_rate)
                i=0



# Initialize the frame loop ====================================================
# ====================================================


kernel = np.ones((5, 5), np.uint8)

grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
image = converter.Convert(grabResult)
gray4 = image.GetArray()

#ret, gray4 = cap.read()
gray4 = np.float32(gray4)
gray7 = np.float32(gray4)
BackUpdate = 1
i=0
preset=0
tt91=0
tt92=0


data1=[]; # This is where output as stored as a list
data1Stamp=[]; # This is where frame count is stored
data2=[];
data2Stamp=[];
data3=[];
data3Stamp=[];
data4=[];
data4Stamp=[];


# Initialize position data - needed for later excel transformation from list to numpy array====================================
# ====================================
pos_data = np.zeros((n_tanks, 20000, 2))

while((i-preset+1) <= SavingSeconds ):
    # capture frame-by-frame
    CurrentTime1 = strftime("%H",) + strftime("%M",) + strftime("%S",)

    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    image = converter.Convert(grabResult)

    frame = image.GetArray()
    w,h,c= frame.shape
    # print(w,h,c)
    # print("cap: ", cap.isOpened(), "\nframe:", frame) for testing if camera works
    gray2 = frame[:]
    gray6 = copy.deepcopy(frame)

    if dummy == 1: #records inside these 4 boxes
        if setupbox == 0:
            starttime = datetime.datetime.now()
            frametime = starttime
            setupbox = 1
            # if RGB == 1:
            #     #Below is for RGB
            #     Tank1= cv2.VideoWriter(tt81 + '\\Tank1.avi',fourcc, 20.0, (boxes[1][0]-boxes[0][0],boxes[1][1]-boxes[0][1]))
            # else:
            #Below is for B/W
            Tank1= cv2.VideoWriter(tt81 + '\\Tank1.avi',fourcc, set_frame_rate, (boxes[1][0]-boxes[0][0],boxes[1][1]-boxes[0][1]),0) #boxes[1][0]-boxes[0][0],boxes[1][1]-boxes[0][1] = dimensions of the recording
            Tank2= cv2.VideoWriter(tt82 + '\\Tank2.avi',fourcc, set_frame_rate, (boxes[3][0]-boxes[2][0],boxes[3][1]-boxes[2][1]),0)
            Tank3= cv2.VideoWriter(tt83 + '\\Tank3.avi',fourcc, set_frame_rate, (boxes[5][0]-boxes[4][0],boxes[5][1]-boxes[4][1]),0)
            Tank4= cv2.VideoWriter(tt84 + '\\Tank4.avi',fourcc, set_frame_rate, (boxes[7][0]-boxes[6][0],boxes[7][1]-boxes[6][1]),0)
            Tank1_Raw= cv2.VideoWriter(tt81 + '\\Tank1_Raw.avi',fourcc, set_frame_rate, (boxes[1][0]-boxes[0][0],boxes[1][1]-boxes[0][1]),0)
            Tank2_Raw= cv2.VideoWriter(tt82 + '\\Tank2_Raw.avi',fourcc, set_frame_rate, (boxes[3][0]-boxes[2][0],boxes[3][1]-boxes[2][1]),0)
            Tank3_Raw= cv2.VideoWriter(tt83 + '\\Tank3_Raw.avi',fourcc, set_frame_rate, (boxes[5][0]-boxes[4][0],boxes[5][1]-boxes[4][1]),0)
            Tank4_Raw= cv2.VideoWriter(tt84 + '\\Tank4_Raw.avi',fourcc, set_frame_rate, (boxes[7][0]-boxes[6][0],boxes[7][1]-boxes[6][1]),0)

    if mode==1:
        cv2.rectangle(gray2,(boxes[0][0],boxes[0][1]),(boxes[1][0],boxes[1][1]), (0,0,255),1)
        cv2.rectangle(gray2,(boxes[2][0],boxes[2][1]),(boxes[3][0],boxes[3][1]), (0,0,255),1)
        cv2.rectangle(gray2,(boxes[4][0],boxes[4][1]),(boxes[5][0],boxes[5][1]), (0,0,255),1)
        cv2.rectangle(gray2,(boxes[6][0],boxes[6][1]),(boxes[7][0],boxes[7][1]), (0,0,255),1)

        if (i-preset+1) % SavingSeconds == 0:
            CurrentTime = strftime("%H",) + strftime("%M",) + strftime("%S",)
            tt91 = '%02d' % int((i-preset+1) / SavingSeconds)
            tt92 = '%02d' % (int((i-preset+1) / SavingSeconds)+1)
            print ('Files_' + tt91 + ' were saved at ' + CurrentTime)
            if int(tt91)<NumberOfMinutes:
                data1=[];
                data1Stamp=[];
                data2=[];
                data2Stamp=[];
                data3=[];
                data3Stamp=[];
                data4=[];
                data4Stamp=[];
                BackUpdate = 0
                gray7 = np.float32(gray2)
        if BackUpdate <=45:
            cv2.accumulateWeighted(gray2,gray7,0.1)
            gray8 = cv2.convertScaleAbs(gray7)
            BackUpdate = BackUpdate + 1
        else:
            if BackUpdate == 46:
                gray5 = gray8
                BackUpdate = 0

        elapsed_time=(datetime.datetime.now() - starttime).total_seconds()

        # Below is for Tank 1 tracking =======================================================
        img1 = cv2.subtract(gray2[boxes[0][1]:boxes[1][1],boxes[0][0]:boxes[1][0]],gray5[boxes[0][1]:boxes[1][1],boxes[0][0]:boxes[1][0]]) # global view #input - background, make sure same dimension
        img1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
        img1a = cv2.GaussianBlur(img1,(5,5),0)
        img1a = cv2.dilate(img1a,kernel,iterations=1)
        ret, img1b = cv2.threshold(img1a,FishThreshold,255,0)
        edged = cv2.Canny(img1b,25,200)
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse = True)[:2]

### tracking fish
        if len(cnts) == 0: #if no fish
            x = 0
            y = 0
            w = 0
            h = 0
            data1.append([i-preset+1,elapsed_time,0, 0, 0, 0, 0, 0])
        else:
            [x, y, w, h] = cv2.boundingRect(cnts[0]) #give rectangle
            data1.append([i-preset+1,elapsed_time,x+w/2+boxes[0][0], y+h/2+boxes[0][1], x, y, w, h]) #list of coordinates? i = 1634; preset = 15, elapsed_time, boxes
            cv2.rectangle(gray2,(x-2+boxes[0][0],y-2++boxes[0][1]),(x+w+2+boxes[0][0],y+h+2++boxes[0][1]),(0,255,0),2) #this just shows the rectangle ojn the screen ### 255 - color, 2, - thickness
            cv2.circle(gray2, (x+int(w/2)+boxes[0][0], y+int(h/2)+boxes[0][1]), 3, (0,0,255),-1)
            pos_data[0, i, :] = np.array([x + w / 2 + boxes[0][0], y + h / 2 + boxes[0][1]])

        # Below is for Tank 2 tracking =======================================================
        img2 = cv2.subtract(gray2[boxes[2][1]:boxes[3][1],boxes[2][0]:boxes[3][0]],gray5[boxes[2][1]:boxes[3][1],boxes[2][0]:boxes[3][0]]) # global view
        img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
        img2a = cv2.GaussianBlur(img2,(5,5),0)
        img2a = cv2.dilate(img2a,kernel,iterations=1)
        ret, img2b = cv2.threshold(img2a,FishThreshold,255,0)
        edged = cv2.Canny(img2b,25,200)
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse = True)[:2]
        if len(cnts) == 0:
            x = 0
            y = 0
            w = 0
            h = 0
            data2.append([i-preset+1,elapsed_time,0, 0, 0, 0, 0, 0])
        else:
            [x, y, w, h] = cv2.boundingRect(cnts[0])
            data2.append([i-preset+1,elapsed_time,x+w/2+boxes[2][0], y+h/2+boxes[2][1], x, y, w, h])
            cv2.rectangle(gray2,(x-2+boxes[2][0],y-2++boxes[2][1]),(x+w+2+boxes[2][0],y+h+2++boxes[2][1]),(0,255,0),2)
            cv2.circle(gray2, (x+int(w/2)+boxes[2][0], y+int(h/2)+boxes[2][1]), 3, (0,0,255),-1)
            pos_data[1, i, :] = np.array([x + w / 2 + boxes[2][0], y + h / 2 + boxes[2][1]])


        # Below is for Tank 3 tracking =======================================================
        img3 = cv2.subtract(gray2[boxes[4][1]:boxes[5][1],boxes[4][0]:boxes[5][0]],gray5[boxes[4][1]:boxes[5][1],boxes[4][0]:boxes[5][0]]) # global view
        img3 = cv2.cvtColor(img3,cv2.COLOR_BGR2GRAY)
        img3a = cv2.GaussianBlur(img3,(5,5),0)
        img3a = cv2.dilate(img3a,kernel,iterations=1)
        ret, img3b = cv2.threshold(img3a,FishThreshold,255,0)
        edged = cv2.Canny(img3b,25,200)
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse = True)[:2]
        if len(cnts) == 0:
            x = 0
            y = 0
            w = 0
            h = 0
            data3.append([i-preset+1,elapsed_time,0, 0, 0, 0, 0, 0])
        else:
            [x, y, w, h] = cv2.boundingRect(cnts[0])
            data3.append([i-preset+1,elapsed_time,x+w/2+boxes[4][0], y+h/2+boxes[4][1], x, y, w, h])
            cv2.rectangle(gray2,(x-2+boxes[4][0],y-2++boxes[4][1]),(x+w+2+boxes[4][0],y+h+2++boxes[4][1]),(0,255,0),2)
            cv2.circle(gray2, (x+int(w/2)+boxes[4][0], y+int(h/2)+boxes[4][1]), 3, (0,0,255),-1)
            pos_data[2, i, :] = np.array([x + w / 2 + boxes[4][0], y + h / 2 + boxes[4][1]])

        # Below is for Tank 4 tracking =======================================================
        img4 = cv2.subtract(gray2[boxes[6][1]:boxes[7][1],boxes[6][0]:boxes[7][0]],gray5[boxes[6][1]:boxes[7][1],boxes[6][0]:boxes[7][0]]) # global view
        img4 = cv2.cvtColor(img4,cv2.COLOR_BGR2GRAY)
        img4a = cv2.GaussianBlur(img4,(5,5),0)
        img4a = cv2.dilate(img4a,kernel,iterations=1)
        ret, img4b = cv2.threshold(img4a,FishThreshold,255,0)
        edged = cv2.Canny(img4b,25,200)
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse = True)[:2]
        if len(cnts) == 0:
            x = 0
            y = 0
            w = 0
            h = 0
            data4.append([i-preset+1,elapsed_time,0, 0, 0, 0, 0, 0])
        else:
            [x, y, w, h] = cv2.boundingRect(cnts[0])
            data4.append([i-preset+1,elapsed_time,x+w/2+boxes[6][0], y+h/2+boxes[6][1], x, y, w, h])
            cv2.rectangle(gray2,(x-2+boxes[6][0],y-2++boxes[6][1]),(x+w+2+boxes[6][0],y+h+2++boxes[6][1]),(0,255,0),2)
            cv2.circle(gray2, (x+int(w/2)+boxes[6][0], y+int(h/2)+boxes[6][1]), 3, (0,0,255),-1)
            pos_data[3, i, :] = np.array([x + w / 2 + boxes[6][0], y + h / 2 + boxes[6][1]])

        # storing the video =======================================================
        cv2.imshow('frame',gray2)

        gray2 = cv2.cvtColor(gray2,cv2.COLOR_BGR2GRAY)
        gray6 = cv2.cvtColor(gray6,cv2.COLOR_BGR2GRAY)

        tank1 = gray2[boxes[0][1]:boxes[1][1],boxes[0][0]:boxes[1][0]]
        tank1_raw = gray6[boxes[0][1]:boxes[1][1],boxes[0][0]:boxes[1][0]]
        Tank1.write(tank1)
        Tank1_Raw.write(tank1_raw)

        tank2 = gray2[boxes[2][1]:boxes[3][1],boxes[2][0]:boxes[3][0]]
        tank2_raw = gray6[boxes[2][1]:boxes[3][1],boxes[2][0]:boxes[3][0]]
        Tank2.write(tank2)
        Tank2_Raw.write(tank2_raw)
        data2Stamp.append([i-preset+1,elapsed_time])

        tank3 = gray2[boxes[4][1]:boxes[5][1],boxes[4][0]:boxes[5][0]]
        tank3_raw = gray6[boxes[4][1]:boxes[5][1],boxes[4][0]:boxes[5][0]]
        Tank3.write(tank3)
        Tank3_Raw.write(tank3_raw)
        data3Stamp.append([i-preset+1,elapsed_time])

        tank4 = gray2[boxes[6][1]:boxes[7][1],boxes[6][0]:boxes[7][0]]
        tank4_raw = gray6[boxes[6][1]:boxes[7][1],boxes[6][0]:boxes[7][0]]
        Tank4.write(tank4)
        Tank4_Raw.write(tank4_raw)
        data4Stamp.append([i-preset+1,elapsed_time])



        frametime = datetime.datetime.now()
        elapsed_time = 0


    else:
        preset = preset + 1
        if preset < 50:
            cv2.accumulateWeighted(gray2,gray4,0.1)
            gray5 = cv2.convertScaleAbs(gray4)
            cv2.imshow('frame',gray5)
        else:
            cv2.imshow('SelectROIs',gray2)


    cv2.setMouseCallback('frame',set_up_ROIs)


    i = i + 1


    if cv2.waitKey(dummy) & 0xFF == ord('q'): #changed from dummy to 1
        save1=1
        break

# Storing the coordinates in excel files =======================================================
### making pos_data
data1 = np.array(data1) # This is needed so that it is possible to get frame_arr and tstamp_arr for the excel sheet making


# other variables for input into Excel_Save_Rytis()
frame_arr = data1[:,0] # of Frames in sheet,
tstamp_arr = data1[:,1] # same as frame_arr
strt_time = time.strftime("%d_%b_%Y_%Hh%Mmin%Ss", time.localtime()) #strt_time - int (epoch time in s) - start time of the experiment?????? Where do I get? ### tt91 could be the start
tank_dims = np.zeros((4,4))#     tank_dims - np.array, where shape (# of Tanks, 4) - (x_pos,y_pos) pairs for 2 identifying points of each tank
tank_dims[0, :] = np.array((boxes[0][0],boxes[0][1],boxes[1][0],boxes[1][1])) #y,x?
tank_dims[1, :] = np.array((boxes[2][0],boxes[2][1],boxes[3][0],boxes[3][1]))
tank_dims[2, :] = np.array((boxes[4][0],boxes[4][1],boxes[5][0],boxes[5][1]))
tank_dims[3, :] = np.array((boxes[6][0],boxes[6][1],boxes[7][0],boxes[7][1]))
information = [FishName1, FishName2, FishName3, FishName4, DOB1, DOB2, DOB3, DOB4, GroupName, FishType1, FishType2, FishType3, FishType4, camera.Width.GetValue(), camera.Height.GetValue()]

if save1==1:
    CurrentTime = strftime("%H",) + strftime("%M",) + strftime("%S",)
    tt91 = '%02d' % int((i-preset+1) / SavingSeconds)
    tt92 = '%02d' % (int((i-preset+1) / SavingSeconds)+1)
    tt91 = int(tt91) + 1
    tt91 = str(tt91)
    print ('Files_' + tt91 + '_quit were saved at ' + CurrentTime)
    # tt99 = Excel_Save(tt91, GroupName, boxes, data1, data1Stamp, data2, data2Stamp, data3, data3Stamp, data4, data4Stamp, Tank1, Tank2, Tank3, Tank4, Tank1_Raw, Tank2_Raw, Tank3_Raw, Tank4_Raw, FishName1,DOB1,FishType1,FishName2,DOB2,FishType2,FishName3,DOB3,FishType3,FishName4,DOB4,FishType4,FrameWidth,FrameHeight,TankWidth,save1,tt85, set_frame_rate)
    Excel_Save_Rytis(strt_time, tank_dims, frame_arr, tstamp_arr, pos_data, group_path, information)

# When everything is done release the capture

camera.StopGrabbing()

CurrentDate = strftime("%y",) + strftime("%m",) + strftime("%d",)
CurrentTime = strftime("%H",) + strftime("%M",) + strftime("%S",)
Excel_Save_Rytis(strt_time, tank_dims, frame_arr, tstamp_arr, pos_data, group_path, information)


analysis_Matas(strt_time, GroupName, path_to_save, group_path, track1, track2)
### include the analysis function here
print('The experiment ended at ...ymd & hms ____' + CurrentDate + ' & ' + CurrentTime)

cv2.destroyAllWindows()
