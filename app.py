import cv2
import mediapipe as mp
import time
import os
import random
import threading
import ctypes
import tkinter as tk
from PIL import Image, ImageTk
import urllib.request

# --- CONFIGURATION ---
MODEL_PATH = "efficientdet_lite0.tflite"
# Check both potential paths for the alarm
ALARM_PATHS = ["./assets/alarm.mp3", "./assets/memes/alarm.mp3"]
MEMES_DIR = "./assets/memes/"
CONFIDENCE_THRESHOLD = 2.0  # 2 seconds requirement

class ScrollAlarm:
    def __init__(self):
        self.running = True
        self.detection_start_time = None
        self.is_alarm_on = False
        self.current_frame = None
        
        self._ensure_model_exists()
        self._init_detector()

    def _ensure_model_exists(self):
        """Downloads the MediaPipe object detection model if missing."""
        if not os.path.exists(MODEL_PATH):
            print(f"[*] Model '{MODEL_PATH}' not found. Downloading...")
            url = "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float32/1/efficientdet_lite0.tflite"
            try:
                urllib.request.urlretrieve(url, MODEL_PATH)
                print("[+] Model downloaded successfully.")
            except Exception as e:
                print(f"[-] Failed to download model: {e}")


    def _init_detector(self):
        """Initializes the MediaPipe Object Detector Task."""
        from mediapipe.tasks.python import vision
        base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
        self.detector = vision.ObjectDetector.create_from_options(options)

    def trigger_alarm(self):
        """Triggered when high confidence phone usage is detected."""
        if self.is_alarm_on:
            return
        
        self.is_alarm_on = True
        print("\n[!!!] PHONE DETECTED! STOP SCROLLING!")
        
        # Start alarm sequence in a separate thread to avoid blocking detection
        threading.Thread(target=self._run_alarm_ui_logic, daemon=True).start()

    def _run_alarm_ui_logic(self):
        """Plays sound and shows the meme popup."""
        # 1. Play Sound (Native Windows MCI)
        played = False
        for path in ALARM_PATHS:
            if os.path.exists(path):
                abs_path = os.path.abspath(path)
                # MCI Command to play MP3
                ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias alarm', None, 0, 0)
                ctypes.windll.winmm.mciSendStringW('play alarm repeat', None, 0, 0)
                played = True
                break
        
        if not played:
            print("[!] Warning: Alarm sound file not found.")

        # 2. Show 'Always on Top' Meme Window
        self._show_meme_popup()

    def _show_meme_popup(self):
        """Creates a Tkinter window with a random meme."""
        root = tk.Tk()
        root.title("PUT YOUR PHONE DOWN!")
        root.attributes("-topmost", True) # Keep window on top
        
        # Try to load a random meme image
        try:
            if os.path.exists(MEMES_DIR):
                memes = [f for f in os.listdir(MEMES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if memes:
                    meme_path = os.path.join(MEMES_DIR, random.choice(memes))
                    img = Image.open(meme_path)
                    img.thumbnail((600, 600))
                    photo = ImageTk.PhotoImage(img)
                    label = tk.Label(root, image=photo)
                    label.image = photo # Keep reference
                    label.pack(padx=20, pady=20)
        except Exception as e:
            tk.Label(root, text="GET OFF YOUR PHONE!", font=("Arial", 28), fg="red").pack(padx=50, pady=50)

        def stop_alarm():
            # Stop Windows MCI sound
            ctypes.windll.winmm.mciSendStringW('stop alarm', None, 0, 0)
            ctypes.windll.winmm.mciSendStringW('close alarm', None, 0, 0)
            
            self.is_alarm_on = False
            self.detection_start_time = None
            root.destroy()

        # Resolution button
        tk.Button(root, text="OK, I'll stop scrolling", command=stop_alarm, 
                  font=("Arial", 14), bg="#ff4444", fg="white", padx=20).pack(pady=20)
        
        root.mainloop()

    def detection_worker(self):
        """Background thread logic for processing frames."""
        while self.running:
            if self.current_frame is None:
                time.sleep(0.01)
                continue
            
            # Prepare image for MediaPipe
            rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect objects
            results = self.detector.detect(mp_image)
            
            # Look for 'cell phone' label
            phone_found = False
            for detection in results.detections:
                for category in detection.categories:
                    if category.category_name == "cell phone":
                        phone_found = True
                        break
            
            # Logic for 2-second confidence timer
            if phone_found:
                if self.detection_start_time is None:
                    self.detection_start_time = time.time()
                elif time.time() - self.detection_start_time >= CONFIDENCE_THRESHOLD:
                    self.trigger_alarm()
            else:
                # Reset timer if phone is gone (and alarm isn't currently active)
                if not self.is_alarm_on:
                    self.detection_start_time = None
            
            time.sleep(0.05) # Throttle detection slightly to save CPU

    def run(self):
        """Main application loop."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[-] Error: Could not open webcam.")
            return

        # Start detection thread
        detect_thread = threading.Thread(target=self.detection_worker, daemon=True)
        detect_thread.start()

        print("[*] Scroll Alarm Active. Press 'q' to quit.")
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Update current frame for the worker thread
                self.current_frame = frame
                
                # Render the webcam feed
                cv2.imshow("Scroll Alarm - Feed", self.frame_with_overlay(frame))
                
                # Exit strategy
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
        finally:
            self.running = False
            cap.release()
            cv2.destroyAllWindows()

    def frame_with_overlay(self, frame):
        """Adds visual status to the cv2 window."""
        status = "ALARM ACTIVE" if self.is_alarm_on else "MONITORING"
        color = (0, 0, 255) if self.is_alarm_on else (0, 255, 0)
        
        cv2.putText(frame, f"Status: {status}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if self.detection_start_time and not self.is_alarm_on:
            elapsed = time.time() - self.detection_start_time
            cv2.rectangle(frame, (20, 60), (20 + int(elapsed * 100), 75), (0, 255, 255), -1)
            
        return frame

if __name__ == "__main__":
    app = ScrollAlarm()
    app.run()
