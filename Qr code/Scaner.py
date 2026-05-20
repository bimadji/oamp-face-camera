import cv2

cap = cv2.VideoCapture(0)

detector = cv2.QRCodeDetector()

while True:
    _, frame = cap.read()

    data, bbox, _ = detector.detectAndDecode(frame)

    if data:
        print("QR Code:", data)

    cv2.imshow("QR Scanner", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()