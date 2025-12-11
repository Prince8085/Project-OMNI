"""
OMNI - Sci-Fi HUD Interface (PyQt5)
Advanced futuristic GUI with video core, real-time stats, and threaded AI.
"""

import sys
import os
import psutil
import threading
import json
from pathlib import Path
import cv2
import winsound
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsOpacityEffect,
                             QFrame, QSizePolicy, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QImage, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import pyqtgraph as pg

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Lazy imports for heavy modules
# from src.core.brain import OmniBrain
# from src.perception.voice_new import AdvancedVoiceModule
# from src.perception.wake_word import WakeWordListener
# from src.perception.face_auth import FaceAuth
# from src.perception.gestures import HandTracker

# --- WORKER THREADS ---

class BrainWorker(QThread):
    """Worker thread for AI processing."""
    response_ready = pyqtSignal(str, str) # display_text, speech_text
    
    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.command = None
        
    def process(self, text):
        self.command = text
        self.start()
        
    def run(self):
        if not self.command: return
        try:
            result = self.brain.process_command(self.command)
            raw_output = result.get('output', '{}')
            
            # Parse JSON
            try:
                data = json.loads(raw_output)
                display_text = data.get('display', raw_output)
                speech_text = data.get('speech', display_text)
            except json.JSONDecodeError:
                display_text = raw_output
                speech_text = raw_output
                
            self.response_ready.emit(display_text, speech_text)
        except Exception as e:
            self.response_ready.emit(f"Error: {e}", f"System error: {e}")

class StartupWorker(QThread):
    """Worker to load heavy modules in background."""
    finished = pyqtSignal(object, object, object) # brain, voice, auth
    status_update = pyqtSignal(str)

    def run(self):
        self.status_update.emit("LOADING BRAIN...")
        from src.core.brain import OmniBrain
        brain = OmniBrain()
        
        self.status_update.emit("LOADING VOICE...")
        from src.perception.voice_new import AdvancedVoiceModule
        voice = AdvancedVoiceModule()
        
        self.status_update.emit("LOADING SECURITY...")
        from src.perception.face_auth import FaceAuth
        auth = FaceAuth()
        
        self.finished.emit(brain, voice, auth)

class WakeWordWorker(QThread):
    """Worker thread for Wake Word detection."""
    wake_detected = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.listener = None
        self.is_running = True
        
    def _on_wake(self):
        self.wake_detected.emit()
        
    def run(self):
        from src.perception.wake_word import WakeWordListener
        self.listener = WakeWordListener(callback=self._on_wake)
        self.listener.start()
        
    def stop(self):
        if self.listener:
            self.listener.stop()
        self.quit()

class VideoWorker(QThread):
    """Worker thread for playing video using OpenCV."""
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {self.video_path}")
            return

        while self._run_flag:
            ret, cv_img = cap.read()
            if not ret:
                # Loop video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            # Convert to RGB
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # Emit full resolution, let GUI scale it
            self.change_pixmap_signal.emit(convert_to_qt_format)
            
            # Control framerate (approx 30 fps)
            self.msleep(33)
            
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

class ScreenRecorder(QThread):
    """Worker thread for screen recording."""
    
    def __init__(self):
        super().__init__()
        self.is_recording = True
        
    def run(self):
        try:
            import pyautogui
            import numpy as np
            import cv2
            from datetime import datetime
            
            # Create recordings dir
            if not os.path.exists('recordings'):
                os.makedirs('recordings')
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/omni_session_{timestamp}.avi"
            
            screen_size = pyautogui.size()
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            out = cv2.VideoWriter(filename, fourcc, 10.0, screen_size)
            
            print(f"DEBUG: Recording started: {filename}")
            
            while self.is_recording:
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
                self.msleep(100) # Cap at ~10 FPS
                
            out.release()
            print("DEBUG: Recording saved.")
            
        except Exception as e:
            print(f"Recording Error: {e}")
        
    def stop(self):
        self.is_recording = False
        self.wait()

