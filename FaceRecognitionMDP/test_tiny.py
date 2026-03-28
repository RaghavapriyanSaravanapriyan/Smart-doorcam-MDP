import face_recognition
import numpy as np

# Create a tiny 100x100 RGB image (all black)
tiny_img = np.zeros((100, 100, 3), dtype=np.uint8)

print(f"Tiny image shape: {tiny_img.shape}, dtype: {tiny_img.dtype}")
try:
    locs = face_recognition.face_locations(tiny_img)
    print(f"Success! Found: {len(locs)}")
except Exception as e:
    print(f"Failed: {e}")
