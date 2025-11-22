"""
Security bypass handlers for VFS bot
Handles Cloudflare challenges and on-screen keyboards
"""

import logging
import time
import random
from typing import Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class CloudflareHandler:
    """Handles Cloudflare challenge detection and bypass with advanced strategies"""

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
        self.last_detection_type = None

    def detect_cloudflare(self) -> Tuple[bool, str]:
        """
        Detect if Cloudflare challenge is present with type identification

        Returns:
            Tuple of (is_detected, challenge_type)
            challenge_type can be: 'turnstile', 'jschallenge', 'managed', 'none'
        """
        try:
            page_source = self.driver.page_source.lower()

            # Check for Cloudflare Turnstile (interactive challenge)
            turnstile_indicators = [
                "//iframe[contains(@src, 'challenges.cloudflare.com')]",
                "//iframe[contains(@title, 'cloudflare')]",
                "//*[@id='cf-turnstile']",
                "//*[contains(@class, 'cf-turnstile')]"
            ]

            for indicator in turnstile_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element and element.is_displayed():
                        self.logger.info("Cloudflare Turnstile challenge detected")
                        self.last_detection_type = "turnstile"
                        return True, "turnstile"
                except:
                    continue

            # Check for JavaScript challenge (automatic)
            js_challenge_indicators = [
                "//title[contains(text(), 'Just a moment')]",
                "//*[contains(text(), 'Checking your browser')]",
                "//div[@id='cf-wrapper']",
                "//div[@class='cf-browser-verification']",
                "//*[contains(text(), 'please wait')]",
                "//*[contains(text(), 'DDoS protection')]"
            ]

            for indicator in js_challenge_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element:
                        self.logger.info("Cloudflare JavaScript challenge detected")
                        self.last_detection_type = "jschallenge"
                        return True, "jschallenge"
                except:
                    continue

            # Check for Cloudflare in page source
            if 'cloudflare' in page_source and any(phrase in page_source for phrase in
                ['checking your browser', 'just a moment', 'please wait', 'ray id']):
                self.logger.info("Cloudflare challenge detected in page source")
                self.last_detection_type = "managed"
                return True, "managed"

            # Check for challenge in iframe
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if 'cloudflare' in src.lower() or 'challenge' in src.lower():
                        self.logger.info("Cloudflare challenge detected in iframe")
                        self.last_detection_type = "turnstile"
                        return True, "turnstile"
            except:
                pass

            return False, "none"

        except Exception as e:
            self.logger.debug(f"Error detecting Cloudflare: {e}")
            return False, "none"

    def _simulate_human_behavior(self):
        """Simulate human-like mouse movements to appear more natural"""
        try:
            # Random mouse movements
            actions = ActionChains(self.driver)

            # Get window size
            window_size = self.driver.get_window_size()
            width = window_size['width']
            height = window_size['height']

            # Move to random position
            x = random.randint(100, width - 100)
            y = random.randint(100, height - 100)

            # Perform movement
            actions.move_by_offset(x // 2, y // 2).perform()
            time.sleep(random.uniform(0.1, 0.3))

            # Small random scroll
            scroll_amount = random.randint(-100, 100)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

        except Exception as e:
            self.logger.debug(f"Error simulating human behavior: {e}")

    def wait_for_cloudflare_bypass(self, timeout: int = 120, check_interval: float = 2.0) -> bool:
        """
        Wait for Cloudflare challenge to be bypassed with enhanced detection

        Args:
            timeout: Maximum time to wait in seconds (default: 120s for Cloudflare challenges)
            check_interval: How often to check in seconds (default: 2s)

        Returns:
            True if bypassed successfully, False if timeout
        """
        try:
            self.logger.info(f"Waiting for Cloudflare bypass (timeout: {timeout}s)...")
            start_time = time.time()
            last_url = self.driver.current_url
            check_count = 0

            while time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)
                check_count += 1

                # Log progress every 10 seconds
                if elapsed > 0 and elapsed % 10 == 0 and check_count % 5 == 0:
                    self.logger.info(f"Still waiting for Cloudflare bypass... ({elapsed}s elapsed)")

                # Check if challenge is gone
                is_detected, challenge_type = self.detect_cloudflare()
                if not is_detected:
                    self.logger.info("Cloudflare challenge resolved!")
                    # Extra wait for page to fully stabilize
                    time.sleep(3)
                    return True

                # Check for URL change (often indicates bypass success)
                current_url = self.driver.current_url
                if current_url != last_url:
                    self.logger.info(f"URL changed: {last_url} -> {current_url}")
                    last_url = current_url

                    # If URL changed and no challenge detected, likely succeeded
                    if not is_detected:
                        self.logger.info("Cloudflare bypassed (URL changed)")
                        time.sleep(3)
                        return True

                # Check page source for success indicators
                try:
                    page_source = self.driver.page_source.lower()

                    # If we see actual content (not challenge page), might be successful
                    content_indicators = ['login', 'email', 'password', 'dashboard', 'appointment']
                    challenge_indicators = ['checking your browser', 'just a moment', 'please wait']

                    has_content = any(indicator in page_source for indicator in content_indicators)
                    has_challenge = any(indicator in page_source for indicator in challenge_indicators)

                    if has_content and not has_challenge:
                        self.logger.info("Cloudflare bypassed (content detected)")
                        time.sleep(3)
                        return True

                except Exception as e:
                    self.logger.debug(f"Error checking page content: {e}")

                # Simulate human behavior periodically to avoid detection
                if check_count % 5 == 0:  # Every ~10 seconds
                    self._simulate_human_behavior()

                # Progressive check interval - check more frequently at first
                if elapsed < 30:
                    sleep_time = 1.5  # Check every 1.5s for first 30s
                else:
                    sleep_time = check_interval  # Then use normal interval

                time.sleep(sleep_time)

            self.logger.warning(f"Cloudflare bypass timeout after {timeout}s")
            # Take screenshot for debugging
            try:
                self.driver.save_screenshot("/tmp/cloudflare_timeout.png")
                self.logger.info("Saved timeout screenshot to /tmp/cloudflare_timeout.png")
            except:
                pass

            return False

        except Exception as e:
            self.logger.error(f"Error waiting for Cloudflare bypass: {e}")
            return False

    def handle_cloudflare(self, max_wait: int = 120) -> bool:
        """
        Detect and handle Cloudflare challenge with extended timeout

        Args:
            max_wait: Maximum time to wait for automatic bypass (default: 120s)

        Returns:
            True if handled/bypassed, False if failed
        """
        is_detected, challenge_type = self.detect_cloudflare()

        if is_detected:
            self.logger.info(f"Cloudflare challenge detected (type: {challenge_type})")
            self.logger.info("Waiting for automatic bypass - this may take up to 2 minutes...")

            # For Turnstile challenges, we might need even more time
            if challenge_type == "turnstile":
                self.logger.info("Turnstile challenge detected - using extended timeout")
                max_wait = max(max_wait, 150)  # At least 2.5 minutes for Turnstile

            return self.wait_for_cloudflare_bypass(timeout=max_wait)

        self.logger.debug("No Cloudflare challenge detected")
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
