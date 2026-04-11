# 🛡️ Secure Doorcam Live Protocol

A professional-grade, real-time facial recognition security system. Built with a high-performance **FastAPI** backend and a stylized **Cyberpunk dashboard**, this system implements strict security logic to manage restricted area access.


## 🛠️ System Architecture

The application utilizes a **Producer-Consumer multi-threaded architecture** to ensure smooth video playback while performing heavy CPU-intensive facial recognition.


### Key Components:
- **Capture Thread**: High-speed frame acquisition (aims for 60 FPS).
- **Processing Thread**: Decoupled recognition logic using `face_recognition` (Dlib-based).
- **Grace Period Logic**: Implements a 1-second "unlocked" buffer to prevent jitter.
- **Strict Security**: Access is only granted if a **Known** member is present **AND** no **Unknown** individuals are in the frame.

---

## 🚀 Installation & Setup

### 1. Prerequisites (Crucial for Windows)
The core library `face_recognition` depends on `dlib`, which requires C++ compilation.
1. Install **Visual Studio Build Tools**.
2. Select "Desktop development with C++".
3. Install **CMake** (`pip install cmake`).

### 2. Environment Setup
```bash
# Clone or enter the directory
cd FaceRecognitionMDP

# Install core dependencies
pip install -r requirements.txt
```

### 3. Configure Authorized Personnel
Edit `team.txt` to define your security perimeter.
Format: `Name,ImageFile.jpg`
```text
Raghav,raghav.jpg
Nishanth,nishanth.jpg
```
*Ensure the corresponding `.jpg` files are in the root directory.*

### 4. Deploy Server
```bash
python main.py
```
Dashboard available at: 👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🔒 Security Features

| Feature | Description |
| :--- | :--- |
| **Zero-Trust Detection** | If an unknown face enters the frame alongside a team member, the door remains **LOCKED**. |
| **Dynamic Simulation** | Physical door state is visually simulated with animated sliding panels in the UI. |
| **Real-time Logging** | Captures arrival times and identity for all recognized personnel. |
| **Performance Scaling** | Frames are processed at 0.25x scale for low-latency recognition on standard hardware. |

---

## 📁 Project Structure

```text
FaceRecognitionMDP/
├── main.py              # Core FastAPI application & Threading logic
├── team.txt             # Authorization database
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # Cyberpunk UI & Door Simulation
├── [Name].jpg           # Authorized face source images
└── README.md            # You are here
```

---

## ❓ Troubleshooting

- **Camera Not Found**: The system checks Index 1 first (common for external webcams) and falls back to Index 0. Modify `cv2.VideoCapture(index)` in `main.py` if needed.
- **dlib Compilation Error**: Ensure `CMake` is installed and the C++ Compiler is in your PATH. 
- **Low FPS**: Ensure you are not running other CPU-heavy background tasks; facial recognition is computationally expensive.

---

> [!TIP]
> **Pro Tip:** For maximum security, use high-resolution source images with clear lighting for your team members. The system uses a default tolerance of `0.6` for recognition balance. **