"""
Browser setup and configuration for VFS bot
Handles Chrome driver setup with proxy and anti-detection measures
"""

import logging
import os
import json
import pickle
import zipfile
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from typing import Optional
from pathlib import Path


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
        self.cookies_file = Path("data/cookies.pkl")
        self.cookies_file.parent.mkdir(exist_ok=True)

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
        proxy_extension_path = None
        if self.config.get('use_proxy', False):
            proxy_config, proxy_extension_path = self._setup_proxy()
            if proxy_config:
                # Don't add proxy server via argument if we're using extension
                # The extension will handle both proxy and auth
                if not proxy_extension_path:
                    # No auth, just use proxy server argument
                    options.add_argument(f'--proxy-server={proxy_config}')
                    self.logger.info(f"Using proxy without auth: {proxy_config}")
                else:
                    self.logger.info(f"Using proxy with authentication: {proxy_config}")

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

            # If we have a proxy extension, we need to load it
            if proxy_extension_path:
                self.logger.info(f"Loading proxy extension: {proxy_extension_path}")
                self.driver = uc.Chrome(
                    options=options,
                    version_main=None,
                    use_subprocess=True,
                    user_data_dir=None
                )
                # Install the extension after driver creation
                try:
                    self.driver.install_addon(proxy_extension_path, temporary=True)
                    self.logger.info("Proxy authentication extension installed successfully")
                except Exception as ext_error:
                    self.logger.warning(f"Could not install extension via install_addon: {ext_error}")
                    # Try alternative method - add to options before creating driver
                    try:
                        # Close current driver and recreate with extension in options
                        self.driver.quit()
                        options.add_extension(proxy_extension_path)
                        self.driver = uc.Chrome(
                            options=options,
                            version_main=None,
                            use_subprocess=True,
                            user_data_dir=None
                        )
                        self.logger.info("Proxy extension loaded via options")
                    except Exception as e2:
                        self.logger.error(f"Failed to load proxy extension: {e2}")
            else:
                self.driver = uc.Chrome(
                    options=options,
                    version_main=None,
                    use_subprocess=True,
                    user_data_dir=None
                )

            # Apply advanced anti-detection measures
            self._apply_stealth_scripts(user_agent)

            # Set timeouts - increased for Cloudflare
            self.driver.set_page_load_timeout(120)
            self.driver.implicitly_wait(10)

            self.logger.info("Browser initialized successfully with stealth mode")
            return self.driver

        except Exception as e:
            self.logger.error(f"Error creating browser: {e}")
            raise

    def _apply_stealth_scripts(self, user_agent: str):
        """
        Apply comprehensive stealth JavaScript to avoid detection

        Args:
            user_agent: User agent string to use
        """
        try:
            # Override user agent via CDP
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent,
                "platform": "Win32",
                "acceptLanguage": "en-US,en;q=0.9"
            })

            # Comprehensive stealth script
            stealth_js = """
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        },
                        {
                            0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            length: 1,
                            name: "Chrome PDF Viewer"
                        },
                        {
                            0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                            1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"},
                            description: "",
                            filename: "internal-nacl-plugin",
                            length: 2,
                            name: "Native Client"
                        }
                    ]
                });

                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });

                // Mock platform
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });

                // Mock hardware concurrency (CPU cores)
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });

                // Mock device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });

                // Mock vendor
                Object.defineProperty(navigator, 'vendor', {
                    get: () => 'Google Inc.'
                });

                // Chrome runtime
                window.chrome = {
                    runtime: {}
                };

                // Override toString for functions to hide modifications
                const originalToString = Function.prototype.toString;
                Function.prototype.toString = function() {
                    if (this === window.navigator.permissions.query) {
                        return 'function query() { [native code] }';
                    }
                    return originalToString.call(this);
                };

                // WebGL vendor override
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.call(this, parameter);
                };

                // Battery API
                if ('getBattery' in navigator) {
                    navigator.getBattery = () => Promise.resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 1,
                        addEventListener: () => {},
                        removeEventListener: () => {},
                        dispatchEvent: () => true
                    });
                }

                // Connection API - simulate real network
                if ('connection' in navigator) {
                    Object.defineProperty(navigator, 'connection', {
                        get: () => ({
                            effectiveType: '4g',
                            rtt: 50,
                            downlink: 10,
                            saveData: false
                        })
                    });
                }

                // Screen properties for consistency
                Object.defineProperty(screen, 'availWidth', {
                    get: () => window.screen.width
                });
                Object.defineProperty(screen, 'availHeight', {
                    get: () => window.screen.height
                });

                // Notification permission
                Object.defineProperty(Notification, 'permission', {
                    get: () => 'default'
                });
            """

            self.driver.execute_script(stealth_js)
            self.logger.debug("Stealth scripts applied successfully")

        except Exception as e:
            self.logger.warning(f"Error applying stealth scripts: {e}")

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

        # Proxy string for Chrome argument
        proxy_scheme = self.config.get('proxy_scheme', 'http')
        proxy_str = f"{proxy_scheme}://{host}:{port}"

        # Create auth extension if username and password provided
        if user and password:
            self.logger.info(f"Setting up proxy with authentication for {host}:{port}")
            extension_path = self._create_proxy_auth_extension(host, port, user, password)
            return proxy_str, extension_path
        else:
            self.logger.warning("Proxy configured without authentication credentials")
            self.logger.warning("If your proxy requires auth, add proxy_user and proxy_pass to config.yaml")
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

        # Determine proxy scheme - try to auto-detect from config or use http as default
        proxy_scheme = self.config.get('proxy_scheme', 'http')

        # Background script for proxy authentication
        # Using both http and https to handle all connections
        background_js = """
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "%s",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost", "127.0.0.1"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {
    console.log('Proxy configured:', config);
});

function callbackFn(details) {
    console.log('Proxy auth request for:', details.url);
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

console.log('Proxy auth extension loaded');
""" % (proxy_scheme, host, port, user, password)

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

    def save_cookies(self, domain: Optional[str] = None):
        """
        Save browser cookies to file for session persistence

        Args:
            domain: Optional domain filter for cookies
        """
        try:
            if not self.driver:
                return

            cookies = self.driver.get_cookies()

            # Filter by domain if specified
            if domain:
                cookies = [c for c in cookies if domain in c.get('domain', '')]

            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)

            self.logger.info(f"Saved {len(cookies)} cookies to {self.cookies_file}")

        except Exception as e:
            self.logger.error(f"Error saving cookies: {e}")

    def load_cookies(self, url: str):
        """
        Load cookies from file and add to current session

        Args:
            url: URL to navigate to before loading cookies (required for domain)
        """
        try:
            if not self.cookies_file.exists():
                self.logger.debug("No saved cookies found")
                return False

            # Navigate to the domain first (required to set cookies)
            self.driver.get(url)

            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)

            # Add each cookie
            for cookie in cookies:
                try:
                    # Remove expiry if it's in the past
                    if 'expiry' in cookie:
                        import time
                        if cookie['expiry'] < time.time():
                            continue

                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.debug(f"Could not add cookie {cookie.get('name')}: {e}")

            self.logger.info(f"Loaded {len(cookies)} cookies from {self.cookies_file}")

            # Refresh page to apply cookies
            self.driver.refresh()

            return True

        except Exception as e:
            self.logger.error(f"Error loading cookies: {e}")
            return False

    def close(self):
        """Close the browser and save cookies"""
        if self.driver:
            try:
                # Save cookies before closing
                self.save_cookies()
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
