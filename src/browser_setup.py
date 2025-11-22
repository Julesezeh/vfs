"""
Browser setup and configuration for VFS bot
Handles Chrome driver setup with proxy and anti-detection measures
"""

import logging
import os
import zipfile
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from typing import Optional


class BrowserSetup:
    """Handles browser initialization with anti-detection features"""

    def __init__(self, config: dict):
        """
        Initialize browser setup

        Args:
            config: Browser configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.driver = None

    def create_driver(self) -> uc.Chrome:
        """
        Create and configure Chrome WebDriver with anti-detection measures

        Returns:
            Configured Chrome WebDriver instance
        """
        self.logger.info("Setting up Chrome browser...")

        # Configure Chrome options
        options = uc.ChromeOptions()

        # Headless mode
        if self.config.get('headless', False):
            options.add_argument('--headless=new')
            self.logger.info("Running in headless mode")

        # Window size
        width = self.config.get('window_width', 1920)
        height = self.config.get('window_height', 1080)
        options.add_argument(f'--window-size={width},{height}')

        # User agent
        user_agent = self.config.get('user_agent', 'auto')
        if user_agent == 'auto':
            ua = UserAgent()
            user_agent = ua.chrome
        options.add_argument(f'user-agent={user_agent}')
        self.logger.info(f"Using user agent: {user_agent}")

        # Proxy configuration
        proxy_extension = None
        if self.config.get('use_proxy', False):
            proxy_config, proxy_extension = self._setup_proxy()
            if proxy_config:
                options.add_argument(f'--proxy-server={proxy_config}')
                self.logger.info(f"Using proxy: {proxy_config}")

                # Add proxy auth extension if created
                if proxy_extension:
                    options.add_extension(proxy_extension)
                    self.logger.info("Proxy authentication extension loaded")

        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        # Don't disable extensions - we need them for proxy auth
        # options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')

        # Ensure NOT in incognito mode (proxy extensions don't work in incognito)
        # Remove any incognito flags that might have been set

        # Additional stealth options
        # Note: undetected-chromedriver handles these automatically
        # Commenting out to avoid conflicts with newer Chrome versions
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)

        # Preferences to appear more human-like
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_settings.popups": 0,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        try:
            # Create undetected Chrome driver
            self.logger.info("Initializing undetected Chrome driver...")
            self.driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                use_subprocess=True,
                user_data_dir=None  # Use temporary profile, not incognito
            )

            # Additional JavaScript to hide WebDriver
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })

            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            # Set timeouts
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)

            self.logger.info("Browser initialized successfully")
            return self.driver

        except Exception as e:
            self.logger.error(f"Error creating browser: {e}")
            raise

    def _setup_proxy(self) -> tuple[Optional[str], Optional[str]]:
        """
        Setup proxy configuration

        Returns:
            Tuple of (proxy_string, extension_path)
        """
        host = self.config.get('proxy_host', '')
        port = self.config.get('proxy_port', '')
        user = self.config.get('proxy_user', '')
        password = self.config.get('proxy_pass', '')

        if not host or not port:
            self.logger.warning("Proxy enabled but host/port not configured")
            return None, None

        # Proxy string without auth for Chrome argument
        proxy_str = f"{host}:{port}"

        # Create auth extension if username and password provided
        if user and password:
            extension_path = self._create_proxy_auth_extension(host, port, user, password)
            return proxy_str, extension_path
        else:
            return proxy_str, None

    def _create_proxy_auth_extension(self, host: str, port: str, user: str, password: str) -> str:
        """
        Create a Chrome extension for proxy authentication

        Args:
            host: Proxy host
            port: Proxy port
            user: Proxy username
            password: Proxy password

        Returns:
            Path to the created extension zip file
        """
        import tempfile

        # Create extension directory
        extension_dir = tempfile.mkdtemp()

        # Manifest file
        manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Proxy Auth",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version": "76.0.0"
}
"""

        # Background script for proxy authentication
        background_js = """
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {urls: ["<all_urls>"]},
    ['blocking']
);
""" % (host, port, user, password)

        # Write files
        manifest_path = os.path.join(extension_dir, 'manifest.json')
        background_path = os.path.join(extension_dir, 'background.js')

        with open(manifest_path, 'w') as f:
            f.write(manifest_json)

        with open(background_path, 'w') as f:
            f.write(background_js)

        # Create zip file
        extension_zip = os.path.join(extension_dir, 'proxy_auth_extension.zip')
        with zipfile.ZipFile(extension_zip, 'w') as zipf:
            zipf.write(manifest_path, 'manifest.json')
            zipf.write(background_path, 'background.js')

        self.logger.info(f"Created proxy auth extension: {extension_zip}")
        return extension_zip

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")


class BrowserManager:
    """Context manager for browser lifecycle"""

    def __init__(self, config: dict):
        self.config = config
        self.browser_setup = BrowserSetup(config)
        self.driver = None

    def __enter__(self):
        self.driver = self.browser_setup.create_driver()
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.browser_setup.close()
        return False
