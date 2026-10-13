"""
Session 1: Real-time YOLO11 Object Detection
Captures live webcam video, runs each frame through a YOLO11 neural network,
and displays bounding boxes with class labels and confidence scores.
"""


from ultralytics import YOLO
import cv2


# Load the YOLO11 nano model (smallest/fastest variant)
# Downloads the pretrained weights automatically on first run
# Pretrained on COCO dataset: 80 common object classes (person, cup, chair, etc.)
model = YOLO("yolo11n.pt")

# Open the default webcam (index 0)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
	print("ERROR: Could not open webcam")
	exit(1)

print("Press 'q' to quit")

while True:
	# Grab a single frame from the webcam
	ret, frame = cap.read()
	if not ret:
		break

	# Run YOLO11 inference on the frame
	# Returns a list of Results objects (one per image, so we use index [0])
	results = model(frame, verbose=False)

	# Draw bounding boxes, class labels, and confidence scores onto the frame
	annotated = results[0].plot()

	# Display the annotated frame in a window
	cv2.imshow("YOLO11 Live", annotated)

	# Exit loop when 'q' is pressed (waitKey(1) polls every 1ms)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# Clean up: release the webcam and close the display window
cap.release()
cv2.destroyAllWindows()