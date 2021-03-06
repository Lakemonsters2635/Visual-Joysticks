import cv2
import cv2.cv2
import mediapipe as mp
import time
import pyvjoy
from networktables import NetworkTables
from networktables import NetworkTablesInstance

# pinky disable drive
# deal with going too far off screen, especially on left edge
# Increase reliability of thumb
# Try to eliminate spurious hands by setting a higher threshold

useNetworkTables = True


hidNames = {
    pyvjoy.HID_USAGE_X: "Axis-0",
    pyvjoy.HID_USAGE_Y: "Axis-1",
    pyvjoy.HID_USAGE_Z: "Axis-2",
    pyvjoy.HID_USAGE_RX: "Axis-3",
    pyvjoy.HID_USAGE_RY: "Axis-4",
    pyvjoy.HID_USAGE_RZ: "Axis-5",
    pyvjoy.HID_USAGE_SL0: "Slider-0",
    pyvjoy.HID_USAGE_SL1: "Slider-1"
}
print(hidNames)

joystick = pyvjoy.VJoyDevice(1)

if useNetworkTables:
    ntinst = NetworkTablesInstance.getDefault()

    print("Setting up NetworkTables client for team {}".format(2635))
    ntinst.startClientTeam(2635)
    ntinst.startDSClient()

    sd = NetworkTables.getTable("SmartDashboard")
    print(sd)


def setAxis(whichAxis, value):
    if useNetworkTables:
        # print(whichAxis)
        sd.putValue("vJoy/{0}".format(hidNames[whichAxis]), value)
    else:
        joystick.set_axis(whichAxis, value)


def setButton(whichButton, value):
    if useNetworkTables:
        sd.putValue("vJoy/Button-{0}".format(whichButton), value)
    else:
        joystick.set_button(whichButton, value)


xSpacing = 0.166

driveLeftHandStartX = xSpacing
driveRightHandStartX = 3 * xSpacing
gameToolHandStartX = 5 * xSpacing
allHandsStartY = 0.5

startCircleSize = 20
circleLineThickness = 3

driveHandsMaxY = allHandsStartY - 0.333
driveHandsMinY = 2 * allHandsStartY - driveHandsMaxY

driveLeftHandMinX = driveLeftHandStartX - xSpacing
driveLeftHandMaxX = driveLeftHandStartX + xSpacing
gameToolHandMinX = gameToolHandStartX - xSpacing
gameToolHandMaxX = gameToolHandStartX + xSpacing
driveRightHandMinX = driveRightHandStartX - xSpacing
driveRightHandMaxX = driveRightHandStartX + xSpacing


def mapPixelPercentToThrottle(x, Min, Max):
    return -((2 / (Min - Max)) * (x - Min) + 1)


fingerTips = [4, 8, 12, 16, 20]
leftDriveButton = [[], [0], [1], [0, 1], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                   [], [], [], [], [], [], [], [], [], [], []]
rightDriveButton = [[], [2], [3], [2, 3], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [],
                    [], [], [], [], [], [], [], [], [], []]
gameToolButtons = [[], [4], [5], [4, 5], [6], [6, 4], [6, 4, 5], [], [], [], [], [], [], [], [], [], [], [7, 4], [7, 5],
                   [7, 4, 5], [7, 6], [7, 6, 4], [7, 6, 4, 5], [], [], [], [], [], [], [], [], [], []]


# Thumb is sensitive to hand orientation.
# Solution:
#   1. Measure distance from LM4 (tip) to LM3 (1st joint).
#   2. Require LM4 to be at least 25% of that distance to left/right of LM3


def fingersUp(myHandType, landmarks):
    if myHandType == "Right":
        if landmarks[fingerTips[0]].x < landmarks[fingerTips[0] - 1].x:
            fingers = 1
        else:
            fingers = 0

    else:
        if landmarks[fingerTips[0]].x > landmarks[fingerTips[0] - 1].x:
            fingers = 1
        else:
            fingers = 0

            # 4 Fingers
    for fingerId in range(1, 5):
        if landmarks[fingerTips[fingerId]].y < landmarks[fingerTips[fingerId] - 2].y:
            fingers += 2 ** fingerId

    return fingers


