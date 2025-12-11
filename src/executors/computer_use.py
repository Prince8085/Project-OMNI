"""
Computer Use module for Project OMNI - Phase 3.
Vision-based GUI automation using screenshots and AI vision.
"""

import logging
from typing import Dict, Any, Tuple, Optional
import time

logger = logging.getLogger(__name__)


class ComputerUseModule:
    """Vision-based computer control using AI vision models."""
    
    def __init__(self, vision_model: str = "gpt-4-vision-preview"):
        """
        Initialize Computer Use module.
        
        Args:
            vision_model: Vision model to use for screen understanding
        """
        self.vision_model = vision_model
        self.screen_width = 1920
        self.screen_height = 1080
        
        try:
            import pyautogui
            pyautogui.FAILSAFE = True  # Move mouse to corner to abort
            self.pyautogui = pyautogui
            
            # Get actual screen size
            self.screen_width, self.screen_height = pyautogui.size()
            logger.info(f"Screen size: {self.screen_width}x{self.screen_height}")
        except ImportError:
            logger.warning("PyAutoGUI not available. GUI automation disabled.")
            self.pyautogui = None
    
    def take_screenshot(self, save_path: Optional[str] = None) -> str:
        """
        Take a screenshot of the current screen.
        
        Args:
            save_path: Path to save screenshot (optional)
            
        Returns:
            Path to screenshot
        """
        try:
            if not self.pyautogui:
                raise RuntimeError("PyAutoGUI not available")
            
            if not save_path:
                import tempfile
                save_path = tempfile.mktemp(suffix='.png')
            
            screenshot = self.pyautogui.screenshot()
            screenshot.save(save_path)
            
            logger.info(f"Screenshot saved: {save_path}")
            return save_path
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            raise
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> bool:
        """
        Click at specific coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            
        Returns:
            True if successful
        """
        try:
            if not self.pyautogui:
                raise RuntimeError("PyAutoGUI not available")
            
            self.pyautogui.click(x, y, clicks=clicks, button=button)
            logger.info(f"Clicked at ({x}, {y}) with {button} button")
            return True
        except Exception as e:
            logger.error(f"Error clicking: {e}")
            raise
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text using keyboard.
        
        Args:
            text: Text to type
            interval: Interval between keystrokes
            
        Returns:
            True if successful
        """
        try:
            if not self.pyautogui:
                raise RuntimeError("PyAutoGUI not available")
            
            self.pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            raise
    
    def press_key(self, key: str, presses: int = 1) -> bool:
        """
        Press a keyboard key.
        
        Args:
            key: Key name (e.g., 'enter', 'tab', 'ctrl')
            presses: Number of times to press
            
        Returns:
            True if successful
        """
        try:
            if not self.pyautogui:
                raise RuntimeError("PyAutoGUI not available")
            
            self.pyautogui.press(key, presses=presses)
            logger.info(f"Pressed key: {key} ({presses} times)")
            return True
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            raise
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        Move mouse to coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
            
        Returns:
            True if successful
        """
        try:
            if not self.pyautogui:
                raise RuntimeError("PyAutoGUI not available")
            
            self.pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
            raise
    
    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Find an image on screen and return its center coordinates.
        
        Args:
            image_path: Path to image to find
            confidence: Match confidence (0.0 to 1.0)
            
        Returns:
            (x, y) coordinates if found, None otherwise
        """
        try:
            if not self.pyautogui:
                raise RuntimeError("PyAutoGUI not available")
            
            location = self.pyautogui.locateCenterOnScreen(
                image_path, 
                confidence=confidence
            )
            
            if location:
                logger.info(f"Found image at {location}")
                return location
            else:
                logger.info(f"Image not found: {image_path}")
                return None
        except Exception as e:
            logger.error(f"Error finding image: {e}")
            return None
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            (x, y) coordinates
        """
        try:
            if not self.pyautogui:
                raise RuntimeError("PyAutoGUI not available")
            
            return self.pyautogui.position()
        except Exception as e:
            logger.error(f"Error getting mouse position: {e}")
            raise
