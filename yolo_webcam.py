from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
	print("ERROR: Could not open webcam")
	exit(1)

print("Press 'q' to quit")

while True:
	ret, frame = cap.read()
	if not ret:
		break

	results = model(frame, verbose=False)
	annotated = results[0].plot()

	cv2.imshow("YOLO11 Live", annotated)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()