import cv2
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)

detector = HandDetector(detectionCon=0.8, maxHands=2)

fingerTips = (4, 8, 12, 16, 20)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # hands, img = detector.findHands(img, flipType=False)
    hands = detector.findHands(img, flipType=False, draw=False)

    for hand in hands:
        # print(hand)
        lmList = hand["lmList"]         # List of 21 landmarks
        bbox = hand["bbox"]             # bounding box (x, y, w, h)
        center = hand["center"]         # center of hand (cx, cy)
        handType = hand["type"]             # 'Left' or 'Right'
        # print(center)
        color = (0, 0, 255)
        if handType == 'Left':
            color = (0, 255, 0)
        cv2.circle(img, center, 15, color, cv2.FILLED)

        fingersUp = detector.fingersUp(hand)
        for i in range(0, 5):
            if fingersUp[i] != 0:
                cv2.circle(img, lmList[fingerTips[i]], 7, (0, 255, 255), cv2.FILLED)

    cv2.imshow("Image", img)

    key = cv2.waitKey(1)
    if key == 27 or key == 113:
        break

