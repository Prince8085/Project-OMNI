# <div align="center">Project OMNI</div>

### <div align="center">Omnipotent Machine Network Intelligence</div>

<div align="center">
  Your Personal autonomous AI Agent with Full System Access.
  <br>
  <i>"Building Jarvis: A fully autonomous AI agent powered by Open Interpreter"</i>
  <br><br>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
  [![Status](https://img.shields.io/badge/status-active-success)]()
</div>

---

## 🚀 Overview

**Project OMNI** is an enterprise-grade autonomous AI agent designed to run locally on your machine. Unlike cloud-based chatbots, OMNI has "hands" and "eyes"—it can interact with your file system, execute code, control your mouse and keyboard, and see your screen.

Powered by **Gemini Pro** (and supporting GPT-4/Qwen), OMNI bridges the gap between thinking and doing.

### ✨ Key Capabilities

- **🤖 Autonomous Execution**: Writes and runs Python scripts to automate complex workflows.
- **👁️ Computer Vision**: Sees your screen and uses Face Authentication/Hand Gestures.
- **🗣️ Advanced Voice**: Real-time voice interaction with neural text-to-speech.
- **🖥️ Sci-Fi HUD**: A futuristic, movie-style interface for system monitoring and control.
- **🛡️ Secure Sandboxing**: 3-Tier Permission System (Safe/Confirm/Block) with Docker integration.
- **🧠 Local Memory (RAG)**: Ingests documents to provide context-aware answers.

---

## 🛠️ Quick Start

### Prerequisites
- Python 3.10+
- [Docker](https://www.docker.com/) (Optional, for sandboxing)
- API Key (Google Gemini, OpenAI, or OpenRouter)

### Installation

```bash
# Clone the repository
git clone https://github.com/Prince8085/Project-OMNI.git
cd Project-OMNI

# Create virtual environment
python -m venv venv
venv\Scripts\activate # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API Keys
# Rename config/.env.example to config/.env and add your keys
# GOOGLE_API_KEY=...
```

### Usage

**Run the Sci-Fi GUI (Recommended):**
```bash
python src/gui_sci_fi.py
```

**Run the Command Line Interface:**
```bash
python src/cli.py
```

---

## 🏗️ Architecture

OMNI is built on a modular architecture centered around the **OmniBrain**:

1.  **Perception**: Voice (Microphone), Vision (Camera), Input (Text).
2.  **OmniBrain**: The orchestrator that manages context, RAG memory, and safety checks.
3.  **Executors**:
    *   **Open Interpreter**: For coding and system tasks.
    *   **Computer Use**: For GUI automation (Mouse/Keyboard).
    *   **Browser**: For web navigation (Playwright).
4.  **Interface**: PyQt5 HUD or Rich CLI.

---

## 🛡️ Safety & Security

OMNI has full system access, so safety is paramount.

*   **Permission Tiers**: Critical actions (delete, format, install) require explicit user confirmation.
*   **Action Logging**: Every executed command is logged in `logs/` for audit.
*   **Sandboxing**: Code execution can be routed to a Docker container.

> ⚠️ **Disclaimer**: Always review the code OMNI proposes to run, especially when operating outside the sandbox.

---

## 🤝 Contributing

This is an open-source project. Contributions are welcome! 
1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <b>Built with ❤️ by Prince Kachhwaha</b>
</div>
