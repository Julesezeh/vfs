"""
Security bypass handlers for VFS bot
Handles Cloudflare challenges and on-screen keyboards
"""

import logging
import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CloudflareHandler:
    """Handles Cloudflare challenge detection and bypass"""

    def __init__(self, driver, timing_helper):
        """
        Initialize Cloudflare handler

        Args:
            driver: Selenium WebDriver instance
            timing_helper: TimingHelper instance
        """
        self.driver = driver
        self.timing = timing_helper
        self.logger = logging.getLogger(__name__)

    def detect_cloudflare(self) -> bool:
        """
        Detect if Cloudflare challenge is present

        Returns:
            True if Cloudflare detected, False otherwise
        """
        try:
            # Check for common Cloudflare indicators
            cloudflare_indicators = [
                "//title[contains(text(), 'Just a moment')]",
                "//*[contains(text(), 'Checking your browser')]",
                "//*[contains(text(), 'Cloudflare')]",
                "//div[@id='cf-wrapper']",
                "//div[@class='cf-browser-verification']"
            ]

            for indicator in cloudflare_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element:
                        self.logger.info("Cloudflare challenge detected")
                        return True
                except:
                    continue

            return False

        except Exception as e:
            self.logger.debug(f"Error detecting Cloudflare: {e}")
            return False

    def wait_for_cloudflare_bypass(self, timeout: int = 30) -> bool:
        """
        Wait for Cloudflare challenge to be bypassed

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if bypassed successfully, False if timeout
        """
        try:
            self.logger.info("Waiting for Cloudflare bypass...")
            start_time = time.time()

            while time.time() - start_time < timeout:
                # Check if challenge is gone
                if not self.detect_cloudflare():
                    self.logger.info("Cloudflare bypassed successfully!")
                    time.sleep(2)  # Extra wait for page to stabilize
                    return True

                # Check if we're on a different page (bypass succeeded)
                current_url = self.driver.current_url.lower()
                if 'cloudflare' not in current_url and 'challenge' not in current_url:
                    page_source = self.driver.page_source.lower()
                    if 'checking your browser' not in page_source:
                        self.logger.info("Cloudflare bypassed (page changed)")
                        return True

                self.logger.debug("Still waiting for Cloudflare bypass...")
                time.sleep(2)

            self.logger.warning("Cloudflare bypass timeout")
            return False

        except Exception as e:
            self.logger.error(f"Error waiting for Cloudflare bypass: {e}")
            return False

    def handle_cloudflare(self, max_wait: int = 30) -> bool:
        """
        Detect and handle Cloudflare challenge

        Args:
            max_wait: Maximum time to wait for automatic bypass

        Returns:
            True if handled/bypassed, False if failed
        """
        if self.detect_cloudflare():
            self.logger.info("Cloudflare challenge detected - waiting for automatic bypass...")
            return self.wait_for_cloudflare_bypass(timeout=max_wait)
        return True  # No Cloudflare detected


