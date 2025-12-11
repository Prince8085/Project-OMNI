"""
OMNI - Premium JARVIS Interface
Modern GUI using CustomTkinter with Neural Voice and Advanced Execution.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import Canvas
import threading
import math
import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.brain import OmniBrain
from src.perception.voice_new import AdvancedVoiceModule
from src.perception.wake_word import WakeWordListener
from src.executors.open_interpreter import OpenInterpreterExecutor

# Configure Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class PremiumOrb(Canvas):
    """Advanced animated orb visualization."""
    
    def __init__(self, master, width=300, height=300, bg_color='#0a0a0f'):
        super().__init__(master, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.is_active = False
        self.phase = 0
        
        self.create_elements()
        self.animate()
        
    def create_elements(self):
        """Create initial orb elements."""
        # Outer glow ring
        self.outer_ring = self.create_oval(
            self.center_x - 100, self.center_y - 100,
            self.center_x + 100, self.center_y + 100,
            outline='#00ffff', width=2
        )
        
        # Inner rotating rings
        self.rings = []
        for i in range(3):
            r = 80 - (i * 20)
            ring = self.create_oval(
                self.center_x - r, self.center_y - r,
                self.center_x + r, self.center_y + r,
                outline=f'#00{200-i*40:02x}ff', width=2
            )
            self.rings.append(ring)
            
        # Core
        self.core = self.create_oval(
            self.center_x - 20, self.center_y - 20,
            self.center_x + 20, self.center_y + 20,
            fill='#00ffff', outline=''
        )
        
    def animate(self):
        """Animation loop."""
        self.phase += 0.05
        
        # Pulse core
        pulse = 20 + math.sin(self.phase * 2) * 5
        self.coords(
            self.core,
            self.center_x - pulse, self.center_y - pulse,
            self.center_x + pulse, self.center_y + pulse
        )
        
        # Rotate/Pulse rings
        if self.is_active:
            speed_mult = 3
            color_base = '#ff3333' # Red when active
        else:
            speed_mult = 1
            color_base = '#00ffff' # Cyan when idle
            
        for i, ring in enumerate(self.rings):
            # Breathing effect on rings
            offset = math.sin(self.phase * speed_mult + i) * 5
            r = 80 - (i * 20) + offset
            self.coords(
                ring,
                self.center_x - r, self.center_y - r,
                self.center_x + r, self.center_y + r
            )
            self.itemconfig(ring, outline=color_base)
            
        self.after(20, self.animate)
        
    def set_active(self, active: bool):
        self.is_active = active

class OmniPremiumGUI(ctk.CTk):
    """Premium Modern GUI for OMNI."""
    
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("OMNI - Advanced System")
        self.geometry("1200x800")
        self.configure(fg_color='#0a0a0f')
        
        # Initialize Core
        self.brain = OmniBrain()
        # Override executor with our custom one if needed, but brain uses it by default
        # We need to update the system prompt for Hindlish
        self.brain.executor.system_message += "\n\nIMPORTANT: Speak in a friendly 'Hindlish' style (mix of Hindi and English). Be conversational and helpful. Example: 'Haan sir, main kar deta hoon. File create ho gayi hai.'"
        
        self.voice = AdvancedVoiceModule()
        
        # Wake Word
        self.wake_word = WakeWordListener(callback=self._on_wake_word)
        threading.Thread(target=self.wake_word.start, daemon=True).start()
        
        self._setup_ui()
        
        # Welcome
        self.after(1000, self._welcome)
        
    def _setup_ui(self):
        """Setup the modern UI layout."""
        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Sidebar (Visuals) ---
        self.sidebar = ctk.CTkFrame(self, width=350, corner_radius=0, fg_color='#0f1419')
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="⬡ OMNI", 
            font=ctk.CTkFont(family="Orbitron", size=32, weight="bold"),
            text_color="#00ffff"
        )
        self.logo_label.pack(pady=(40, 20))
        
        # Orb Container
        self.orb_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.orb_frame.pack(fill="both", expand=True)
        
        self.orb = PremiumOrb(self.orb_frame, width=300, height=300, bg_color='#0f1419')
        self.orb.pack(pady=20)
        
        # Voice Button
        self.voice_btn = ctk.CTkButton(
            self.sidebar,
            text="🎤 VOICE INPUT",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=25,
            fg_color="#003366",
            hover_color="#004488",
            border_width=2,
            border_color="#00ffff",
            command=self._toggle_voice
        )
        self.voice_btn.pack(pady=40, padx=30, fill="x")
        
        # --- Right Main Area (Chat) ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Chat History
        self.chat_frame = ctk.CTkScrollableFrame(
            self.main_area,
            fg_color="#161b22",
            corner_radius=15,
            label_text="COMMUNICATION LOG",
            label_font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            label_text_color="#00ffff"
        )
        self.chat_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Input Area
        self.input_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.input_frame.pack(fill="x")
        
        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type your command here...",
            height=50,
            font=ctk.CTkFont(size=14),
            corner_radius=25,
            border_color="#00ffff",
            fg_color="#0f1419",
            text_color="#ffffff"
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self._send_message)
        
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="▶",
            width=50,
            height=50,
            corner_radius=25,
            fg_color="#00ffff",
            text_color="#000000",
            hover_color="#ccffff",
            font=ctk.CTkFont(size=20),
            command=self._send_message
        )
        self.send_btn.pack(side="right")
        
    def _welcome(self):
        """Welcome message."""
        msg = "Namaste! OMNI systems online. Main aapki kya madad kar sakta hoon?"
        self._add_message("OMNI", msg)
        self.voice.speak(msg)
        
    def _add_message(self, sender, text):
        """Add message to chat."""
        # Container
        msg_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_frame.pack(fill="x", pady=5)
        
        # Sender Label
        if sender == "You":
            color = "#00ff88"
            align = "e" # East (Right)
            bg = "#1a2f23"
        elif sender == "OMNI":
            color = "#00ffff"
            align = "w" # West (Left)
            bg = "#0f222e"
        else:
            color = "#ffaa00"
            align = "w"
            bg = "#2e220f"
            
        # Bubble
        bubble = ctk.CTkLabel(
            msg_frame,
            text=f"{sender}:\n{text}",
            font=ctk.CTkFont(family="Consolas", size=14),
            text_color="#ffffff",
            fg_color=bg,
            corner_radius=10,
            padx=15,
            pady=10,
            justify="left",
            wraplength=600
        )
        bubble.pack(anchor=align, padx=10)
        
        # Auto scroll
        # self.chat_frame._parent_canvas.yview_moveto(1.0) # Tricky in ctk
        
    def _send_message(self, event=None):
        """Handle send."""
        text = self.entry.get().strip()
        if not text: return
        
        self.entry.delete(0, 'end')
        self._add_message("You", text)
        
        threading.Thread(target=self._process_command, args=(text,), daemon=True).start()
        
    def _process_command(self, text):
        """Process command in background."""
        self.orb.set_active(True)
        try:
            # Execute
            result = self.brain.process_command(text)
            raw_output = result.get('output', '{}')
            
            # Parse JSON
            import json
            try:
                data = json.loads(raw_output)
                display_text = data.get('display', raw_output)
                speech_text = data.get('speech', display_text)
            except json.JSONDecodeError:
                # Fallback if not JSON
                display_text = raw_output
                speech_text = raw_output
            
            # Display
            self.after(0, lambda: self._add_message("OMNI", display_text))
            
            # Speak
            self.voice.speak(speech_text)
            
        except Exception as e:
            self.after(0, lambda: self._add_message("SYSTEM", f"Error: {e}"))
        finally:
            self.orb.set_active(False)
            
    def _on_wake_word(self):
        """Called when wake word is detected."""
        self.after(0, lambda: self.voice_btn.configure(fg_color="#ff3333", text="🔴 LISTENING..."))
        self.after(0, self._toggle_voice)

    def _toggle_voice(self):
        """Toggle voice input."""
        # For now, just a placeholder or simple input dialog
        # Implementing full STT loop in GUI is complex, reusing existing logic
        import speech_recognition as sr
        
        def listen():
            self.voice_btn.configure(fg_color="#ff3333", text="🔴 LISTENING...")
            self.orb.set_active(True)
            
            r = sr.Recognizer()
            with sr.Microphone() as source:
                try:
                    audio = r.listen(source, timeout=5)
                    text = r.recognize_google(audio)
                    self.after(0, lambda: self._handle_voice_text(text))
                except Exception as e:
                    print(e)
                finally:
                    self.after(0, lambda: self.voice_btn.configure(fg_color="#003366", text="🎤 VOICE INPUT"))
                    self.orb.set_active(False)
                    
        threading.Thread(target=listen, daemon=True).start()
        
    def _handle_voice_text(self, text):
        self.entry.insert(0, text)
        self._send_message()

if __name__ == "__main__":
    app = OmniPremiumGUI()
    app.mainloop()
