import face_recognition
import numpy as np

try:
    raghav_image = face_recognition.load_image_file("raghav.jpg")
    print(f"Shape: {raghav_image.shape}")
    print(f"Dtype: {raghav_image.dtype}")
except Exception as e:
    print(f"Error loading raghav.jpg: {e}")

try:
    jensen_image = face_recognition.load_image_file("jensen.jpg")
    print(f"Shape: {jensen_image.shape}")
    print(f"Dtype: {jensen_image.dtype}")
except Exception as e:
    print(f"Error loading jensen.jpg: {e}")
