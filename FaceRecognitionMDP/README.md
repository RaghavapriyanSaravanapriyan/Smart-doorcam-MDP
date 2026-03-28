# 🛡️ Secure Doorcam Live Protocol

A professional-grade, real-time facial recognition security system featuring a polished web dashboard, automated door simulation, and authorized entry logging.

## 🚀 Quick Start Instructions

### 1. Install Dependencies
Ensure you have Python 3.10+ installed. Open your terminal in this project directory and run:

```bash
pip install fastapi uvicorn face_recognition opencv-python numpy jinja2
```

> [!IMPORTANT]
> This system requires a working webcam. If you have multiple cameras, the system defaults to Camera Index 1 (and falls back to 0).

### 2. Configure Your Team
Open the `team.txt` file to manage who is allowed access. The format is `Name,ImageFile.jpg`:

```text
Raghav,raghav.jpg
Jensen,jensen.jpg
```

- Ensure the `.jpg` files exist in the root folder.
- The system will automatically learn these faces on startup.

### 3. Start the Live Server
Run the main application:

```bash
python main.py
```

Look for the link in your terminal: `INFO: Uvicorn running on http://0.0.0.0:8000`.

### 4. Access the Dashboard
Open your web browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🔒 Security Logic & Features

- **Dynamic Door Simulation**: 
  - **RED / LOCKED**: If an unknown person or no one is in frame, the "Restricted Area" doors remain shut.
  - **GREEN / OPENED**: As soon as a recognized team member steps in, the doors slide open and access is granted.
- **Visual Tracking**: 
  - **Green Box**: Known team member (Safe).
  - **Red Box**: Unknown individual (Unauthorized).
- **Last Visited Log**: A real-time scrolling history of who entered and at what exact time.
- **MJPEG Live Feed**: High-performance, low-latency video streaming directly in the browser.

## 🛠️ Performance Optimization
- **1/4 Processing**: To ensure smooth 30+ FPS, the facial recognition engine processes frames at 25% resolution before scaling back up for display.
- **Dual-Frame Processing**: Face detection runs on every other frame to save CPU cycles while maintaining a smooth visual experience.

---

> [!TIP]
> **Pro Tip:** To add a new team member while the server is running, simply add their name and image path to `team.txt` and restart the `main.py` script. The "authorized" list in the dashboard will update automatically!

LETS GO