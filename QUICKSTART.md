# Project OMNI - Quick Start Guide

## 🚀 Getting Started with OMNI

### Step 1: Install Python Dependencies

```powershell
# Navigate to project directory
cd "c:\Users\user\Downloads\jarvis omni\project-omni"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Keys

1. Copy the example environment file:
```powershell
copy config\.env.example config\.env
```

2. Open `config\.env` and add **at least one** API key:
   - **OpenAI**: Get key from https://platform.openai.com/api-keys
   - **Anthropic**: Get key from https://console.anthropic.com/
   - **Google**: Get key from https://makersuite.google.com/app/apikey

Example:
```
OPENAI_API_KEY=sk-your-actual-key-here
PRIMARY_MODEL=gpt-4o
```

### Step 3: Run OMNI

```powershell
python src\cli.py
```

## 📝 Example Usage

Once OMNI is running, try these commands:

```
>>> List all files in this directory
>>> Create a folder called TestProject
>>> Show me the contents of README.md
>>> What's my current directory?
```

## ⚙️ Configuration

Edit `config/models.yaml` to customize:
- Model selection (GPT-4, Claude, Gemini)
- Safety settings
- Auto-approval preferences
- Timeout values

## 🔒 Safety Features

- **Permission System**: Safe/Confirmation/Blocked tiers
- **Code Review**: See generated code before execution
- **Action Logging**: All actions logged to `~/.omni/logs/`
- **Dangerous Commands**: Automatically blocked (e.g., `rm -rf /`)

## 🐛 Troubleshooting

**"No API keys configured"**
- Make sure you've created `config/.env` and added valid API keys

**"Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Permission errors**
- On Windows, run as Administrator if needed
- Check file permissions in project directory

## 📚 Next Steps

- Read the full roadmap: `projectomniroadmap.md`
- Review implementation plan: See artifacts
- Customize safety settings in `config/models.yaml`
- Add more API integrations (Phase 5)

## 🎯 Currently Available (Phase 1)

✅ Open Interpreter code execution
✅ File system operations
✅ Terminal command execution
✅ Multi-LLM support (GPT-4o, Claude, Gemini)
✅ Safety & permission system
✅ Action logging

## 🔮 Coming Soon

⏳ Computer Use (GUI automation) - Phase 3
⏳ Voice interface (Whisper + TTS) - Phase 4
⏳ Browser automation - Phase 5
⏳ Multi-step workflows - Phase 5
