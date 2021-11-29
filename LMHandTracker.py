import cv2
import cv2.cv2
import mediapipe as mp
import time

class HandDetector():
    def __init__(self, static_image_mode=False, max_num_hands=2, model_complexity=0.5, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=static_image_mode,
                                        max_num_hands=2,
                                        model_complexity=model_complexity,
                                        min_detection_confidence=min_detection_confidence,
                                        min_tracking_confidence=min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

        self.results = {}
        self.w = 0
        self.h = 0
        self.c = 0

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        self.h, self.w, self.c = img.shape

        # print(results.multi_hand_landmarks)

        if draw and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            theHand = self.results.multi_hand_landmarks[handNo]

            for ID, lm in enumerate(theHand.landmark):
                cx, cy = int(lm.x * self.w), int(lm.y * self.h)
                lmList.append([ID, cx, cy])

            if draw:
                self.mpDraw.draw_landmarks(img, theHand, self.mpHands.HAND_CONNECTIONS)

        return lmList

def main():
    pTime = 0
    cTime = 0

    cap = cv2.cv2.VideoCapture(0)

    detector = HandDetector()

    while True:
        success, img = cap.read()

        img = detector.findHands(img, draw=True)
        # lmList = detector.findPosition(img, 0, draw=True)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 2, 3)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) == 27:
            return


if __name__ == "__main__":
    main()
