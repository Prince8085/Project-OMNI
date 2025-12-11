"""
Open Interpreter executor for Project OMNI.
Uses direct REST API and custom code execution loop.
"""

import logging
import os
import json
import requests
import subprocess
import sys
import io
import traceback
from typing import Dict, Any, Generator, List, Tuple
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class OpenInterpreterExecutor:
    """Executor using Open Interpreter with direct REST API and custom execution."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration."""
        self.config = config
        load_dotenv('config/.env')
        
        self.history = []
        self.locals = {}
        
        # Determine provider and model from config
        llm_config = config.get('llms', {})
        primary_model_key = llm_config.get('primary', 'gemini-3-pro-preview')
        model_config = llm_config.get(primary_model_key, {})
        
        self.provider = model_config.get('provider', 'google')
        self.model_name = model_config.get('model_name', primary_model_key) # Fallback to key if name not set
        
        logger.info(f"Initializing Executor with Provider: {self.provider}, Model: {self.model_name}")
        
        if self.provider == 'openrouter':
            self.api_key = os.getenv('OPENROUTER_API_KEY')
            if not self.api_key:
                logger.error("OPENROUTER_API_KEY not found in environment!")
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        else:
            # Default to Google/Gemini
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                logger.error("GOOGLE_API_KEY not found in environment!")
            # Handle model name formatting for Gemini API
            gemini_model = self.model_name
            if "models/" not in gemini_model and self.provider == 'google':
                 gemini_model = f"models/{gemini_model}"
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/{gemini_model}:generateContent?key={self.api_key}"
        
        # System Message
        self.system_message = """
You are OMNI, an Expert Senior Software Engineer and AI Assistant.

Capabilities:
- Execute code in multiple languages (Python, Shell)
- Access and modify files  
- Control the computer
- Analyze data and create visualizations
- Browse the web

CODING STANDARDS (STRICT):
- Write PRODUCTION-GRADE code.
- ALWAYS use Type Hints (from typing import ...).
- ALWAYS include Docstrings and Comments.
- ALWAYS handle errors (try/except blocks).
- Modularize code into functions or classes; do not write flat scripts.
- Use meaningful variable names.
- Do not use placeholders like 'TODO' or 'pass'; implement the full logic.

IMPORTANT:
- When you want to DO something, WRITE THE CODE.
- Do not just explain how to do it.
- Wrap code in markdown blocks.

IMPORTANT: OUTPUT IN JSON FORMAT ONLY.
Your response must be a valid JSON object with the following structure:
{
  "thought": "Brief reasoning about what to do",
  "speech": "What you want to speak to the user (in Hindlish)",
  "code": {
    "language": "python" or "shell" or null,
    "content": "The code to execute" or null
  },
  "display": "Formatted markdown text to show in the chat window"
}

Example:
{
  "thought": "User wants to create a folder. I will use os.makedirs.",
  "speech": "Haan sir, main abhi folder bana deta hoon.",
  "code": {
    "language": "python",
    "content": "import os\\nos.makedirs('New Folder', exist_ok=True)"
  },
  "display": "Creating folder **New Folder**..."
}

Personality:
- Professional yet friendly like JARVIS
- Proactive and efficient
- Clear and concise communication

SELF-CORRECTION PROTOCOL:
- If code execution fails, analyze the error message.
- Do NOT repeat the exact same code.
- Try a different approach or library.
- If a file is missing, check if it exists or create it.
- If a command is not found, try a standard alternative (e.g., 'python' vs 'py').
"""
        logger.info("✓ Configured Open Interpreter with Custom Agent Loop")

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Route call to appropriate LLM provider."""
        if self.provider == 'openrouter':
            return self._call_openrouter(messages)
        else:
            return self._call_gemini(messages)

    def _call_openrouter(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenRouter API."""
        try:
            # Convert messages to OpenAI/OpenRouter format
            formatted_messages = [{"role": "system", "content": self.system_message}]
            
            for msg in messages:
                role = msg.get('role')
                content = msg.get('content')
                
                if role == 'function':
                    # OpenRouter/OpenAI usually expects 'function' role or user role with output
                    # Simulating as user message for compatibility with generic models
                    formatted_messages.append({"role": "user", "content": f"Code Output:\n{content}"})
                elif role == 'assistant':
                     formatted_messages.append({"role": "assistant", "content": content})
                else:
                     formatted_messages.append({"role": "user", "content": content})

            # Add JSON reminder
            formatted_messages.append({"role": "system", "content": "REMINDER: Output strictly in JSON format."})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/project-omni", 
                "X-Title": "Project OMNI",
            }
            
            data = {
                "model": self.model_name,
                "messages": formatted_messages,
                "temperature": 0.7,
                "response_format": {"type": "json_object"} # Try to force JSON if supported
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            
            if response.status_code != 200:
                return json.dumps({
                    "thought": f"OpenRouter API Error {response.status_code}",
                    "speech": "I'm having trouble connecting to OpenRouter.",
                    "code": {},
                    "display": f"API Error: {response.text}"
                })
                
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"OpenRouter Error: {e}")
            return json.dumps({
                "thought": "Connection error",
                "speech": "Connection failed.",
                "code": {},
                "display": f"Error: {e}"
            })

    def _call_gemini(self, messages: List[Dict[str, str]]) -> str:
        """Call Gemini REST API."""
        try:
            # Prepare contents
            contents = []
            
            # Add system message
            contents.append({'role': 'user', 'parts': [{'text': self.system_message}]})
            contents.append({'role': 'model', 'parts': [{'text': "Understood. I will output strictly in JSON format."}]})
            
            for msg in messages:
                role = msg.get('role')
                content = msg.get('content')
                
                parts = []
                # Check for image paths in content (simple heuristic)
                if isinstance(content, str) and ("Screenshot saved to" in content or ".png" in content):
                    # Try to extract path
                    import re
                    paths = re.findall(r"([a-zA-Z]:\\[^:\n]*\.png)", content)
                    if paths:
                        import base64
                        for path in paths:
                            try:
                                with open(path, "rb") as img_file:
                                    b64_data = base64.b64encode(img_file.read()).decode('utf-8')
                                    parts.append({
                                        "inline_data": {
                                            "mime_type": "image/png",
                                            "data": b64_data
                                        }
                                    })
                            except Exception as e:
                                logger.error(f"Failed to load image {path}: {e}")
                
                # Add text part
                parts.append({'text': str(content)})
                
                if role == 'system':
                    continue 
                elif role == 'user':
                    contents.append({'role': 'user', 'parts': parts})
                elif role == 'assistant':
                    contents.append({'role': 'model', 'parts': parts})
                elif role == 'function':
                    contents.append({'role': 'user', 'parts': [{'text': f"Code Output:\n{content}"}]})
            
            # Append strict reminder to the very end
            contents.append({'role': 'user', 'parts': [{'text': "REMINDER: Output strictly in JSON format as specified in the system prompt. No markdown outside the JSON."}]})
            
            # Prepare request
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.5, # Lower temperature for more deterministic formatting
                    "maxOutputTokens": 2048,
                    "responseMimeType": "application/json" # Force JSON mode if supported by API
                }
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            
            if response.status_code != 200:
                return json.dumps({
                    "thought": f"API Error {response.status_code}",
                    "speech": "I'm having trouble connecting to my brain.",
                    "code": {},
                    "display": f"API Error: {response.text}"
                })

            result = response.json()
            try:
                text = result['candidates'][0]['content']['parts'][0]['text']
                # Clean up markdown code blocks if model wraps JSON in them
                if text.strip().startswith('```json'):
                    text = text.strip().replace('```json', '').replace('```', '')
                elif text.strip().startswith('```'):
                    text = text.strip().replace('```', '')
                
                # Validate JSON
                json.loads(text)
                return text
            except (KeyError, IndexError, json.JSONDecodeError):
                # Retry logic could go here, but for now return a safe error JSON
                logger.error(f"Failed to parse JSON: {text if 'text' in locals() else 'No text'}")
                return json.dumps({
                    "thought": "Failed to parse JSON response",
                    "speech": "I understood, but I messed up my own formatting. Please ask again.",
                    "code": {},
                    "display": f"**Raw Output (Parse Error):**\n{text if 'text' in locals() else 'No output'}"
                })
                    
        except Exception as e:
            return f"REST Error: {e}"

    def _extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code from JSON response."""
        try:
            data = json.loads(text)
            code_data = data.get('code', {})
            if code_data and code_data.get('content'):
                return [(code_data.get('language', 'python'), code_data.get('content'))]
            return []
        except json.JSONDecodeError:
            # Fallback for non-JSON responses (legacy/error)
            return super()._extract_code_blocks(text) if hasattr(super(), '_extract_code_blocks') else [] # Avoid recursion if super doesn't have it, but here we are replacing the method so we should just implement the old logic as fallback or just return empty.
            # Actually, let's just implement the old regex logic here as fallback
            blocks = []
            lines = text.split('\n')
            in_block = False
            lang = ""
            code = []
            for line in lines:
                if line.strip().startswith('```'):
                    if in_block:
                        blocks.append((lang, '\n'.join(code)))
                        in_block = False
                        code = []
                    else:
                        in_block = True
                        lang = line.strip().replace('```', '').lower()
                        if not lang: lang = 'python'
                elif in_block:
                    code.append(line)
            return blocks

    def _execute_python(self, code: str) -> str:
        """Execute Python code."""
        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        sys.stderr = redirected_output
        
        try:
            exec(code, self.locals)
            return redirected_output.getvalue()
        except Exception:
            return redirected_output.getvalue() + traceback.format_exc()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def _execute_shell(self, code: str) -> str:
        """Execute Shell code."""
        try:
            result = subprocess.run(
                code, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)

    def execute(self, user_input: str, auto_run: bool = True) -> Dict[str, Any]:
        """Execute user command with agent loop."""
        logger.info(f"Processing: {user_input}")
        
        self.history.append({"role": "user", "content": user_input})
        
        max_turns = 5 # Prevent infinite loops
        full_output = []
        
        for _ in range(max_turns):
            # 1. Get response from LLM
            response_text = self._call_llm(self.history)
            self.history.append({"role": "assistant", "content": response_text})
            full_output.append(response_text)
            
            # 2. Extract code
            code_blocks = self._extract_code_blocks(response_text)
            
            if not code_blocks:
                break # No code to run, we are done
            
            # 3. Execute code
            outputs = []
            for lang, code in code_blocks:
                logger.info(f"Executing {lang} code...")
                if 'python' in lang:
                    output = self._execute_python(code)
                elif 'shell' in lang or 'bash' in lang or 'cmd' in lang:
                    output = self._execute_shell(code)
                else:
                    output = f"Unsupported language: {lang}"
                
                outputs.append(output)
                
            # 4. Feed output back
            combined_output = "\n".join(outputs)
            if not combined_output.strip():
                combined_output = "Code executed successfully (no output)."
                
            self.history.append({"role": "function", "content": combined_output})
            # Loop continues to let LLM react to output
            
        # Ensure we have a final response from the assistant
        if self.history and self.history[-1]['role'] == 'function':
            logger.info("Generating final response after execution...")
            final_response = self._call_llm(self.history)
            self.history.append({"role": "assistant", "content": final_response})
            full_output.append(final_response)

        # Return only the FINAL response for the GUI to parse
        last_assistant_msg = ""
        for msg in reversed(self.history):
            if msg['role'] == 'assistant':
                last_assistant_msg = msg['content']
                break
                
        return {
            'success': True,
            'output': last_assistant_msg if last_assistant_msg else "\n\n".join(full_output),
            'messages': self.history
        }
    
    def reset(self):
        """Reset conversation."""
        self.history = []
        self.locals = {}
        logger.info("Conversation reset")
