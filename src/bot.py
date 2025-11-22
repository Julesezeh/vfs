"""
VFS Appointment Booking Bot
Main bot class handling the automation workflow
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .browser_setup import BrowserSetup
from .telegram_notifier import TelegramNotifier
from .utils import TimingHelper, ElementHelper, ScreenshotHelper
from .field_mappings import VFSFieldMappings, VisaTypeFields
from .security_bypass import CloudflareHandler, VirtualKeyboardHandler


class VFSBookingBot:
    """Main bot class for VFS appointment booking automation"""

    def __init__(self, config: Dict[str, Any], credentials: Dict[str, Any]):
        """
        Initialize VFS booking bot

        Args:
            config: Configuration dictionary
            credentials: Credentials dictionary
        """
        self.config = config
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.browser_setup = BrowserSetup(config['browser'])
        self.driver = None
        self.timing = TimingHelper(config['timing'])
        self.element_helper = None
        self.screenshot_helper = None
        self.cloudflare_handler = None
        self.keyboard_handler = None

        # Initialize Telegram notifier
        telegram_config = config['telegram']
        self.notifier = TelegramNotifier(
            bot_token=telegram_config['bot_token'],
            chat_id=telegram_config['chat_id'],
            enabled=telegram_config['enabled']
        )

        # Bot state
        self.logged_in = False
        self.appointment_booked = False
        self.last_check_time = None

        self.logger.info("VFS Booking Bot initialized")

    def start(self):
        """Start the bot"""
        try:
            self.logger.info("Starting VFS Booking Bot...")

            # Create browser
            self.driver = self.browser_setup.create_driver()
            self.element_helper = ElementHelper(self.driver, self.timing)
            self.screenshot_helper = ScreenshotHelper(self.driver)
            self.cloudflare_handler = CloudflareHandler(self.driver, self.timing)
            self.keyboard_handler = VirtualKeyboardHandler(self.driver, self.timing)

            # Notify start
            if self.config['telegram'].get('notify_on_start', True):
                self.notifier.notify_start()

            # Run booking process
            if self.config['automation'].get('continuous_mode', True):
                self._continuous_booking_loop()
            else:
                self._single_booking_attempt()

        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
            self.notifier.send_message("Bot stopped by user")

        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            screenshot = None
            if self.screenshot_helper:
                screenshot = self.screenshot_helper.take_screenshot("fatal_error")
            self.notifier.notify_error(f"Fatal error: {str(e)}", screenshot)

        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up...")
        if self.driver:
            self.browser_setup.close()

    def _continuous_booking_loop(self):
        """Continuously check for appointments"""
        check_interval = self.config['automation']['check_interval']
        self.logger.info(f"Starting continuous mode (checking every {check_interval}s)")

        while not self.appointment_booked:
            try:
                self.logger.info("Starting booking attempt...")
                self._single_booking_attempt()

                if not self.appointment_booked:
                    self.logger.info(f"No slots found. Waiting {check_interval}s before next check...")
                    time.sleep(check_interval)

            except Exception as e:
                self.logger.error(f"Error in booking loop: {e}")
                self.notifier.notify_error(f"Error in booking loop: {str(e)}")
                time.sleep(check_interval)

    def _single_booking_attempt(self) -> bool:
        """
        Attempt to book an appointment

        Returns:
            True if booking successful, False otherwise
        """
        try:
            # Step 1: Login
            if not self.logged_in:
                if not self.login():
                    return False

            # Step 2: Navigate to appointment booking
            if not self.navigate_to_booking():
                return False

            # Step 3: Check for available slots
            slots = self.check_available_slots()
            if not slots:
                self.logger.info("No appointment slots available")
                self.notifier.notify_no_slots()
                return False

            # Step 4: Select slot
            selected_slot = self.select_best_slot(slots)
            if not selected_slot:
                return False

            # Notify slot found
            if self.config['telegram'].get('notify_on_slot_found', True):
                screenshot = self.screenshot_helper.take_screenshot("slot_found")
                self.notifier.notify_slot_found(
                    date=selected_slot.get('date', 'N/A'),
                    time=selected_slot.get('time', 'N/A'),
                    location=selected_slot.get('location', 'N/A'),
                    screenshot=screenshot
                )

            # Step 5: Fill application form
            if not self.fill_application_form():
                return False

            # Step 6: Review and submit (if auto_book enabled)
            if self.config['automation'].get('auto_book', False):
                if self.submit_booking():
                    self.appointment_booked = True
                    return True
            else:
                self.logger.info("Auto-booking disabled. Please complete manually.")
                self.notifier.send_message(
                    "Slot selected and form filled. Please complete booking manually."
                )
                # Keep browser open for manual completion
                input("Press Enter when you've completed the booking...")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error in booking attempt: {e}", exc_info=True)
            screenshot = self.screenshot_helper.take_screenshot("booking_error")
            self.notifier.notify_error(f"Booking error: {str(e)}", screenshot)
            return False

    def login(self) -> bool:
        """
        Login to VFS account

        Returns:
            True if login successful, False otherwise
        """
        try:
            self.logger.info("Logging in to VFS...")

            # Navigate to login page
            base_url = self.config['vfs']['base_url']

            # Try to load saved cookies first for faster bypass
            self.logger.info("Attempting to load saved session cookies...")
            if self.browser_setup.load_cookies(base_url):
                self.logger.info("Session cookies loaded successfully")
                # Check if already logged in
                if self._verify_login():
                    self.logger.info("Already logged in via saved session!")
                    self.logged_in = True
                    return True
            else:
                # No saved cookies, navigate normally
                self.driver.get(base_url)
                self.timing.wait_page_load()

            # Get Cloudflare timeout from config or use default
            cloudflare_timeout = self.config.get('cloudflare', {}).get('max_wait', 120)

            # Handle Cloudflare challenge if present
            self.logger.info("Checking for Cloudflare challenge...")
            if not self.cloudflare_handler.handle_cloudflare(max_wait=cloudflare_timeout):
                self.logger.warning("Cloudflare bypass may have failed or timed out")
                # Don't give up - sometimes it works anyway
                self.logger.info("Attempting to continue despite timeout...")
            else:
                # Successfully bypassed - save cookies for next time
                self.logger.info("Cloudflare bypassed! Saving session cookies...")
                self.browser_setup.save_cookies()

            # Take screenshot
            self.screenshot_helper.take_screenshot("login_page")

            # Find and fill email
            email_field = self._find_element_with_fallback('login_email')
            if not email_field:
                raise Exception("Could not find email field")

            self.element_helper.human_type(
                email_field,
                self.credentials['vfs_account']['email']
            )
            self.timing.wait_form_field()

            # Find and fill password
            password_field = self._find_element_with_fallback('login_password')
            if not password_field:
                raise Exception("Could not find password field")

            # Use smart password handler (handles virtual keyboards, direct input, etc.)
            password = self.credentials['vfs_account']['password']
            if not self.keyboard_handler.handle_password_input(password_field, password):
                self.logger.warning("Automatic password input may have failed")
                # Take screenshot for manual intervention
                self.screenshot_helper.take_screenshot("password_input_failed")
                # Wait for user to manually enter password if needed
                if not self.config['browser'].get('headless', False):
                    self.logger.info("Please enter password manually if needed...")
                    time.sleep(10)  # Give user time to intervene

            self.timing.wait_form_field()

            # Click login button
            login_button = self._find_element_with_fallback('login_button')
            if not login_button:
                raise Exception("Could not find login button")

            self.element_helper.safe_click(login_button)
            self.timing.wait_navigation()

            # Check if login successful
            if self._verify_login():
                self.logger.info("Login successful")
                self.logged_in = True
                self.screenshot_helper.take_screenshot("login_success")
                return True
            else:
                self.logger.error("Login failed - verification failed")
                self.screenshot_helper.take_screenshot("login_failed")
                return False

        except Exception as e:
            self.logger.error(f"Login error: {e}", exc_info=True)
            self.screenshot_helper.take_screenshot("login_error")
            return False

    def _verify_login(self) -> bool:
        """
        Verify if login was successful

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Wait a bit for page to load
            time.sleep(3)

            # Check for common indicators of successful login
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()

            # If still on login page, login failed
            if 'login' in current_url and 'dashboard' not in current_url:
                # Check for error messages
                if 'invalid' in page_source or 'incorrect' in page_source or 'error' in page_source:
                    return False

            # Look for dashboard or account indicators
            success_indicators = [
                'dashboard', 'account', 'appointment', 'booking',
                'welcome', 'home', 'profile'
            ]

            return any(indicator in current_url.lower() or indicator in page_source
                      for indicator in success_indicators)

        except Exception as e:
            self.logger.error(f"Error verifying login: {e}")
            return False

    def navigate_to_booking(self) -> bool:
        """
        Navigate to appointment booking page

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Navigating to booking page...")

            # Look for appointment/booking link
            possible_texts = [
                'Appointment', 'Book Appointment', 'Schedule', 'New Appointment',
                'Book', 'Booking', 'Schedule Appointment'
            ]

            for text in possible_texts:
                try:
                    xpath = f"//a[contains(text(), '{text}')] | //button[contains(text(), '{text}')]"
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element:
                        self.logger.info(f"Found booking link: {text}")
                        self.element_helper.safe_click(element)
                        self.timing.wait_navigation()
                        self.screenshot_helper.take_screenshot("booking_page")
                        return True
                except NoSuchElementException:
                    continue

            # If no link found, maybe already on booking page
            current_url = self.driver.current_url.lower()
            if 'appointment' in current_url or 'booking' in current_url:
                self.logger.info("Already on booking page")
                return True

            self.logger.warning("Could not find booking page")
            return False

        except Exception as e:
            self.logger.error(f"Error navigating to booking: {e}")
            return False

    def check_available_slots(self) -> List[Dict[str, str]]:
        """
        Check for available appointment slots

        Returns:
            List of available slot dictionaries
        """
        try:
            self.logger.info("Checking for available slots...")
            available_slots = []

            # Select appointment center
            center = self.config['vfs']['appointment_center']
            center_field = self._find_element_with_fallback('appointment_center')
            if center_field:
                self.element_helper.select_dropdown(center_field, center, by_text=True)
                self.timing.wait_form_field()

            # Select visa category
            visa_type = self.config['vfs']['visa_type']
            category_text = "Tourism" if visa_type == "tourist" else "Work"

            category_field = self._find_element_with_fallback('appointment_category')
            if category_field:
                self.element_helper.select_dropdown(category_field, category_text, by_text=True)
                self.timing.wait_form_field()

            # Click check availability or similar button
            check_button = self._find_element_with_fallback('check_availability_button')
            if check_button:
                self.element_helper.safe_click(check_button)
                self.timing.wait_page_load()

            # Look for available slots
            # Try different methods to find slots

            # Method 1: Look for calendar dates
            try:
                date_elements = self.driver.find_elements(By.CSS_SELECTOR, 'td.mat-calendar-body-cell:not(.mat-calendar-body-disabled)')
                if date_elements:
                    self.logger.info(f"Found {len(date_elements)} available dates in calendar")
                    for date_elem in date_elements[:5]:  # Check first 5 dates
                        try:
                            self.element_helper.safe_click(date_elem)
                            self.timing.wait_element()

                            # Look for time slots
                            time_slots = self.driver.find_elements(By.CSS_SELECTOR, 'mat-radio-button, div.time-slot')
                            if time_slots:
                                for time_slot in time_slots:
                                    slot_text = time_slot.text
                                    if slot_text and ':' in slot_text:
                                        available_slots.append({
                                            'date': date_elem.get_attribute('aria-label') or 'Unknown',
                                            'time': slot_text,
                                            'location': center,
                                            'element': time_slot
                                        })
                                        self.logger.info(f"Found slot: {slot_text}")
                        except:
                            continue
            except:
                pass

            # Method 2: Look for slot divs/cards
            try:
                slot_elements = self.driver.find_elements(By.XPATH, VFSFieldMappings.XPATH_SELECTORS['appointment_slot'])
                for slot_elem in slot_elements:
                    slot_text = slot_elem.text
                    if slot_text:
                        available_slots.append({
                            'date': 'Available',
                            'time': slot_text,
                            'location': center,
                            'element': slot_elem
                        })
            except:
                pass

            # Method 3: Check for "no slots" message
            no_slots = self._find_element_with_fallback('no_slots')
            if no_slots:
                self.logger.info("No slots available message found")
                return []

            self.logger.info(f"Found {len(available_slots)} available slots")
            self.screenshot_helper.take_screenshot("available_slots")

            return available_slots

        except Exception as e:
            self.logger.error(f"Error checking slots: {e}", exc_info=True)
            self.screenshot_helper.take_screenshot("slot_check_error")
            return []

    def select_best_slot(self, slots: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """
        Select the best available slot

        Args:
            slots: List of available slots

        Returns:
            Selected slot dictionary or None
        """
        try:
            if not slots:
                return None

            # Select first available slot (you can add custom logic here)
            selected_slot = slots[0]
            self.logger.info(f"Selecting slot: {selected_slot}")

            # Click on the slot element if available
            if 'element' in selected_slot:
                self.element_helper.safe_click(selected_slot['element'])
                self.timing.wait_form_field()

            return selected_slot

        except Exception as e:
            self.logger.error(f"Error selecting slot: {e}")
            return None

    def fill_application_form(self) -> bool:
        """
        Fill the application form with applicant details

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Filling application form...")

            applicant_data = self.credentials['applicant']
            visa_type = self.config['vfs']['visa_type']

            # Get required fields for this visa type
            required_fields = VisaTypeFields.get_required_fields(visa_type)

            # Fill each required field
            for field_name in required_fields:
                if field_name in applicant_data:
                    value = applicant_data[field_name]
                    if value:  # Only fill non-empty values
                        self._fill_form_field(field_name, str(value))

            # Handle checkboxes (terms, privacy, etc.)
            self._accept_terms_and_conditions()

            self.logger.info("Form filled successfully")
            self.screenshot_helper.take_screenshot("form_filled")

            # Click next/continue button
            next_button = self._find_element_with_fallback('next_button')
            if next_button:
                self.element_helper.safe_click(next_button)
                self.timing.wait_navigation()

            return True

        except Exception as e:
            self.logger.error(f"Error filling form: {e}", exc_info=True)
            self.screenshot_helper.take_screenshot("form_fill_error")
            return False

    def _fill_form_field(self, field_name: str, value: str) -> bool:
        """
        Fill a specific form field

        Args:
            field_name: Name of the field
            value: Value to fill

        Returns:
            True if successful, False otherwise
        """
        try:
            element = self._find_element_with_fallback(field_name)
            if not element:
                self.logger.warning(f"Could not find field: {field_name}")
                return False

            # Check if it's a select/dropdown
            tag_name = element.tag_name.lower()
            element_type = element.get_attribute('type')

            if tag_name == 'select' or 'mat-select' in element.get_attribute('class'):
                # It's a dropdown
                self.element_helper.select_dropdown(element, value, by_text=True)
            elif element_type == 'checkbox':
                # It's a checkbox
                if not element.is_selected():
                    self.element_helper.safe_click(element)
            else:
                # It's a text input
                self.element_helper.human_type(element, value)

            self.timing.wait_form_field()
            self.logger.debug(f"Filled field {field_name} with value: {value}")
            return True

        except Exception as e:
            self.logger.error(f"Error filling field {field_name}: {e}")
            return False

    def _accept_terms_and_conditions(self):
        """Accept terms and conditions checkboxes"""
        try:
            checkbox_fields = ['terms_checkbox', 'declaration_checkbox', 'privacy_checkbox']

            for checkbox_name in checkbox_fields:
                checkbox = self._find_element_with_fallback(checkbox_name)
                if checkbox and not checkbox.is_selected():
                    self.element_helper.safe_click(checkbox)
                    self.timing.wait_element()

        except Exception as e:
            self.logger.warning(f"Could not find/click terms checkbox: {e}")

    def submit_booking(self) -> bool:
        """
        Submit the booking

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Submitting booking...")

            # Look for submit/confirm/book button
            submit_button = (
                self._find_element_with_fallback('submit_button') or
                self._find_element_with_fallback('confirm_button') or
                self._find_element_with_fallback('book_button')
            )

            if not submit_button:
                self.logger.error("Could not find submit button")
                return False

            # Take screenshot before submission
            self.screenshot_helper.take_screenshot("before_submit")

            # Click submit
            self.element_helper.safe_click(submit_button)
            self.timing.wait_navigation()

            # Wait for confirmation
            time.sleep(5)

            # Check for success
            if self._verify_booking_success():
                self.logger.info("Booking submitted successfully!")

                # Get appointment details
                appointment_details = self._extract_appointment_details()

                # Take success screenshot
                screenshot = self.screenshot_helper.take_screenshot("booking_success")

                # Notify
                if self.config['telegram'].get('notify_on_booking_success', True):
                    self.notifier.notify_booking_success(appointment_details, screenshot)

                return True
            else:
                self.logger.error("Booking submission may have failed")
                self.screenshot_helper.take_screenshot("submit_failed")
                return False

        except Exception as e:
            self.logger.error(f"Error submitting booking: {e}", exc_info=True)
            self.screenshot_helper.take_screenshot("submit_error")
            return False

    def _verify_booking_success(self) -> bool:
        """
        Verify if booking was successful

        Returns:
            True if booking successful, False otherwise
        """
        try:
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()

            success_indicators = [
                'success', 'confirmed', 'booked', 'reference',
                'confirmation', 'thank you', 'appointment confirmed'
            ]

            # Check URL and page content
            return any(indicator in current_url or indicator in page_source
                      for indicator in success_indicators)

        except Exception as e:
            self.logger.error(f"Error verifying booking success: {e}")
            return False

    def _extract_appointment_details(self) -> Dict[str, str]:
        """
        Extract appointment details from confirmation page

        Returns:
            Dictionary with appointment details
        """
        details = {
            'date': 'N/A',
            'time': 'N/A',
            'location': self.config['vfs']['appointment_center'],
            'reference': 'N/A'
        }

        try:
            page_text = self.driver.page_source

            # Try to extract reference number
            import re
            ref_match = re.search(r'reference[:\s]+([A-Z0-9]+)', page_text, re.IGNORECASE)
            if ref_match:
                details['reference'] = ref_match.group(1)

            # You can add more extraction logic here based on actual page structure

        except Exception as e:
            self.logger.error(f"Error extracting appointment details: {e}")

        return details

    def _find_element_with_fallback(self, field_name: str):
        """
        Find element using multiple selector strategies

        Args:
            field_name: Name of the field to find

        Returns:
            WebElement or None
        """
        # Try CSS selectors
        selectors = VFSFieldMappings.get_field_selectors(field_name)
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    return element
            except NoSuchElementException:
                continue

        # Try XPath selector
        xpath = VFSFieldMappings.get_xpath_selector(field_name)
        if xpath:
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                if element:
                    return element
            except NoSuchElementException:
                pass

        return None