def set_buttons(buttons, Fup):
    buttonsToSet = buttons[Fup]
    buttonsToClear = [0, 1, 2, 3, 4, 5, 6, 7]

    for b in buttonsToSet:
        buttonsToClear.remove(b)

    for b in buttonsToSet:
        # print("Set: ", b)
        setButton(b + 1, True)

    for b in buttonsToClear:
        # print("Clear: ", b)
        setButton(b + 1, False)


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

    # Notes on what gestures mean: Closed fist : don't move Left hand: joystick Right hand: joystick Gestures: Each
    # finger represents a different button, raising multiple fingers can have simulataneous button pressing Each
    # gesture would be mapped to a button press Number of hands: 3 Close fist for command hand means neutral Command
    # hand could represent different buttons with binary numbers See if we can have audio feedback whenever buttons
    # are activated, either different notes for different buttons or a voice that tells which button was pressed

    # Would want filtering on gestures, to ensure that if we want multiple buttons running at same time, that it can
    # account for delays in putting up fingers

    # Visual feedback:
    # having a joystick neutral position on screen for driver to match fists to that place
    # Skeleton drawing of hands
    # When button is triggered, give indication

    # draw two lines on screen for the max and min boundaries of where the palm of the hand can move
    cv2.line(img, (0, int(driveHandsMaxY * h)), (w, int(driveHandsMaxY * h)), (0, 0, 255), 2)
    cv2.line(img, (0, int(driveHandsMinY * h)), (w, int(driveHandsMinY * h)), (0, 0, 255), 2)

    cv2.line(img, (int((1 - driveLeftHandMinX) * w), 0), (int((1 - driveLeftHandMinX) * w), h), (0, 0, 255), 4)
    cv2.line(img, (int((1 - driveLeftHandMaxX) * w), 0), (int((1 - driveLeftHandMaxX) * w), h), (0, 0, 255), 2)

    cv2.line(img, (int((1 - gameToolHandMinX) * w), 0), (int((1 - gameToolHandMinX) * w), h), (0, 0, 255), 2)
    cv2.line(img, (int((1 - gameToolHandMaxX) * w), 0), (int((1 - gameToolHandMaxX) * w), h), (0, 0, 255), 2)

    # draw three circles: 2 for starting "neutral" positions of the drivers hands and 1 for weapons commander hand
    cx, cy = int((1 - driveLeftHandStartX) * w), int(allHandsStartY * h)
    cv2.circle(img, (cx, cy), startCircleSize, (255, 0, 0), circleLineThickness)

    cx = int((1 - driveRightHandStartX) * w)
    cv2.circle(img, (cx, cy), startCircleSize, (0, 0, 255), circleLineThickness)

    cx = int((1 - gameToolHandStartX) * w)
    cv2.circle(img, (cx, cy), startCircleSize, (0, 255, 0), circleLineThickness)

    # X                                 Y
    # int(driveHandsMinY * h))          -1.0
    # int(driveHandsMaxY * h))          +1.0

    sawLeftDrive = False
    sawRightDrive = False

    if results.multi_hand_landmarks:
        # print('Handedness:', results.multi_handedness)
        # print(results.multi_handedness[0])

        # for handedness in results.multi_handedness:
        # print(handedness)

        i = 0
        for handID in range(0, len(results.multi_hand_landmarks)):
            handLms = results.multi_hand_landmarks[handID]
            # print(results.multi_handedness[handID])
            fup = fingersUp(results.multi_handedness[handID].classification[0].label, handLms.landmark)
            # print(bin(fup))
            which = ""

            for Id, lm in enumerate(handLms.landmark):
                # print(Id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(Id, cx, cy)
                if Id == 0:
                    if results.multi_handedness[handID].classification[0].label == "Right":
                        # Gametool hand or Drivehand
                        if lm.x > 0.5:
                            cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
                            tempPixelMapping = mapPixelPercentToThrottle(lm.y, driveHandsMinY, driveHandsMaxY)
                            setAxis(pyvjoy.HID_USAGE_Y, int(16384 * (1 + tempPixelMapping)))
                            tempPixelMapping = mapPixelPercentToThrottle(1 - lm.x, driveLeftHandMinX, driveLeftHandMaxX)
                            setAxis(pyvjoy.HID_USAGE_X, int(16384 * (1 + tempPixelMapping)))
                            which = "Left"
                            sawLeftDrive = True
                            # print(tempPixelMapping)
                        else:
                            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
                            tempPixelMapping = mapPixelPercentToThrottle(lm.y, driveHandsMinY, driveHandsMaxY)
                            setAxis(pyvjoy.HID_USAGE_RZ, int(16384 * (1 + tempPixelMapping)))
                            tempPixelMapping = mapPixelPercentToThrottle(1 - lm.x, gameToolHandMinX, gameToolHandMaxX)
                            setAxis(pyvjoy.HID_USAGE_Z, int(16384 * (1 + tempPixelMapping)))
                            which = "Drive"

                    if results.multi_handedness[handID].classification[0].label == "Left":
                        cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                        tempPixelMapping = mapPixelPercentToThrottle(lm.y, driveHandsMinY, driveHandsMaxY)
                        setAxis(pyvjoy.HID_USAGE_RY, int(16384 * (1 + tempPixelMapping)))
                        tempPixelMapping = mapPixelPercentToThrottle(1 - lm.x, driveRightHandMinX, driveRightHandMaxX)
                        setAxis(pyvjoy.HID_USAGE_RX, int(16384 * (1 + tempPixelMapping)))
                        which = "Right"
                        sawRightDrive = True
                        # print(tempPixelMapping)

            if which == "Right":
                set_buttons(rightDriveButton, fup)
            elif which == "Left":
                set_buttons(leftDriveButton, fup)
            elif which == "Drive":
                set_buttons(gameToolButtons, fup)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    if not sawRightDrive:
        setAxis(pyvjoy.HID_USAGE_RY, 16384)
        setAxis(pyvjoy.HID_USAGE_RX, 16384)

    if not sawLeftDrive:
        setAxis(pyvjoy.HID_USAGE_Y, 16384)
        setAxis(pyvjoy.HID_USAGE_X, 16384)

    if useNetworkTables:
        ntinst.flush()

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 2, 3)

    cv2.imshow("Image", cv2.flip(img, 1))
    if cv2.waitKey(1) == 27:
        break