class WebcamWorker(QThread):
    """Worker thread for Webcam capture, Face Auth, and Gestures."""
    change_pixmap_signal = pyqtSignal(QImage)
    face_detected_signal = pyqtSignal(str) # Name of user
    gesture_signal = pyqtSignal(str) # Gesture name

    def __init__(self, auth_module):
        super().__init__()
        self._run_flag = True
        self.auth = auth_module
        self.frame_count = 0
        self.tracker = None

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                # Lazy load tracker
                if self.tracker is None:
                    from src.perception.gestures import HandTracker
                    self.tracker = HandTracker(detection_con=0.7)

                # 1. Find Hands & Draw
                cv_img = self.tracker.find_hands(cv_img)
                lm_list = self.tracker.get_position(cv_img)
                
                # 2. Detect Gesture
                gesture = self.tracker.detect_gesture(lm_list)
                if gesture:
                    self.gesture_signal.emit(gesture)

                # Convert to RGB
                rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                
                # Face Auth Check (Every 30 frames ~ 1 sec)
                self.frame_count += 1
                if self.frame_count % 30 == 0:
                    user = self.auth.verify_face(rgb_image)
                    if user:
                        self.face_detected_signal.emit(user)

                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                # Mirror the image for natural feel
                p = convert_to_qt_format.mirrored(True, False)
                self.change_pixmap_signal.emit(p)
            
            self.msleep(33) # 30 FPS
            
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

# --- MAIN GUI ---

