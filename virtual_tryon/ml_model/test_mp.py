import cv2
import mediapipe as mp
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

print("Imports successful")
task_path = os.path.join(os.path.dirname(__file__), 'pose_landmarker_lite.task')
with open(task_path, 'rb') as f:
    model_asset_buffer = f.read()

base_options = python.BaseOptions(model_asset_buffer=model_asset_buffer)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False)
detector = vision.PoseLandmarker.create_from_options(options)

print("Detector created")
