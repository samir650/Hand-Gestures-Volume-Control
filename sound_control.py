import cv2
import numpy as np
import mediapipe as mp
import time
import Hand_Tracking_Module as htm
import math
from pynput.keyboard import Key, Controller
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

keyboard = Controller()
wCam, hCam = 1280, 720

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.HandDetector(detectionConf=0.5)

# Initialize audio settings outside the loop for efficiency
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate( IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

while True:
    success, img = cap.read()
    img = detector.find_hands(img)
    lmList = detector.find_position(img)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb coordinates
        x2, y2 = lmList[8][1], lmList[8][2]  # Index finger coordinates
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Center point

        cv2.circle(img, (x1, y1), 10, (255, 0, 0), -1)  # Draw circles
        cv2.circle(img, (x2, y2), 10, (255, 0, 0), -1)
        cv2.circle(img, (cx, cy), 10, (255, 0, 0), -1)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

        length = math.hypot(x2 - x1, y2 - y1)  # Distance between thumb and index

        vol = np.interp(length, [50, 350], [minVol, maxVol])  # Convert length to volume level
        volBar = np.interp(length, [50, 350], [400, 150])
        volDeg = np.interp(length, [50, 350], [0, 100])

        volume.SetMasterVolumeLevel(vol, None)

        print(length, " ", vol)

        if length <= 50:
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), -1)
        if length >= 350:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), -1)

        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volDeg)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
