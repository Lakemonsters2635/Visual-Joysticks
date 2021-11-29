import cv2
import cv2.cv2
import mediapipe as mp
import time
import pyvjoy

joystick = pyvjoy.VJoyDevice(1)

driveLeftHandStartX = 0.188
driveRightHandStartX = 0.5
gameToolHandStartX = 0.875
allHandsStartY = 0.5

startCircleSize = 20
circleLineThickness = 3

driveHandsMaxY = allHandsStartY - 0.333
driveHandsMinY = 2 * allHandsStartY - driveHandsMaxY

driveLeftHandMinX = 0
driveLeftHandMaxX = driveLeftHandStartX * 2

def mapPixelPercentToThrottle (x, min, max):
    return -((2/(min - max)) * (x - min) + 1)

cap = cv2.cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    h, w, c = img.shape

    # print(results.multi_hand_landmarks)

    # Notes on what gestures mean:
    # Closed fist : don't move
    # Left hand: joystick
    # Right hand: joystick
    # Gestures: Each finger represents a different button, raising multiple fingers can have simulataneous button pressing
    # Each gesture would be mapped to a button press
    # Number of hands: 3
    # Close fist for command hand means neutral
    # Command hand could represent different buttons with binary numbers
    # See if we can have audio feedback whenever buttons are activated, either different notes for different buttons or a voice that tells which button was pressed

    # Would want filtering on gestures, to ensure that if we want multiple buttons running at same time, that it can account for delays in putting up fingers

    # Visual feedback:
    # having a joystick neutral position on screen for driver to match fists to that place
    # Skeleton drawing of hands
    # When button is triggered, give indication

    # draw two lines on screen for the max and min boundaries of where the palm of the hand can move
    cv2.line(img, (0, int(driveHandsMaxY * h)), (w, int(driveHandsMaxY * h)), (0, 0, 255), 2)
    cv2.line(img, (0, int(driveHandsMinY * h)), (w, int(driveHandsMinY * h)), (0, 0, 255), 2)

    cv2.line(img, (int((1-driveLeftHandMinX) * w), 0), (int((1-driveLeftHandMinX) * w), h), (0, 0, 255), 4)
    cv2.line(img, (int((1-driveLeftHandMaxX) * w), 0), (int((1-driveLeftHandMaxX) * w), h), (0, 0, 255), 2)

    # draw three circles: 2 for starting "neutral" positions of the drivers hands and 1 for weapons commander hand
    cx, cy = int((1-driveLeftHandStartX) * w), int(allHandsStartY * h)
    cv2.circle(img, (cx, cy), startCircleSize, (255, 0, 0), circleLineThickness)

    cx = int((1 - driveRightHandStartX) * w)
    cv2.circle(img, (cx, cy), startCircleSize, (255, 0, 0), circleLineThickness)

    cx = int((1 - gameToolHandStartX) * w)
    cv2.circle(img, (cx, cy), startCircleSize, (0, 255, 0), circleLineThickness)

# X                                 Y
# int(driveHandsMinY * h))          -1.0
# int(driveHandsMaxY * h))          +1.0


    if results.multi_hand_landmarks:
        # print('Handedness:', results.multi_handedness)
        # print(results.multi_handedness[0])
        i = 0
        for handLms in results.multi_hand_landmarks:
            # print(handLms)
            for id, lm in enumerate(handLms.landmark):
                # print(id, lm)
                cx, cy = int(lm.x*w), int(lm.y*h)
                # print(id, cx, cy)
                if id == 0:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    tempPixelMapping = mapPixelPercentToThrottle(lm.y, driveHandsMinY, driveHandsMaxY)
                    joystick.set_axis(pyvjoy.HID_USAGE_Y, int(16384*(1+tempPixelMapping)))
                    tempPixelMapping = mapPixelPercentToThrottle(1 - lm.x, driveLeftHandMinX, driveLeftHandMaxX)
                    joystick.set_axis(pyvjoy.HID_USAGE_X, int(16384 * (1 + tempPixelMapping)))
                    print(tempPixelMapping)

                # figure out which hand is which

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 2, 3)

    cv2.imshow("Image", cv2.flip(img, 1))
    if cv2.waitKey(1) == 27:
        break;

