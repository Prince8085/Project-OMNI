"""
OMNI - Advanced JARVIS-Style GUI
Stunning holographic interface with voice input/output.
Inspired by Iron Man's JARVIS interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, Canvas
import threading
import queue
from datetime import datetime
from pathlib import Path
import os
import sys
import math
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.brain import OmniBrain
from src.perception.voice import VoiceModule
from dotenv import load_dotenv

# Load environment
load_dotenv('config/.env')


class VoiceVisualizer:
    """Animated voice visualization orb."""
    
    def __init__(self, canvas, x, y, radius=80):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.is_active = False
        self.animation_phase = 0
        
        # Create orb elements
        self.create_orb()
    
    def create_orb(self):
        """Create the central orb with rings."""
        # Outer glow
        self.outer_glow = self.canvas.create_oval(
            self.x - self.radius - 20, self.y - self.radius - 20,
            self.x + self.radius + 20, self.y + self.radius + 20,
            fill='', outline='#00ffff', width=2, state='hidden'
        )
        
        # Rotating rings
        self.rings = []
        for i in range(3):
            r = self.radius - (i * 15)
            ring = self.canvas.create_oval(
                self.x - r, self.y - r,
                self.x + r, self.y + r,
                fill='', outline=f'#00{255-i*50:02x}ff', width=2
            )
            self.rings.append(ring)
        
        # Central core
        self.core = self.canvas.create_oval(
            self.x - 30, self.y - 30,
            self.x + 30, self.y + 30,
            fill='#001a33', outline='#00ffff', width=3
        )
        
        # Pulse effect
        self.pulse = self.canvas.create_oval(
            self.x - 25, self.y - 25,
            self.x + 25, self.y + 25,
            fill='#00ffff', outline='', state='hidden'
        )
    
    def activate(self):
        """Activate the orb (listening/speaking)."""
        self.is_active = True
        self.canvas.itemconfig(self.outer_glow, state='normal')
        self.canvas.itemconfig(self.pulse, state='normal')
        self.animate()
    
    def deactivate(self):
        """Deactivate the orb."""
        self.is_active = False
        self.canvas.itemconfig(self.outer_glow, state='hidden')
        self.canvas.itemconfig(self.pulse, state='hidden')
    
    def animate(self):
        """Animate the orb."""
        if not self.is_active:
            return
        
        self.animation_phase += 0.1
        
        # Pulse effect
        pulse_size = 25 + math.sin(self.animation_phase * 2) * 5
        self.canvas.coords(
            self.pulse,
            self.x - pulse_size, self.y - pulse_size,
            self.x + pulse_size, self.y + pulse_size
        )
        
        # Rotate rings
        for i, ring in enumerate(self.rings):
            angle = self.animation_phase * (1 + i * 0.5)
            # Simple rotation effect by changing opacity
            opacity = int(128 + 127 * math.sin(angle))
            color = f'#00{opacity:02x}ff'
            self.canvas.itemconfig(ring, outline=color)
        
        # Continue animation
        self.canvas.after(50, self.animate)


class JarvisGUI:
    """Advanced JARVIS-style GUI for OMNI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OMNI - JARVIS Interface")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0f')
        
        # Initialize components
        self.brain = None
        self.voice = None
        self.is_listening = False
        self.recognizer = None
        
        self._setup_ui()
        self._init_brain()
        self._init_speech_recognition()
        
    def _setup_ui(self):
        """Setup the JARVIS-style interface."""
        # Top bar with title
        top_bar = tk.Frame(self.root, bg='#0f1419', height=60)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        title_label = tk.Label(
            top_bar,
            text="⬡ OMNI",
            font=('Orbitron', 28, 'bold'),
            bg='#0f1419',
            fg='#00ffff'
        )
        title_label.pack(side=tk.LEFT, padx=30, pady=10)
        
        status_label = tk.Label(
            top_bar,
            text="POWERED BY GEMINI PRO",
            font=('Consolas', 10),
            bg='#0f1419',
            fg='#00ff88'
        )
        status_label.pack(side=tk.RIGHT, padx=30)
        
        # Main container
        main = tk.Frame(self.root, bg='#0a0a0f')
        main.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Left panel - Voice visualizer
        left_panel = tk.Frame(main, bg='#0a0a0f', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)
        left_panel.pack_propagate(False)
        
        # Canvas for orb
        self.orb_canvas = Canvas(
            left_panel,
            bg='#0a0a0f',
            highlightthickness=0,
            width=350,
            height=350
        )
        self.orb_canvas.pack(pady=50)
        
        # Create voice visualizer
        self.visualizer = VoiceVisualizer(self.orb_canvas, 175, 175)
        
        # Voice controls
        voice_frame = tk.Frame(left_panel, bg='#0a0a0f')
        voice_frame.pack(pady=20)
        
        self.voice_btn = tk.Button(
            voice_frame,
            text="🎤 VOICE INPUT",
            command=self._toggle_voice,
            bg='#001a33',
            fg='#00ffff',
            font=('Consolas', 14, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=15,
            cursor='hand2',
            activebackground='#003366',
            activeforeground='#00ffff',
            bd=2,
            highlightthickness=2,
            highlightbackground='#00ffff',
            highlightcolor='#00ffff'
        )
        self.voice_btn.pack()
        
        self.voice_status = tk.Label(
            left_panel,
            text="Ready",
            font=('Consolas', 11),
            bg='#0a0a0f',
            fg='#888888'
        )
        self.voice_status.pack(pady=10)
        
        # Right panel - Chat interface
        right_panel = tk.Frame(main, bg='#0a0a0f')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Chat display
        chat_label = tk.Label(
            right_panel,
            text="◢ COMMUNICATION LOG",
            font=('Consolas', 12, 'bold'),
            bg='#0a0a0f',
            fg='#00ffff',
            anchor=tk.W
        )
        chat_label.pack(fill=tk.X, pady=(0, 10))
        
        # Chat frame with border
        chat_border = tk.Frame(right_panel, bg='#00ffff', bd=2)
        chat_border.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_border,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg='#0f1419',
            fg='#00ffff',
            insertbackground='#00ffff',
            relief=tk.FLAT,
            padx=20,
            pady=20,
            selectbackground='#003366',
            selectforeground='#00ffff'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input area
        input_frame = tk.Frame(right_panel, bg='#0a0a0f')
        input_frame.pack(fill=tk.X, pady=(15, 0))
        
        input_border = tk.Frame(input_frame, bg='#00ffff', bd=2)
        input_border.pack(fill=tk.X)
        
        self.input_field = tk.Entry(
            input_border,
            font=('Consolas', 13),
            bg='#0f1419',
            fg='#00ffff',
            insertbackground='#00ffff',
            relief=tk.FLAT,
            bd=10,
            selectbackground='#003366',
            selectforeground='#00ffff'
        )
        self.input_field.pack(fill=tk.X)
        self.input_field.bind('<Return>', lambda e: self._send_message())
        
        # Send button
        self.send_btn = tk.Button(
            input_frame,
            text="▶ SEND",
            command=self._send_message,
            bg='#001a33',
            fg='#00ffff',
            font=('Consolas', 11, 'bold'),
            relief=tk.FLAT,
            padx=25,
            pady=12,
            cursor='hand2',
            activebackground='#003366',
            activeforeground='#00ffff',
            bd=2,
            highlightthickness=2,
            highlightbackground='#00ffff'
        )
        self.send_btn.pack(pady=(10, 0))
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="◢ SYSTEM READY",
            font=('Consolas', 10),
            bg='#0f1419',
            fg='#00ff88',
            anchor=tk.W,
            padx=30,
            pady=12
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def _init_brain(self):
        """Initialize OMNI brain."""
        def init():
            try:
                self._update_status("◢ INITIALIZING OMNI CORE...")
                self.brain = OmniBrain()
                self.voice = VoiceModule()
                self._update_status("◢ SYSTEM ONLINE - GEMINI PRO ACTIVE")
                self._add_message("OMNI", "Good day. OMNI systems online. How may I assist you?")
                self.voice.speak("Good day. OMNI systems online.")
            except Exception as e:
                self._update_status(f"◢ ERROR: {e}")
                self._add_message("SYSTEM", f"Initialization error: {e}")
        
        threading.Thread(target=init, daemon=True).start()
    
    def _init_speech_recognition(self):
        """Initialize speech recognition."""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"Speech recognition init error: {e}")
    
    def _add_message(self, sender: str, message: str):
        """Add message to chat."""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "You":
            prefix = f"[{timestamp}] ▸ USER:\n"
            self.chat_display.insert(tk.END, prefix, 'user')
        elif sender == "OMNI":
            prefix = f"[{timestamp}] ◢ OMNI:\n"
            self.chat_display.insert(tk.END, prefix, 'omni')
        else:
            prefix = f"[{timestamp}] ◆ {sender}:\n"
            self.chat_display.insert(tk.END, prefix, 'system')
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Configure tags
        self.chat_display.tag_config('user', foreground='#00ff88', font=('Consolas', 11, 'bold'))
        self.chat_display.tag_config('omni', foreground='#00ffff', font=('Consolas', 11, 'bold'))
        self.chat_display.tag_config('system', foreground='#ffaa00', font=('Consolas', 11, 'bold'))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _update_status(self, status: str):
        """Update status bar."""
        self.status_bar.config(text=status)
    
    def _send_message(self):
        """Send message to OMNI."""
        message = self.input_field.get().strip()
        if not message:
            return
        
        self.input_field.delete(0, tk.END)
        self._add_message("You", message)
        
        # Process in background
        def process():
            try:
                self._update_status("◢ PROCESSING REQUEST...")
                self.visualizer.activate()
                
                result = self.brain.process_command(message)
                response = result.get('output', 'No response')
                
                self._add_message("OMNI", response)
                
                # Speak response
                if self.voice:
                    # Speak first 200 chars
                    speech_text = response[:200] if len(response) > 200 else response
                    self.voice.speak(speech_text)
                
                self.visualizer.deactivate()
                self._update_status("◢ SYSTEM READY")
            except Exception as e:
                self._add_message("SYSTEM", f"Error: {e}")
                self.visualizer.deactivate()
                self._update_status("◢ ERROR OCCURRED")
        
        threading.Thread(target=process, daemon=True).start()
    
    def _toggle_voice(self):
        """Toggle voice input."""
        if not self.recognizer:
            self._add_message("SYSTEM", "Speech recognition not available")
            return
        
        if not self.is_listening:
            self.is_listening = True
            self.voice_btn.config(bg='#ff3333', text='🔴 LISTENING...')
            self.voice_status.config(text="Listening...", fg='#ff3333')
            self.visualizer.activate()
            
            # Start listening in background
            threading.Thread(target=self._listen_for_speech, daemon=True).start()
    
    def _listen_for_speech(self):
        """Listen for speech input."""
        try:
            import speech_recognition as sr
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            
            # Add to chat and process
            self.root.after(0, lambda: self._process_voice_input(text))
            
        except sr.WaitTimeoutError:
            self.root.after(0, lambda: self._stop_listening("Timeout"))
        except sr.UnknownValueError:
            self.root.after(0, lambda: self._stop_listening("Could not understand"))
        except Exception as e:
            self.root.after(0, lambda: self._stop_listening(f"Error: {e}"))
    
    def _process_voice_input(self, text: str):
        """Process recognized speech."""
        self._stop_listening("Processing...")
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, text)
        self._send_message()
    
    def _stop_listening(self, message: str = "Ready"):
        """Stop voice input."""
        self.is_listening = False
        self.voice_btn.config(bg='#001a33', text='🎤 VOICE INPUT')
        self.voice_status.config(text=message, fg='#888888')
        self.visualizer.deactivate()
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = JarvisGUI()
    app.run()


if __name__ == '__main__':
    main()
