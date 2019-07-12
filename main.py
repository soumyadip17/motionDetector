import cv2
import numpy as np

cap = cv2.VideoCapture('y2mate.com - theft_real_cctv_footage_VixYrbJlFJs_360p.mp4')

ret, frame1 = cap.read()
ret, frame2 = cap.read()

while ret:

    d = cv2.absdiff(frame1, frame2)

    grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(grey, (5, 5), 0)

    ret, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

    dilated = cv2.dilate(th, np.ones((3, 3), np.uint8), iterations=10)

    eroded = cv2.erode(dilated, np.ones((3, 3), np.uint8), iterations=10)

    count = np.count_nonzero(th)

    print(count)
    if count>4000:
        print(' Movement Detected')
    else:
        print('No Movement')

    (c, _)= cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(frame1, c, -1, (0, 0, 255), 2)

    cv2.imshow("Original", frame2)
    cv2.imshow("Output", eroded)
    cv2.imshow("Countour", frame1)

    frame1 = frame2
    ret, frame2 = cap.read()

    if cv2.waitKey(30) == 27:
        break


cap.release()
cv2.destroyAllWindows()


