import face_recognition
import numpy as np
import cv2
from PIL import Image

def debug_image(name, path):
    print(f"--- Debugging {name} ({path}) ---")
    
    # Method 1: face_recognition
    print("Method 1: face_recognition.load_image_file")
    try:
        img = face_recognition.load_image_file(path)
        print(f"  Shape: {img.shape}, Dtype: {img.dtype}")
        try:
            locs = face_recognition.face_locations(img)
            print(f"  Success! Found: {len(locs)}")
        except Exception as e:
            print(f"  Failed: {e}")
    except Exception as e:
        print(f"  Load failed: {e}")

    # Method 2: PIL explicit conversion
    print("Method 2: PIL.Image.open(...).convert('RGB')")
    try:
        pil_img = Image.open(path).convert('RGB')
        img = np.array(pil_img)
        print(f"  Shape: {img.shape}, Dtype: {img.dtype}")
        try:
            locs = face_recognition.face_locations(img)
            print(f"  Success! Found: {len(locs)}")
        except Exception as e:
            print(f"  Failed: {e}")
    except Exception as e:
        print(f"  Load failed: {e}")

    # Method 3: cv2 explicit conversion
    print("Method 3: cv2.imread and cv2.cvtColor")
    try:
        img_bgr = cv2.imread(path)
        if img_bgr is None:
            print("  cv2.imread returned None")
        else:
            img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            print(f"  Shape: {img.shape}, Dtype: {img.dtype}")
            try:
                locs = face_recognition.face_locations(img)
                print(f"  Success! Found: {len(locs)}")
            except Exception as e:
                print(f"  Failed: {e}")
    except Exception as e:
        print(f"  CV2 failed: {e}")

debug_image("Raghav", "raghav.jpg")
