"""
Browser automation tools for Project OMNI - Phase 5.
Playwright integration for web automation.
Thread-safe implementation using a persistent background event loop.
"""

import logging
import asyncio
import threading
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BrowserAutomation:
    """Browser automation using Playwright with a persistent background loop."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize browser automation.
        
        Args:
            headless: Run browser in headless mode
        """
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None
        
        # Create a dedicated event loop for this browser instance
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
    def _run_loop(self):
        """Run the dedicated event loop."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_async(self, coro):
        """Run a coroutine on the background loop and wait for result."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def start(self, browser_type: str = "chromium", use_profile: bool = True):
        """Start the browser (Synchronous wrapper)."""
        return self._run_async(self._start_async(browser_type, use_profile))

    async def _start_async(self, browser_type: str, use_profile: bool):
        """Async implementation of start."""
        try:
            from playwright.async_api import async_playwright
            import os
            
            self.playwright = await async_playwright().start()
            
            # Common args to reduce detection (Stealth Mode)
            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--start-maximized"
            ]
            
            if use_profile and browser_type == "chromium":
                # Path to local Chrome profile
                user_data_dir = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
                
                # Check if Chrome is running (simple check, might need more robust handling)
                # For now, we assume user might need to close Chrome or we use a copy?
                # Using the real profile requires Chrome to be closed.
                # Let's try to use it directly.
                
                logger.info(f"Using Chrome Profile at: {user_data_dir}")
                
                self.browser = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False, # Must be false for profile
                    channel="chrome", # Use actual Chrome installation
                    args=args,
                    viewport=None # Allow full window size
                )
                self.page = self.browser.pages[0]
                
            else:
                # Standard clean instance
                if browser_type == "chromium":
                    self.browser = await self.playwright.chromium.launch(headless=self.headless, args=args)
                elif browser_type == "firefox":
                    self.browser = await self.playwright.firefox.launch(headless=self.headless, args=args)
                elif browser_type == "webkit":
                    self.browser = await self.playwright.webkit.launch(headless=self.headless, args=args)
                
                self.page = await self.browser.new_page()
            
            logger.info(f"Started {browser_type} browser (Profile: {use_profile})")
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            # Fallback to clean browser if profile is locked
            if use_profile:
                logger.warning("Profile locked? Retrying with clean browser...")
                await self._start_async(browser_type, use_profile=False)
            else:
                raise
    
    def navigate(self, url: str) -> bool:
        """Navigate to a URL (Synchronous wrapper)."""
        return self._run_async(self._navigate_async(url))

    async def _navigate_async(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")
            
            await self.page.goto(url)
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    def click_element(self, selector: str) -> bool:
        """Click an element (Synchronous wrapper)."""
        return self._run_async(self._click_element_async(selector))

    async def _click_element_async(self, selector: str) -> bool:
        """
        Click an element.
        
        Args:
            selector: CSS selector
            
        Returns:
            True if successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")
            
            await self.page.click(selector)
            logger.info(f"Clicked element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Error clicking {selector}: {e}")
            return False
    
    def fill_input(self, selector: str, text: str) -> bool:
        """Fill an input field (Synchronous wrapper)."""
        return self._run_async(self._fill_input_async(selector, text))

    async def _fill_input_async(self, selector: str, text: str) -> bool:
        """
        Fill an input field.
        
        Args:
            selector: CSS selector
            text: Text to fill
            
        Returns:
            True if successful
        """
        try:
            if not self.page: raise RuntimeError("Browser not started")
            await self.page.fill(selector, text)
            logger.info(f"Filled input {selector}")
            return True
        except Exception as e:
            logger.error(f"Error filling {selector}: {e}")
            return False

    def get_text(self, selector: str) -> str:
        """Get text content (Synchronous wrapper)."""
        return self._run_async(self._get_text_async(selector))

    async def _get_text_async(self, selector: str) -> str:
        """
        Get text content of an element.
        
        Args:
            selector: CSS selector
            
        Returns:
            Element text or empty string if not found or error.
        """
        try:
            if not self.page: return ""
            return await self.page.inner_text(selector)
        except Exception as e:
            logger.error(f"Error getting text from {selector}: {e}")
            return ""

    def wait_for_user(self):
        """Pause execution (Synchronous wrapper)."""
        return self._run_async(self._wait_for_user_async())

    async def _wait_for_user_async(self):
        """
        Pause execution and wait for user interaction.
        """
        if not self.page: return
        logger.info("Waiting for user interaction...")
        print("⏸️ PAUSED: Please solve the CAPTCHA or interact with the browser.")
        await asyncio.sleep(30)
        print("▶️ RESUMING...")
    
    def screenshot(self, path: str) -> bool:
        """Take a screenshot (Synchronous wrapper)."""
        return self._run_async(self._screenshot_async(path))

    async def _screenshot_async(self, path: str) -> bool:
        """
        Take a screenshot.
        
        Args:
            path: Path to save screenshot
            
        Returns:
            True if successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")
            
            await self.page.screenshot(path=path)
            logger.info(f"Screenshot saved: {path}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    def close(self):
        """Close the browser (Synchronous wrapper)."""
        return self._run_async(self._close_async())

    async def _close_async(self):
        """Close the browser."""
        try:
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