class VirtualKeyboardHandler:
    """Handles on-screen/virtual keyboard password input"""

    def __init__(self, driver, timing_helper):
        """
        Initialize virtual keyboard handler

        Args:
            driver: Selenium WebDriver instance
            timing_helper: TimingHelper instance
        """
        self.driver = driver
        self.timing = timing_helper
        self.logger = logging.getLogger(__name__)

    def detect_virtual_keyboard(self) -> bool:
        """
        Detect if a virtual keyboard is present

        Returns:
            True if virtual keyboard detected, False otherwise
        """
        try:
            # Common virtual keyboard indicators
            keyboard_selectors = [
                "//div[contains(@class, 'virtual-keyboard')]",
                "//div[contains(@class, 'on-screen-keyboard')]",
                "//div[contains(@class, 'keyboard-container')]",
                "//div[contains(@id, 'keyboard')]",
                "//div[contains(@class, 'keypad')]"
            ]

            for selector in keyboard_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element and element.is_displayed():
                        self.logger.info("Virtual keyboard detected")
                        return True
                except:
                    continue

            return False

        except Exception as e:
            self.logger.debug(f"Error detecting virtual keyboard: {e}")
            return False

    def input_via_virtual_keyboard(self, text: str, keyboard_selector: Optional[str] = None) -> bool:
        """
        Input text using virtual/on-screen keyboard

        Args:
            text: Text to input
            keyboard_selector: Optional custom keyboard container selector

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Attempting virtual keyboard input...")

            # Find keyboard keys
            # VFS commonly uses buttons with data-key or similar attributes
            for char in text:
                char_lower = char.lower()
                char_upper = char.upper()

                # Try multiple selector strategies
                key_selectors = [
                    f"//button[@data-key='{char}']",
                    f"//button[@value='{char}']",
                    f"//button[text()='{char}']",
                    f"//div[@data-key='{char}']",
                    f"//span[text()='{char}']/parent::button",
                    # Try both cases
                    f"//button[contains(text(), '{char_lower}') or contains(text(), '{char_upper}')]",
                ]

                clicked = False
                for selector in key_selectors:
                    try:
                        key_element = self.driver.find_element(By.XPATH, selector)
                        if key_element and key_element.is_displayed():
                            # Click the key
                            key_element.click()
                            self.timing.wait_typing()
                            clicked = True
                            self.logger.debug(f"Clicked virtual key: {char}")
                            break
                    except:
                        continue

                if not clicked:
                    self.logger.warning(f"Could not find virtual key for: {char}")
                    # Try JavaScript injection as fallback
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error with virtual keyboard input: {e}")
            return False

    def input_password_direct(self, password_field, password: str) -> bool:
        """
        Bypass virtual keyboard by directly setting input value via JavaScript

        Args:
            password_field: Password field element
            password: Password to set

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Attempting direct password input via JavaScript...")

            # Method 1: Set value directly
            self.driver.execute_script(
                "arguments[0].value = arguments[1];",
                password_field,
                password
            )

            # Method 2: Trigger input event to ensure any listeners are called
            self.driver.execute_script(
                """
                var element = arguments[0];
                var value = arguments[1];
                element.value = value;

                // Trigger various events that might be monitored
                var events = ['input', 'change', 'keyup', 'keydown'];
                events.forEach(function(eventType) {
                    var event = new Event(eventType, { bubbles: true });
                    element.dispatchEvent(event);
                });
                """,
                password_field,
                password
            )

            # Verify value was set
            time.sleep(0.5)
            current_value = password_field.get_attribute('value')

            if current_value == password or len(current_value) == len(password):
                self.logger.info("Password set successfully via JavaScript")
                return True
            else:
                self.logger.warning("JavaScript password set verification failed")
                return False

        except Exception as e:
            self.logger.error(f"Error with direct password input: {e}")
            return False

    def handle_password_input(self, password_field, password: str) -> bool:
        """
        Smart password input handler - tries multiple methods

        Args:
            password_field: Password input element
            password: Password to input

        Returns:
            True if successful, False otherwise
        """
        try:
            # Strategy 1: Try direct JavaScript input first (fastest and most reliable)
            self.logger.info("Attempting password input...")

            if self.input_password_direct(password_field, password):
                return True

            # Strategy 2: Check for virtual keyboard
            if self.detect_virtual_keyboard():
                self.logger.info("Virtual keyboard detected, attempting keyboard input...")
                if self.input_via_virtual_keyboard(password):
                    return True

            # Strategy 3: Try regular typing (may trigger keyboard)
            try:
                self.logger.info("Attempting regular password typing...")
                password_field.clear()
                time.sleep(0.5)

                for char in password:
                    password_field.send_keys(char)
                    self.timing.wait_typing()

                return True
            except Exception as e:
                self.logger.warning(f"Regular typing failed: {e}")

            # Strategy 4: Manual intervention
            self.logger.warning("Automatic password input failed - manual intervention may be required")
            return False

        except Exception as e:
            self.logger.error(f"Error handling password input: {e}")
            return False
