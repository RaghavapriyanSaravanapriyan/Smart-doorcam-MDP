import face_recognition
import numpy as np
import cv2

def debug_image(name, path):
    print(f"--- Debugging {name} ({path}) ---")
    try:
        img = face_recognition.load_image_file(path)
        print(f"  Type: {type(img)}")
        print(f"  Shape: {img.shape}")
        print(f"  Dtype: {img.dtype}")
        print(f"  Min: {np.min(img)}, Max: {np.max(img)}")
        print(f"  Flags: \n{img.flags}")
        
        # Try to call face_locations
        try:
            locs = face_recognition.face_locations(img)
            print(f"  Face locations found: {len(locs)}")
        except Exception as e:
            print(f"  face_locations failed: {e}")
            
    except Exception as e:
        print(f"  Load failed: {e}")

debug_image("Raghav", "raghav.jpg")
debug_image("Jensen", "jensen.jpg")
