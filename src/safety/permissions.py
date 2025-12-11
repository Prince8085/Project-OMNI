"""
Safety and permission management system for Project OMNI.
Handles authorization, dangerous command detection, and action logging.
"""

import re
import logging
from typing import List, Tuple
from enum import Enum
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class PermissionTier(Enum):
    """Permission levels for operations."""
    SAFE = "safe"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    BLOCKED = "blocked"


class PermissionManager:
    """Manages operation permissions and safety checks."""
    
    def __init__(self, config_path: str = "config/models.yaml"):
        """Initialize permission manager with configuration."""
        self.config = self._load_config(config_path)
        self.blocked_patterns = self._load_blocked_patterns()
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Return default configuration."""
        return {
            'safety': {
                'auto_approve_safe_commands': True,
                'max_file_operations_per_command': 10,
                'safe_operations': ['read_file', 'list_directory', 'get_file_info'],
                'requires_confirmation': ['write_file', 'delete_file', 'execute_command'],
                'blocked_operations': ['format_disk', 'delete_system_files']
            }
        }
    
    def _load_blocked_patterns(self) -> List[re.Pattern]:
        """Load dangerous command patterns from file."""
        patterns = []
        pattern_file = Path("config/blocked_commands.txt")
        
        if pattern_file.exists():
            try:
                with open(pattern_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                patterns.append(re.compile(line))
                            except re.error as e:
                                logger.warning(f"Invalid regex pattern '{line}': {e}")
            except Exception as e:
                logger.error(f"Error loading blocked patterns: {e}")
        
        return patterns
    
    def check_permission(self, operation: str, command: str = "") -> Tuple[PermissionTier, str]:
        """
        Check permission level for an operation.
        
        Args:
            operation: The operation type (e.g., 'write_file', 'execute_command')
            command: Optional command string to check against blocked patterns
            
        Returns:
            Tuple of (PermissionTier, reason)
        """
        safety_config = self.config.get('safety', {})
        
        # Check if operation is explicitly blocked
        if operation in safety_config.get('blocked_operations', []):
            return PermissionTier.BLOCKED, f"Operation '{operation}' is blocked for safety"
        
        # Check command against dangerous patterns
        if command:
            is_blocked, reason = self._check_dangerous_command(command)
            if is_blocked:
                return PermissionTier.BLOCKED, reason
        
        # Check if operation requires confirmation
        if operation in safety_config.get('requires_confirmation', []):
            return PermissionTier.REQUIRES_CONFIRMATION, "Operation requires user confirmation"
        
        # Check if operation is safe
        if operation in safety_config.get('safe_operations', []):
            return PermissionTier.SAFE, "Operation is safe to auto-execute"
        
        # Default to requiring confirmation for unknown operations
        return PermissionTier.REQUIRES_CONFIRMATION, "Unknown operation, requiring confirmation"
    
    def _check_dangerous_command(self, command: str) -> Tuple[bool, str]:
        """
        Check if command matches any dangerous patterns.
        
        Returns:
            Tuple of (is_dangerous, reason)
        """
        for pattern in self.blocked_patterns:
            if pattern.search(command):
                return True, f"Command matches blocked pattern: {pattern.pattern}"
        
        return False, ""
    
    def can_auto_execute(self, operation: str, command: str = "") -> bool:
        """
        Check if operation can be auto-executed without confirmation.
        
        Args:
            operation: The operation type
            command: Optional command string
            
        Returns:
            True if can auto-execute, False otherwise
        """
        tier, _ = self.check_permission(operation, command)
        
        safety_config = self.config.get('safety', {})
        auto_approve_safe = safety_config.get('auto_approve_safe_commands', True)
        
        return tier == PermissionTier.SAFE and auto_approve_safe


class ActionLogger:
    """Logs all actions for audit trail."""
    
    def __init__(self, log_dir: str = "~/.omni/logs"):
        """Initialize action logger."""
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging to file."""
        log_file = self.log_dir / "actions.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    
    def log_action(self, operation: str, details: dict, success: bool = True):
        """
        Log an action to the audit trail.
        
        Args:
            operation: The operation performed
            details: Dictionary with operation details
            success: Whether operation succeeded
        """
        log_entry = {
            'operation': operation,
            'success': success,
            **details
        }
        
        if success:
            logger.info(f"Action executed: {log_entry}")
        else:
            logger.error(f"Action failed: {log_entry}")
