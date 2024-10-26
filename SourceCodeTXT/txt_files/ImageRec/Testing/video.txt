"""
This script is used for video inferencing using pc webcam. 
It uses the YOLOv5 model to perform real-time object detection on the video feed for simpler model testing.
"""

import cv2
import torch
import numpy as np
from model import *


# Draw bounding boxes and labels on the image
def draw_boxes(results, frame):
    for *box, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, box)
        label = f"{results.names[int(cls)]} {conf:.2f}"
        color = (0, 255, 0)  # Green color for bounding box
        text_color = (0, 0, 0)  # Black color for text

        # Draw the bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        # For the text background, find space required by the text so that we can put a background with that amount of width.
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        # Print the text
        cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)

    return frame

# Main function to perform live inferencing
def live_inferencing():
    model = load_model()
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Perform inference
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert frame to RGB
        results = model(frame_rgb, size=640)  # Perform inference with the model

        df_results = results.pandas().xyxy[0]
        df_results['bboxHt'] = df_results['ymax'] - df_results['ymin']
        df_results['bboxWt'] = df_results['xmax'] - df_results['xmin']
        df_results['bboxArea'] = df_results['bboxHt'] * df_results['bboxWt']

        # Label with largest bbox height will be last
        df_results = df_results.sort_values('bboxArea', ascending=False)

        print("Results:\n")
        print(df_results)
        print("End:\n")
        # Draw bounding boxes and labels
        frame = draw_boxes(results, frame)

        # Display the frame
        cv2.imshow('YOLOv5 Live Inference', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    live_inferencing()