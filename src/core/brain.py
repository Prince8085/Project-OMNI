"""
OmniBrain - The intelligence core of Project OMNI.
Handles decision-making, context management, and task routing.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from src.executors.open_interpreter import OpenInterpreterExecutor
from src.executors.computer_use import ComputerUseModule
from src.safety.permissions import ActionLogger
# Lazy imports for optional modules to prevent startup crashes
# from src.core.rag import RAGModule
# from src.tools.iot import SmartHome
# from src.tools.mobile_link import MobileLink

logger = logging.getLogger(__name__)

class OmniBrain:
    """
    The main intelligence engine for OMNI.
    Orchestrates execution, safety checks, and context management.
    """
    
    def __init__(self):
        """Initialize the brain."""
        self.config = self._load_config()
        self.executor = OpenInterpreterExecutor(self.config)
        self.action_logger = ActionLogger()
        
        # Initialize RAG (Super Brain)
        try:
            from src.core.rag import RAGModule
            self.rag = RAGModule()
            self.rag_active = True
        except Exception as e:
            logger.warning(f"RAG Module failed to load: {e}")
            self.rag_active = False

        # Initialize IoT (Smart Home)
        try:
            from src.tools.iot import SmartHome
            self.iot = SmartHome()
        except Exception as e:
            logger.warning(f"IoT Module failed to load: {e}")
            self.iot = None
        
        # Initialize Mobile Link (Telegram)
        try:
            from src.tools.mobile_link import MobileLink
            self.mobile = MobileLink(callback=lambda text: self.process_command(text, auto_run=True))
            import threading
            if self.mobile.is_active:
                threading.Thread(target=self.mobile.run, daemon=True).start()
        except Exception as e:
            logger.warning(f"Mobile Link failed to load: {e}")
            self.mobile = None
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            config_path = Path('config/models.yaml')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            return {}
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            return {}

    def process_command(self, user_input: str, auto_run: bool = False) -> Dict[str, Any]:
        """
        Process a user command.
        
        Args:
            user_input: The natural language command
            auto_run: Whether to execute without confirmation
            
        Returns:
            Dict containing execution results
        """
        try:
            if not auto_run:
                require_confirmation = self.config.get('execution', {}).get(
                    'require_confirmation', True
                )
                auto_run = not require_confirmation
            
            # RAG: Ingest if requested
            if "learn this file" in user_input.lower() or "read this file" in user_input.lower():
                # Extract path (simple heuristic)
                import re
                paths = re.findall(r"([a-zA-Z]:\\[^:\n]*\.(?:pdf|txt|md|py))", user_input)
                if paths:
                    for path in paths:
                        result = self.rag.ingest_file(path)
                        return {'success': True, 'output': f"Memory Updated: {result}"}

            # RAG: Retrieve Context
            rag_context = ""
            if self.rag_active:
                rag_context = self.rag.query(user_input)
                if rag_context:
                    rag_context = f"\n\n[RELEVANT MEMORY]:\n{rag_context}\n"
            
            # Execute using Open Interpreter
            full_prompt = f"{user_input}{rag_context}"
            result = self.executor.execute(full_prompt, auto_run=auto_run)
            
            # Log the action
            self.action_logger.log_action(
                operation='execute_command',
                details={
                    'command': user_input,
                    'auto_run': auto_run,
                    'success': result.get('success', False)
                },
                success=result.get('success', False)
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing command: {e}"
            logger.error(error_msg)
            
            self.action_logger.log_action(
                operation='execute_command',
                details={'command': user_input, 'error': str(e)},
                success=False
            )
            
            return {
                'success': False,
                'error': error_msg,
                'output': error_msg
            }
    
    def reset(self):
        """Reset the brain state."""
        self.executor.reset()
        logger.info("OmniBrain reset")