class VoiceListenerWorker(QThread):
    """Worker for active voice listening (Google Speech Recognition)."""
    started = pyqtSignal()
    finished = pyqtSignal()
    text_recognized = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def run(self):
        import speech_recognition as sr
        self.started.emit()
        
        r = sr.Recognizer()
        r.energy_threshold = 3000
        r.dynamic_energy_threshold = True
        
        try:
            with sr.Microphone() as source:
                # Listen
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                
                # Recognize
                text = r.recognize_google(audio)
                self.text_recognized.emit(text)
                
        except sr.WaitTimeoutError:
            self.error.emit("Timeout")
        except sr.UnknownValueError:
            self.error.emit("Could not understand")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class OmniSciFiGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        print("DEBUG: Initializing MainWindow...")
        
        # 1. Main Window Setup (Frameless & Fullscreen)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        
        # Background
        self.setStyleSheet("background-color: #050505;")
        
        # Initialize Core (Moved to StartupWorker)
        self.brain = None
        self.voice = None
        self.auth = None
        
        # Start Startup Worker
        self.startup_worker = StartupWorker()
        self.startup_worker.status_update.connect(self.update_loading_status)
        self.startup_worker.finished.connect(self.on_core_loaded)
        self.startup_worker.start()
        
        # Setup UI
        print("DEBUG: Setting up UI...")
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout (HBox: Left Stats | Center Core | Right Chat)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- LEFT PANEL: System Stats ---
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setStyleSheet("background-color: rgba(0, 20, 40, 150); border: 1px solid #00ffff; border-radius: 10px;")
        left_layout = QVBoxLayout(left_panel)
        
        # CPU Graph
        self.cpu_plot = pg.PlotWidget(title="CPU Usage")
        self.cpu_plot.setBackground('transparent')
        self.cpu_plot.showGrid(x=True, y=True, alpha=0.3)
        self.cpu_curve = self.cpu_plot.plot(pen=pg.mkPen('#00ffff', width=2))
        self.cpu_data = [0] * 60
        left_layout.addWidget(self.cpu_plot)
        
        # RAM Graph
        self.ram_plot = pg.PlotWidget(title="RAM Usage")
        self.ram_plot.setBackground('transparent')
        self.ram_plot.showGrid(x=True, y=True, alpha=0.3)
        self.ram_curve = self.ram_plot.plot(pen=pg.mkPen('#ff00ff', width=2))
        self.ram_data = [0] * 60
        left_layout.addWidget(self.ram_plot)
        
        main_layout.addWidget(left_panel, stretch=1)
        
        # --- CENTER PANEL: Video Core ---
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        # Webcam Label (Top of Center)
        self.webcam_label = QLabel("INITIALIZING CAMERA...")
        self.webcam_label.setAlignment(Qt.AlignCenter)
        self.webcam_label.setStyleSheet("border: 1px solid #00ffff; border-radius: 5px; background-color: #000; color: #00ffff;")
        self.webcam_label.setMinimumSize(320, 240)
        self.webcam_label.setMaximumHeight(300)
        center_layout.addWidget(self.webcam_label)
        
        # Start Webcam Thread
        self.webcam_thread = WebcamWorker(None) # Auth passed later
        self.webcam_thread.change_pixmap_signal.connect(self.update_webcam_image)
        self.webcam_thread.face_detected_signal.connect(self.unlock_system)
        self.webcam_thread.gesture_signal.connect(self.handle_gesture)
        self.webcam_thread.start()
        
        # Video Label (Display for OpenCV)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid #00ffff; border-radius: 10px; background-color: #000;")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setMinimumSize(640, 480)
        
        # Start Video Thread
        video_path = os.path.join(project_root, "gui_mp4.mp4")
        if os.path.exists(video_path):
            self.video_thread = VideoWorker(video_path)
            self.video_thread.change_pixmap_signal.connect(self.update_video_image)
            self.video_thread.start()
        else:
            self.video_label.setText(f"VIDEO NOT FOUND:\n{video_path}")
            self.video_label.setStyleSheet("color: red; border: 1px solid red;")
            
            self.video_label.setStyleSheet("color: red; border: 1px solid red;")
            
        center_layout.addWidget(self.video_label)

        # Background Audio (Music)
        if os.path.exists(video_path):
            print(f"DEBUG: Loading Audio from {video_path}")
            self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.media_player.setVolume(100) # Max volume
            
            # Loop audio & Debug
            self.media_player.mediaStatusChanged.connect(self.loop_audio)
            self.media_player.error.connect(self.handle_media_error)
            self.media_player.stateChanged.connect(lambda s: print(f"DEBUG: Media State: {s}"))
            
            self.media_player.play()
        
        # --- CONTROL PANEL (Below Video) ---
        control_panel = QFrame()
        control_panel.setStyleSheet("background-color: rgba(0, 20, 40, 150); border: 1px solid #00ffff; border-radius: 10px;")
        control_layout = QHBoxLayout(control_panel)
        
        # Input Field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type command here...")
        self.input_field.setFont(QFont("Consolas", 12))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 100);
                color: #00ffff;
                border: 1px solid #00ffff;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.input_field.returnPressed.connect(self.send_text_command)
        control_layout.addWidget(self.input_field)
        
        # Send Button
        send_btn = QPushButton("▶")
        send_btn.setFixedWidth(40)
        send_btn.setStyleSheet("background-color: #00ffff; color: #000; border-radius: 5px; font-weight: bold;")
        send_btn.clicked.connect(self.send_text_command)
        control_layout.addWidget(send_btn)
        
        # Mic Button
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedWidth(40)
        self.mic_btn.setStyleSheet("background-color: #003366; color: #fff; border: 1px solid #00ffff; border-radius: 5px;")
        self.mic_btn.clicked.connect(self.toggle_voice)
        control_layout.addWidget(self.mic_btn)
        
        center_layout.addWidget(control_panel)
        
        # Status Label
        self.status_label = QLabel("SYSTEM: ONLINE")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Consolas", 16, QFont.Bold))
        self.status_label.setStyleSheet("color: #00ffff; letter-spacing: 2px;")
        center_layout.addWidget(self.status_label)
        
        main_layout.addWidget(center_panel, stretch=2)
        
        # --- RIGHT PANEL: Chat & Input ---
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("background-color: rgba(0, 20, 40, 150); border: 1px solid #00ffff; border-radius: 10px;")
        right_layout = QVBoxLayout(self.right_panel)
        
        # Chat History
        self.chat_label = QLabel("OMNI TERMINAL\nSystem Ready.")
        self.chat_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.chat_label.setFont(QFont("Consolas", 12))
        self.chat_label.setStyleSheet("color: #00ff00; padding: 10px;")
        self.chat_label.setWordWrap(True)
        right_layout.addWidget(self.chat_label, stretch=1)
        
        # Close Button
        close_btn = QPushButton("EXIT SYSTEM")
        close_btn.setStyleSheet("color: red; border: 1px solid red; padding: 5px;")
        close_btn.clicked.connect(self.close)
        right_layout.addWidget(close_btn)
        
        main_layout.addWidget(self.right_panel, stretch=1)
        
        # Lock state
        self.is_locked = True

        # Start Threads (Moved to on_core_loaded)
        # self.brain_worker = BrainWorker(self.brain)
        # self.brain_worker.response_ready.connect(self.on_brain_response)
        
        # self.wake_worker = WakeWordWorker()
        # self.wake_worker.wake_detected.connect(self.on_wake_word)
        # self.wake_worker.start()
        
        # Welcome (Moved to on_core_loaded)
        # if not self.is_locked:
        #     QTimer.singleShot(2000, lambda: self.voice.speak("System Online. HUD Initialized."))

        # Timer for Stats
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def update_loading_status(self, status):
        """Update status label during loading."""
        self.status_label.setText(f"SYSTEM: {status}")
        self.status_label.setStyleSheet("color: #ffff00;")

    def on_core_loaded(self, brain, voice, auth):
        """Called when core modules are loaded."""
        self.brain = brain
        self.voice = voice
        self.auth = auth
        
        self.status_label.setText("SYSTEM: ONLINE")
        self.status_label.setStyleSheet("color: #00ffff;")
        
        # Start Threads
        print("DEBUG: Starting Brain/Wake Threads...")
        self.brain_worker = BrainWorker(self.brain)
        self.brain_worker.response_ready.connect(self.on_brain_response)
        
        self.wake_worker = WakeWordWorker()
        self.wake_worker.wake_detected.connect(self.on_wake_word)
        self.wake_worker.start()
        
        # Update Webcam Worker with loaded Auth
        if hasattr(self, 'webcam_thread'):
            self.webcam_thread.auth = self.auth
            
        # Start Screen Recording
        self.recorder = ScreenRecorder()
        self.recorder.start()
        self.status_label.setText("SYSTEM: ONLINE | REC")

        # Welcome
        if not self.is_locked:
            QTimer.singleShot(500, lambda: self.voice.speak("System Online. HUD Initialized."))
        
        # Check Lock
        if not self.auth.known_face_encodings:
             self.is_locked = False
             if hasattr(self, 'lock_overlay'): self.lock_overlay.hide()
        else:
             self.is_locked = True
             self.show_lock_screen()

    def update_video_image(self, qt_image):
        # Scale to label size while keeping aspect ratio
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def update_webcam_image(self, qt_image):
        # Scale to label size
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.webcam_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.webcam_label.setPixmap(scaled_pixmap)

    def send_text_command(self):
        text = self.input_field.text().strip()
        if not text: return
        self.input_field.clear()
        self.process_input(text)

    def update_stats(self):
        # CPU
        cpu = psutil.cpu_percent()
        self.cpu_data.pop(0)
        self.cpu_data.append(cpu)
        self.cpu_curve.setData(self.cpu_data)
        
        # RAM
        ram = psutil.virtual_memory().percent
        self.ram_data.pop(0)
        self.ram_data.append(ram)
        self.ram_curve.setData(self.ram_data)

    def on_wake_word(self):
        self.status_label.setText("STATUS: LISTENING...")
        self.status_label.setStyleSheet("color: #ff3333;")
        self.toggle_voice()



