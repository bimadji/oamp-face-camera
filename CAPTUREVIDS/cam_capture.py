import cv2 as cv
import os
from datetime import datetime

# buka webcam
cap = cv.VideoCapture(2)

if not cap.isOpened():
    print("Webcam tidak bisa dibuka")
    exit()

# ukuran frame
frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

# codec
fourcc = cv.VideoWriter_fourcc(*'mp4v')

recording = False
out = None
filename = ""

print("Tekan 'r' untuk start/stop recording")
print("Tekan 'q' untuk keluar")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Gagal membaca frame")
        break

    # kalau recording aktif
    if recording:
        out.write(frame)

        # indikator REC
        cv.circle(frame, (30, 30), 10, (0, 0, 255), -1)
        cv.putText(
            frame,
            "REC",
            (50, 35),
            cv.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    cv.imshow("frame", frame)

    key = cv.waitKey(1) & 0xFF

    # start / stop recording
    if key == ord('r'):

        # START RECORDING
        if not recording:

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output_{timestamp}.mp4"

            out = cv.VideoWriter(
                filename,
                fourcc,
                20.0,
                (frame_width, frame_height)
            )

            recording = True

            print(f"\nRecording dimulai:")
            print(os.path.abspath(filename))

        # STOP RECORDING
        else:
            recording = False

            out.release()
            out = None

            print("\nRecording dihentikan")
            print("Video berhasil disimpan di:")
            print(os.path.abspath(filename))

    # keluar
    elif key == ord('q'):
        break

# cleanup
cap.release()

if out is not None:
    out.release()

cv.destroyAllWindows()