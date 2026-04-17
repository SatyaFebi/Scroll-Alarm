# 📱 Scroll Alarm - Computer Vision Edition

A productivity tool designed to stop your doom-scrolling habit. Using real-time Computer Vision, this app detects if you're holding a smartphone while working and triggers an annoying alarm + meme popup until you put it down.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-00ADD8?style=for-the-badge&logo=google&logoColor=white)

## ✨ Features
- **Real-time Detection:** Uses Google's MediaPipe Object Detection (EfficientDet Lite0).
- **Confidence Timer:** Requires the phone to be detected for at least 2 consecutive seconds to trigger (avoids false alarms).
- **Annoying Alarm:** Plays a loud sound through Windows native MCI (no extra audio libs needed).
- **Meme Interruption:** Shows a random "Always on Top" meme window that stays focused until you confirm you'll stop.
- **Auto-Setup:** Automatically downloads the required TFLite model on the first run.

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Scroll_Alarm_Computer_Vision.git
   cd Scroll_Alarm_Computer_Vision
   ```

2. **Create and activate a Virtual Environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Usage

Simply run the main script:
```bash
python main.py
```

- Press **'q'** on the camera feed window to quit the application.
- When a phone is detected, the status bar in the feed will change and a timer will start.
- Once the alarm triggered, click the button in the popup to stop the sound and resume monitoring.

## 📂 Project Structure
```text
.
├── assets/
│   └── memes/         # Store your alarm sound and meme images here
│       ├── alarm.mp3
│       └── ...
├── main.py            # Core application logic
├── requirements.txt   # Python dependencies
└── efficientdet_lite0.tflite (auto-downloaded)
```

## ⚙️ Configuration
You can tweak settings in `main.py` under the `--- CONFIGURATION ---` section:
- `CONFIDENCE_THRESHOLD`: Time in seconds before the alarm triggers (default: 2.0).
- `MODEL_PATH`: Change the TFLite model used.
- `MEMES_DIR`: Path to your meme images folder.

## 📝 License
MIT License. Feel free to use and modify for your own productivity!
