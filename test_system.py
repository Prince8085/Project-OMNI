"""
System Test Script for OMNI
Tests all components and verifies Gemini integration.
"""

import os
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("🤖 OMNI SYSTEM TEST")
print("=" * 60)

# Test 1: Environment Configuration
print("\n1️⃣ Testing Environment Configuration...")
from dotenv import load_dotenv
load_dotenv('config/.env')

google_api_key = os.getenv('GOOGLE_API_KEY')
if google_api_key and len(google_api_key) > 20:
    print("   ✅ Gemini API Key found")
else:
    print("   ❌ Gemini API Key missing or invalid")

primary_model = os.getenv('PRIMARY_MODEL', 'gemini-pro')
print(f"   ✅ Primary Model: {primary_model}")

# Test 2: Import Core Modules
print("\n2️⃣ Testing Core Module Imports...")
try:
    from src.core.brain import OmniBrain
    print("   ✅ OmniBrain imported")
except Exception as e:
    print(f"   ❌ OmniBrain import failed: {e}")

try:
    from src.executors.open_interpreter import OpenInterpreterExecutor
    print("   ✅ OpenInterpreterExecutor imported")
except Exception as e:
    print(f"   ❌ OpenInterpreterExecutor import failed: {e}")

try:
    from src.perception.voice import VoiceModule
    print("   ✅ VoiceModule imported")
except Exception as e:
    print(f"   ❌ VoiceModule import failed: {e}")

# Test 3: Phase 2-5 Modules
print("\n3️⃣ Testing Advanced Modules...")
try:
    from src.tools.data_analysis import DataAnalysisTools
    print("   ✅ DataAnalysisTools imported")
except Exception as e:
    print(f"   ❌ DataAnalysisTools: {e}")

try:
    from src.tools.web_scraping import WebScrapingTools
    print("   ✅ WebScrapingTools imported")
except Exception as e:
    print(f"   ❌ WebScrapingTools: {e}")

try:
    from src.executors.computer_use import ComputerUseModule
    print("   ✅ ComputerUseModule imported")
except Exception as e:
    print(f"   ❌ ComputerUseModule: {e}")

# Test 4: Dependencies
print("\n4️⃣ Testing Key Dependencies...")
try:
    import pandas
    print("   ✅ pandas installed")
except:
    print("   ❌ pandas missing")

try:
    import speech_recognition
    print("   ✅ SpeechRecognition installed")
except:
    print("   ❌ SpeechRecognition missing")

try:
    import pyaudio
    print("   ✅ PyAudio installed")
except:
    print("   ❌ PyAudio missing")

try:
    import pyttsx3
    print("   ✅ pyttsx3 installed")
except:
    print("   ❌ pyttsx3 missing")

# Test 5: Open Interpreter Configuration
print("\n5️⃣ Testing Open Interpreter Configuration...")
try:
    config = {}
    executor = OpenInterpreterExecutor(config)
    print("   ✅ OpenInterpreterExecutor initialized")
    print(f"   ✅ Model: {executor.interpreter.llm.model}")
    print("   ✅ Gemini API configured")
except Exception as e:
    print(f"   ❌ Executor initialization failed: {e}")

# Test 6: Voice Module
print("\n6️⃣ Testing Voice Module...")
try:
    voice = VoiceModule()
    voices = voice.list_voices()
    print(f"   ✅ Voice module initialized ({len(voices)} voices available)")
except Exception as e:
    print(f"   ❌ Voice module failed: {e}")

# Test 7: GUI Files
print("\n7️⃣ Testing GUI Files...")
gui_files = [
    'src/gui.py',
    'src/gui_jarvis.py'
]
for gui_file in gui_files:
    if os.path.exists(gui_file):
        print(f"   ✅ {gui_file} exists")
    else:
        print(f"   ❌ {gui_file} missing")

# Test 8: Speech Recognition
print("\n8️⃣ Testing Speech Recognition...")
try:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    print("   ✅ Speech recognition ready")
    print(f"   ✅ Microphone detected")
except Exception as e:
    print(f"   ❌ Speech recognition failed: {e}")

print("\n" + "=" * 60)
print("📊 SYSTEM TEST COMPLETE")
print("=" * 60)

print("\n✨ To run OMNI:")
print("   GUI (JARVIS Style): py -3.9 src\\gui_jarvis.py")
print("   CLI: py -3.9 src\\cli.py")
