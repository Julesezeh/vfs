"""
Utility functions for VFS booking bot
Includes timing, waiting, screenshot, and helper functions
"""

import logging
import random
import time
import os
from datetime import datetime
from typing import Tuple, Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TimingHelper:
    """Handles human-like timing and delays"""

    def __init__(self, timing_config: dict):
        """
        Initialize timing helper

        Args:
            timing_config: Timing configuration from config file
        """
        self.config = timing_config
        self.logger = logging.getLogger(__name__)

    def get_random_delay(self, delay_type: str) -> float:
        """
        Get random delay for specified type

        Args:
            delay_type: Type of delay (page_load_wait, element_wait, etc.)

        Returns:
            Random delay in seconds
        """
        delay_range = self.config.get(delay_type, [1, 3])
        return random.uniform(delay_range[0], delay_range[1])

    def wait_page_load(self):
        """Wait for page load with random delay"""
        delay = self.get_random_delay('page_load_wait')
        self.logger.debug(f"Waiting {delay:.2f}s for page load")
        time.sleep(delay)

    def wait_element(self):
        """Wait before interacting with element"""
        delay = self.get_random_delay('element_wait')
        self.logger.debug(f"Waiting {delay:.2f}s before element interaction")
        time.sleep(delay)

    def wait_typing(self):
        """Delay between keystrokes"""
        delay = self.get_random_delay('typing_delay')
        time.sleep(delay)

    def wait_click(self):
        """Wait before clicking"""
        delay = self.get_random_delay('click_delay')
        self.logger.debug(f"Waiting {delay:.2f}s before click")
        time.sleep(delay)

    def wait_form_field(self):
        """Wait between form fields"""
        delay = self.get_random_delay('form_field_delay')
        self.logger.debug(f"Waiting {delay:.2f}s between form fields")
        time.sleep(delay)

    def wait_navigation(self):
        """Wait for navigation"""
        delay = self.get_random_delay('navigation_delay')
        self.logger.debug(f"Waiting {delay:.2f}s for navigation")
        time.sleep(delay)


class ElementHelper:
    """Helper functions for element interactions"""

    def __init__(self, driver, timing_helper: TimingHelper):
        """
        Initialize element helper

        Args:
            driver: Selenium WebDriver instance
            timing_helper: TimingHelper instance
        """
        self.driver = driver
        self.timing = timing_helper
        self.logger = logging.getLogger(__name__)

    def wait_for_element(
        self,
        by: By,
        value: str,
        timeout: int = 20,
        condition: str = 'presence'
    ) -> Optional[WebElement]:
        """
        Wait for element with specified condition

        Args:
            by: Selenium By locator type
            value: Locator value
            timeout: Maximum wait time in seconds
            condition: Condition type (presence, visible, clickable)

        Returns:
            WebElement if found, None otherwise
        """
        try:
            conditions = {
                'presence': EC.presence_of_element_located,
                'visible': EC.visibility_of_element_located,
                'clickable': EC.element_to_be_clickable
            }

            condition_func = conditions.get(condition, EC.presence_of_element_located)
            element = WebDriverWait(self.driver, timeout).until(
                condition_func((by, value))
            )
            return element

        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element: {value}")
            return None
        except Exception as e:
            self.logger.error(f"Error waiting for element {value}: {e}")
            return None

    def safe_click(self, element: WebElement, use_js: bool = False) -> bool:
        """
        Safely click an element with human-like behavior

        Args:
            element: WebElement to click
            use_js: Use JavaScript click instead of regular click

        Returns:
            True if successful, False otherwise
        """
        try:
            self.timing.wait_click()

            if use_js:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                # Move to element first (more human-like)
                ActionChains(self.driver).move_to_element(element).pause(0.2).click().perform()

            return True

        except Exception as e:
            self.logger.error(f"Error clicking element: {e}")
            # Try JavaScript click as fallback
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                return False

    def human_type(self, element: WebElement, text: str, clear_first: bool = True) -> bool:
        """
        Type text with human-like delays

        Args:
            element: WebElement to type into
            text: Text to type
            clear_first: Clear field before typing

        Returns:
            True if successful, False otherwise
        """
        try:
            self.timing.wait_element()

            if clear_first:
                element.clear()
                time.sleep(0.2)

            # Type character by character with random delays
            for char in text:
                element.send_keys(char)
                self.timing.wait_typing()

            return True

        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False

    def select_dropdown(
        self,
        element: WebElement,
        value: str,
        by_text: bool = True
    ) -> bool:
        """
        Select value from dropdown

        Args:
            element: Dropdown element
            value: Value to select
            by_text: Select by visible text (True) or value (False)

        Returns:
            True if successful, False otherwise
        """
        try:
            from selenium.webdriver.support.ui import Select

            self.timing.wait_element()
            select = Select(element)

            if by_text:
                select.select_by_visible_text(value)
            else:
                select.select_by_value(value)

            return True

        except Exception as e:
            self.logger.error(f"Error selecting dropdown value: {e}")
            return False

    def is_element_present(self, by: By, value: str) -> bool:
        """
        Check if element is present

        Args:
            by: Selenium By locator type
            value: Locator value

        Returns:
            True if element present, False otherwise
        """
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False


class ScreenshotHelper:
    """Helper for taking and managing screenshots"""

    def __init__(self, driver, screenshot_dir: str = "screenshots"):
        """
        Initialize screenshot helper

        Args:
            driver: Selenium WebDriver instance
            screenshot_dir: Directory to save screenshots
        """
        self.driver = driver
        self.screenshot_dir = screenshot_dir
        self.logger = logging.getLogger(__name__)

        # Create screenshot directory if it doesn't exist
        os.makedirs(screenshot_dir, exist_ok=True)

    def take_screenshot(self, name: str = "screenshot") -> Optional[str]:
        """
        Take screenshot and save to file

        Args:
            name: Base name for screenshot file

        Returns:
            Path to saved screenshot or None if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)

            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")

            return filepath

        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return None


class RetryHelper:
    """Helper for retry logic"""

    @staticmethod
    def retry_with_backoff(
        func,
        max_retries: int = 3,
        initial_delay: int = 1,
        backoff_factor: int = 2,
        exceptions: Tuple = (Exception,)
    ):
        """
        Retry function with exponential backoff

        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for delay after each retry
            exceptions: Tuple of exceptions to catch

        Returns:
            Function result or raises last exception
        """
        logger = logging.getLogger(__name__)
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                return func()
            except exceptions as e:
                if attempt == max_retries - 1:
                    logger.error(f"Max retries reached. Last error: {e}")
                    raise

                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= backoff_factor


def setup_logging(config: dict) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        config: Logging configuration dictionary

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config.get('log_file', 'logs/vfs_bot.log'))
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging level
    level_str = config.get('level', 'INFO')
    level = getattr(logging, level_str, logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Setup handlers
    handlers = []

    if config.get('log_to_console', True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    if config.get('log_to_file', True):
        file_handler = logging.FileHandler(config['log_file'])
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )

    return logging.getLogger('VFSBot')
