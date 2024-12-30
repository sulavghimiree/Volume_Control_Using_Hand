import cv2
import time
import numpy as np
import Hand_tracking_module as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

Wcam, Hcam = 640, 480

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]



cap = cv2.VideoCapture(0)
cap.set(3, Wcam)
cap.set(4, Hcam)
pTime = 0

detector = htm.HandTrackingModule(detectionCon=0.7)
vol = 0
volBar = 400
volper = 0
while True:
    ret, frame = cap.read()
    frame = detector.findHands(frame)

    lmList = detector.findPosition(frame, draw=False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        #print(length)

        # Hand range 50 - 250
        # Volume range -65 - 0

        vol = np.interp(length, [50, 250], [minVol, maxVol])
        volBar = np.interp(length, [50, 250], [400, 150])
        volper = np.interp(length, [50, 250], [0, 100])
        print(int(length),vol)
        volume.SetMasterVolumeLevel(vol, None)

        if(length <50):
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        elif(length > 250):
            cv2.circle(frame, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
        
    cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(frame, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(frame, f'{int(volper)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2) 
    


    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(frame, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
    cv2.imshow('Frame', frame)
    cv2.waitKey(1)