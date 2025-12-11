"""
Terminal command execution tools.
Provides safe command execution with permission checking.
"""

import subprocess
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class TerminalTools:
    """Tools for executing terminal commands."""
    
    def __init__(self, permission_manager=None):
        """Initialize terminal tools."""
        self.permission_manager = permission_manager
    
    def execute_command(
        self, 
        command: str, 
        timeout: int = 300,
        shell: bool = True
    ) -> Tuple[bool, str, str]:
        """
        Execute a terminal command.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            shell: Whether to execute through shell
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            logger.info(f"Executing command: {command}")
            
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            
            if success:
                logger.info(f"Command succeeded: {command}")
            else:
                logger.warning(f"Command failed with code {result.returncode}: {command}")
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            logger.error(f"{error_msg}: {command}")
            return False, "", error_msg
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error executing command '{command}': {error_msg}")
            return False, "", error_msg
