"""
OMNI GUI - Graphical Interface with Voice
A beautiful GUI for Project OMNI with voice input/output.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
from datetime import datetime
from pathlib import Path
import os
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.brain import OmniBrain
from src.perception.voice import VoiceModule
from dotenv import load_dotenv

# Load environment
load_dotenv('config/.env')


class OmniGUI:
    """Graphical interface for OMNI with voice capabilities."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 OMNI - AI Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e2e')
        
        # Initialize components
        self.brain = None
        self.voice = None
        self.message_queue = queue.Queue()
        self.is_listening = False
        
        self._setup_ui()
        self._init_brain()
        
    def _setup_ui(self):
        """Setup the user interface."""
        # Header
        header = tk.Frame(self.root, bg='#2d2d44', height=80)
        header.pack(fill=tk.X, padx=0, pady=0)
        
        title = tk.Label(
            header,
            text="🤖 OMNI",
            font=('Segoe UI', 24, 'bold'),
            bg='#2d2d44',
            fg='#00ff88'
        )
        title.pack(pady=20)
        
        subtitle = tk.Label(
            header,
            text="Your AI Assistant with Full System Access",
            font=('Segoe UI', 10),
            bg='#2d2d44',
            fg='#888888'
        )
        subtitle.pack()
        
        # Main container
        main = tk.Frame(self.root, bg='#1e1e2e')
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Chat display
        chat_frame = tk.Frame(main, bg='#1e1e2e')
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            chat_frame,
            text="Conversation",
            font=('Segoe UI', 12, 'bold'),
            bg='#1e1e2e',
            fg='#ffffff'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#2d2d44',
            fg='#ffffff',
            insertbackground='#00ff88',
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input area
        input_frame = tk.Frame(main, bg='#1e1e2e')
        input_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.input_field = tk.Entry(
            input_frame,
            font=('Segoe UI', 12),
            bg='#2d2d44',
            fg='#ffffff',
            insertbackground='#00ff88',
            relief=tk.FLAT,
            bd=10
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_field.bind('<Return>', lambda e: self._send_message())
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg='#1e1e2e')
        button_frame.pack(side=tk.RIGHT)
        
        self.send_btn = tk.Button(
            button_frame,
            text="Send",
            command=self._send_message,
            bg='#00ff88',
            fg='#1e1e2e',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.send_btn.pack(side=tk.LEFT, padx=5)
        
        self.voice_btn = tk.Button(
            button_frame,
            text="🎤 Voice",
            command=self._toggle_voice,
            bg='#5555ff',
            fg='#ffffff',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.voice_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=('Segoe UI', 9),
            bg='#2d2d44',
            fg='#888888',
            anchor=tk.W,
            padx=20,
            pady=10
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
    def _init_brain(self):
        """Initialize OMNI brain in background."""
        def init():
            try:
                self._update_status("Initializing OMNI...")
                self.brain = OmniBrain()
                self.voice = VoiceModule()
                self._update_status("✅ Ready - Powered by Gemini Pro")
                self._add_message("OMNI", "Hello! I'm OMNI, your AI assistant. How can I help you today?")
                self.voice.speak("Hello! I'm OMNI, your AI assistant.")
            except Exception as e:
                self._update_status(f"❌ Error: {e}")
                self._add_message("System", f"Error initializing: {e}")
        
        threading.Thread(target=init, daemon=True).start()
    
    def _add_message(self, sender: str, message: str):
        """Add message to chat display."""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "You":
            prefix = f"[{timestamp}] 👤 You:\n"
            self.chat_display.insert(tk.END, prefix, 'user')
        elif sender == "OMNI":
            prefix = f"[{timestamp}] 🤖 OMNI:\n"
            self.chat_display.insert(tk.END, prefix, 'omni')
        else:
            prefix = f"[{timestamp}] ℹ️ {sender}:\n"
            self.chat_display.insert(tk.END, prefix, 'system')
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Configure tags
        self.chat_display.tag_config('user', foreground='#00ff88', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_config('omni', foreground='#5555ff', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_config('system', foreground='#ffaa00', font=('Segoe UI', 10, 'bold'))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _update_status(self, status: str):
        """Update status bar."""
        self.status_label.config(text=status)
    
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
                self._update_status("🤔 Thinking...")
                result = self.brain.process_command(message)
                
                response = result.get('output', 'No response')
                self._add_message("OMNI", response)
                
                # Speak response
                if self.voice:
                    self.voice.speak(response[:200])  # Speak first 200 chars
                
                self._update_status("✅ Ready")
            except Exception as e:
                self._add_message("System", f"Error: {e}")
                self._update_status("❌ Error")
        
        threading.Thread(target=process, daemon=True).start()
    
    def _toggle_voice(self):
        """Toggle voice input."""
        if not self.is_listening:
            self.is_listening = True
            self.voice_btn.config(bg='#ff5555', text='🔴 Listening...')
            self._update_status("🎤 Listening for voice input...")
            self._add_message("System", "Voice input not yet implemented. Please type your message.")
            
            # Reset after 2 seconds
            self.root.after(2000, lambda: self._stop_listening())
        else:
            self._stop_listening()
    
    def _stop_listening(self):
        """Stop voice input."""
        self.is_listening = False
        self.voice_btn.config(bg='#5555ff', text='🎤 Voice')
        self._update_status("✅ Ready")
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = OmniGUI()
    app.run()


if __name__ == '__main__':
    main()