# ... (Inside OmniSciFiGUI class)

    def toggle_voice(self):
        # Toggle Logic
        if hasattr(self, 'is_listening') and self.is_listening:
            # STOP LISTENING (Cancel worker if possible, or just ignore)
            self.is_listening = False
            self.status_label.setText("STATUS: STOPPING...")
            return

        # START LISTENING
        self.is_listening = True
        
        # Create and start worker
        self.voice_worker = VoiceListenerWorker()
        self.voice_worker.started.connect(self.on_voice_start)
        self.voice_worker.finished.connect(self.on_voice_end)
        self.voice_worker.text_recognized.connect(self.process_input)
        self.voice_worker.error.connect(lambda e: print(f"Voice Error: {e}"))
        self.voice_worker.start()
        
    def on_voice_start(self):
        winsound.Beep(1000, 200)
        self.right_panel.setStyleSheet("background-color: rgba(50, 0, 0, 150); border: 2px solid #ff3333; border-radius: 10px;")
        self.status_label.setText("STATUS: LISTENING...")
        self.status_label.setStyleSheet("color: #ff3333;")
        self.mic_btn.setStyleSheet("background-color: #ff3333; color: #fff; border: 1px solid #fff; border-radius: 5px;")
        
    def on_voice_end(self):
        winsound.Beep(800, 200)
        self.right_panel.setStyleSheet("background-color: rgba(0, 20, 40, 150); border: 1px solid #00ffff; border-radius: 10px;")
        self.status_label.setText("STATUS: IDLE")
        self.status_label.setStyleSheet("color: #00ffff;")
        self.mic_btn.setStyleSheet("background-color: #003366; color: #fff; border: 1px solid #00ffff; border-radius: 5px;")
        self.is_listening = False

    def process_input(self, text):
        self.chat_label.setText(f"USER: {text}\n\n" + self.chat_label.text()[:500])
        self.status_label.setText("STATUS: PROCESSING...")
        self.brain_worker.process(text)

    def on_brain_response(self, display_text, speech_text):
        self.chat_label.setText(f"OMNI: {display_text}\n\n" + self.chat_label.text()[:500])
        self.status_label.setText("STATUS: IDLE")
        self.status_label.setStyleSheet("color: #00ffff;")
        self.voice.speak(speech_text)

    def show_lock_screen(self):
        """Overlay a lock screen."""
        self.lock_overlay = QLabel(self)
        self.lock_overlay.setGeometry(0, 0, self.width(), self.height())
        self.lock_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 240); color: red; font-size: 30px; font-weight: bold;")
        self.lock_overlay.setText("🔒 SYSTEM LOCKED\n\nSCANNING FACE...")
        self.lock_overlay.setAlignment(Qt.AlignCenter)
        self.lock_overlay.show()
        self.voice.speak("System Locked. Please identify yourself.")

    def unlock_system(self, user_name):
        """Unlock if face matches."""
        if hasattr(self, 'lock_overlay') and self.lock_overlay.isVisible():
            self.lock_overlay.hide()
            self.is_locked = False
            self.voice.speak(f"Welcome back, {user_name}. System Unlocked.")
            self.status_label.setText(f"USER: {user_name.upper()}")

    def handle_gesture(self, gesture):
        """Handle detected gestures."""
        if self.is_locked: return
        
        if gesture == "OPEN_PALM":
            if not getattr(self, 'is_listening', False):
                self.status_label.setText("GESTURE: WAKE")
                self.toggle_voice()
        elif gesture == "FIST":
            if getattr(self, 'is_listening', False):
                self.status_label.setText("GESTURE: STOP")
                self.toggle_voice()

    def loop_audio(self, status):
        """Restart audio when finished."""
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.play()

    def handle_media_error(self):
        """Handle media player errors."""
        print(f"ERROR: Media Player Error: {self.media_player.errorString()}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            
    def closeEvent(self, event):
        """Handle cleanup on close."""
        if hasattr(self, 'recorder'):
            self.recorder.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OmniSciFiGUI()
    window.show()
    sys.exit(app.exec_())
