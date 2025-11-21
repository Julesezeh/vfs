# Troubleshooting Guide

Common issues and solutions for the VFS Booking Bot.

## Installation Issues

### Python Version Error

**Error:** `Python 3.8 or higher required`

**Solution:**
```bash
# Check your Python version
python --version
python3 --version

# Install Python 3.8+ from python.org
# Or use pyenv:
pyenv install 3.8.0
pyenv global 3.8.0
```

### Dependency Installation Fails

**Error:** `pip install` fails with compilation errors

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-dev build-essential

# Install system dependencies (macOS)
brew install python

# Try installing requirements again
pip install -r requirements.txt
```

### Chrome Driver Issues

**Error:** `ChromeDriver version mismatch` or `selenium.common.exceptions.SessionNotCreatedException`

**Solution:**
The bot uses `undetected-chromedriver` which handles driver installation automatically. If issues persist:

```bash
# Clear Chrome driver cache
rm -rf ~/.wdm

# Update Chrome browser to latest version
# The driver will auto-download matching version
```

## Configuration Issues

### Config File Not Found

**Error:** `ERROR: Config file not found: config/config.yaml`

**Solution:**
```bash
# Copy example configuration files
cp config/config.yaml.example config/config.yaml
cp config/credentials.yaml.example config/credentials.yaml

# Edit with your details
nano config/config.yaml
nano config/credentials.yaml
```

### YAML Parsing Error

**Error:** `ERROR: Invalid YAML in config file`

**Solution:**
```yaml
# Common YAML mistakes:

# ❌ Wrong - mixing tabs and spaces
browser:
	headless: false

# ✅ Correct - use spaces only
browser:
  headless: false

# ❌ Wrong - missing quotes for special characters
password: P@ssw0rd!

# ✅ Correct - quote strings with special characters
password: "P@ssw0rd!"

# ❌ Wrong - incorrect indentation
vfs:
email: "test@example.com"

# ✅ Correct - consistent indentation (2 spaces)
vfs:
  email: "test@example.com"
```

### Configuration Validation Fails

**Error:** `Missing config section: telegram` or similar

**Solution:**
Ensure all required sections exist in `config/config.yaml`:
- vfs
- browser
- timing
- automation
- telegram
- logging

Copy from `config.yaml.example` if sections are missing.

## Telegram Issues

### No Telegram Notifications

**Problem:** Bot runs but no Telegram messages received

**Diagnosis:**
```bash
# Test Telegram separately
python3 << EOF
from src.telegram_notifier import TelegramNotifier
notifier = TelegramNotifier(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID",
    enabled=True
)
result = notifier.send_message("Test message")
print(f"Message sent: {result}")
EOF
```

**Solutions:**

1. **Wrong Bot Token**
   - Go to @BotFather on Telegram
   - Send `/mybots` → Select your bot → API Token
   - Copy the complete token (format: `123456789:ABCdefGHI...`)

2. **Wrong Chat ID**
   - Message @userinfobot on Telegram
   - Copy your ID (just the numbers, like `987654321`)
   - Or use: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

3. **Bot Not Started**
   - Search for your bot on Telegram
   - Click START button
   - Try sending test message again

4. **Telegram Disabled in Config**
   ```yaml
   telegram:
     enabled: true  # Make sure this is true
   ```

## Browser/Proxy Issues

### Proxy Connection Failed

**Error:** `ERR_PROXY_CONNECTION_FAILED` or `ERR_TUNNEL_CONNECTION_FAILED`

**Solutions:**

1. **Verify Proxy Settings**
   ```yaml
   browser:
     use_proxy: true
     proxy_host: "123.45.67.89"  # IP or hostname
     proxy_port: "8080"           # Port number
     proxy_user: "username"       # Optional
     proxy_pass: "password"       # Optional
   ```

2. **Test Proxy Manually**
   ```bash
   # Test with curl
   curl -x http://username:password@proxy:port https://google.com

   # Test with Chrome directly
   google-chrome --proxy-server="proxy:port"
   ```

3. **Disable Proxy for Testing**
   ```yaml
   browser:
     use_proxy: false
   ```

### Browser Doesn't Start

**Error:** `WebDriverException: Message: unknown error: Chrome failed to start`

**Solutions:**

1. **Check Chrome Installation**
   ```bash
   # Linux
   which google-chrome
   google-chrome --version

   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

   # Windows
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
   ```

2. **Run in Non-Headless Mode**
   ```yaml
   browser:
     headless: false  # See what's happening
   ```

3. **Check Display (Linux)**
   ```bash
   # If running on server without display
   export DISPLAY=:99
   Xvfb :99 -screen 0 1920x1080x24 &
   ```

### Browser Detected as Bot

**Problem:** Website shows CAPTCHA or blocks access

**Solutions:**

1. **Increase Delays**
   ```yaml
   timing:
     page_load_wait: [5, 10]     # Increase all delays
     element_wait: [2, 5]
     typing_delay: [0.2, 0.5]
     click_delay: [1, 3]
     form_field_delay: [3, 6]
   ```

2. **Use Different User Agent**
   ```yaml
   browser:
     user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
   ```

3. **Manual CAPTCHA Handling**
   - Run in non-headless mode
   - Let bot start
   - Solve CAPTCHA manually when it appears
   - Bot will continue automatically

## Login Issues

### Login Failed - Verification Failed

**Error:** `Login failed - verification failed`

**Solutions:**

1. **Check Credentials**
   ```yaml
   vfs_account:
     email: "correct.email@example.com"  # Double-check spelling
     password: "CorrectPassword123"      # Case-sensitive
   ```

2. **Test Manual Login**
   - Try logging in manually through browser
   - Ensure account is not locked
   - Check if email/password are correct

3. **CAPTCHA at Login**
   - VFS might require CAPTCHA
   - Run in non-headless mode: `headless: false`
   - Solve CAPTCHA manually
   - Bot will continue

4. **Two-Factor Authentication**
   - If VFS enables 2FA, bot cannot handle it automatically
   - You'll need to complete 2FA manually
   - Keep browser open for manual intervention

### Session Timeout

**Problem:** Bot logs in but session expires

**Solutions:**

1. **Reduce Check Interval**
   ```yaml
   automation:
     check_interval: 1800  # 30 minutes instead of 1 hour
   ```

2. **Handle Re-login**
   - Bot should detect login page and re-login
   - Check logs for login attempts

## Element Detection Issues

### Could Not Find Element

**Error:** `Could not find field: login_email` or similar

**Solutions:**

1. **VFS Website Changed**
   - Website structure might have changed
   - Run in non-headless mode to see the page
   - Take screenshot and inspect elements

2. **Update Field Selectors**

   Edit `src/field_mappings.py`:
   ```python
   # Find the element in browser DevTools (F12)
   # Right-click element → Copy → Copy selector
   # Add to COMMON_SELECTORS:

   'login_email': 'input[name="email"]',  # Update this
   'login_email_alt': 'input#userEmail',  # Add alternative
   ```

3. **Check Logs**
   ```bash
   tail -f logs/vfs_bot.log
   # Look for specific errors about elements
   ```

4. **Inspect Screenshots**
   ```bash
   ls -lt screenshots/
   # Open latest screenshot to see what page bot is on
   ```

### Element Not Clickable

**Error:** `ElementNotInteractableException` or `ElementClickInterceptedException`

**Solutions:**

1. **Increase Delays**
   ```yaml
   timing:
     element_wait: [2, 4]  # Wait longer before clicking
     click_delay: [1, 2]   # Wait longer before click
   ```

2. **Scroll to Element**
   - Bot should auto-scroll, but if not working:
   - Edit `src/utils.py` → `safe_click()` method
   - Add: `driver.execute_script("arguments[0].scrollIntoView();", element)`

3. **Use JavaScript Click**
   - Already implemented as fallback in `safe_click()`
   - If still failing, check element visibility

## Slot Detection Issues

### No Slots Found (Always)

**Problem:** Bot always reports "No slots available"

**Diagnosis:**

1. **Check Manually**
   - Log into VFS manually
   - Check if slots actually exist
   - If no slots exist, bot is working correctly!

2. **Run in Non-Headless Mode**
   ```yaml
   browser:
     headless: false
   ```
   - Watch what bot sees
   - Check if it's reaching the slots page

3. **Check Screenshots**
   ```bash
   ls -lt screenshots/
   ```
   - Look at `available_slots*.png`
   - Verify bot is on correct page

**Solutions:**

1. **Update Slot Selectors**

   If VFS changed slot display:
   ```python
   # In src/field_mappings.py, update:
   'available_slots': 'div.slot-container',  # Update selector
   ```

2. **Increase Check Frequency**
   ```yaml
   automation:
     check_interval: 900  # Check every 15 minutes
   ```

3. **Monitor Different Times**
   - Slots might be released at specific times
   - Try running bot at different hours
   - Check early morning or late night

## Performance Issues

### Bot Running Slowly

**Problem:** Bot takes too long between actions

**Solutions:**

1. **Reduce Delays**
   ```yaml
   timing:
     page_load_wait: [2, 4]      # Reduce from [3, 6]
     element_wait: [0.5, 2]      # Reduce from [1, 3]
     form_field_delay: [1, 2]    # Reduce from [2, 4]
   ```

2. **Use Headless Mode**
   ```yaml
   browser:
     headless: true  # Faster than rendering GUI
   ```

3. **Disable Screenshots**
   ```yaml
   automation:
     screenshot_on_error: false
     screenshot_on_success: false
   ```

### High Memory Usage

**Problem:** Bot consumes too much RAM

**Solutions:**

1. **Restart Periodically**
   ```bash
   # Use a wrapper script to restart bot every few hours
   while true; do
       python main.py --one-shot
       sleep 3600
   done
   ```

2. **Run in Headless Mode**
   ```yaml
   browser:
     headless: true
   ```

3. **Close Browser Between Checks**
   - Modify bot to close/reopen browser
   - Already implemented in continuous mode

## Booking Issues

### Form Not Filled Correctly

**Problem:** Bot fills form but data is wrong

**Solutions:**

1. **Check Credentials File**
   ```yaml
   # Ensure format matches VFS requirements:
   applicant:
     date_of_birth: "01/01/1990"  # DD/MM/YYYY format
     passport_expiry_date: "31/12/2030"  # DD/MM/YYYY
   ```

2. **Check Field Mappings**
   - Different visa types have different fields
   - Verify visa_type in config matches form

3. **Manual Review**
   ```yaml
   automation:
     auto_book: false  # Review before submission
   ```

### Booking Submission Fails

**Problem:** Bot clicks submit but booking not confirmed

**Solutions:**

1. **Payment Required**
   - VFS might require payment
   - Bot cannot handle payment automatically
   - Complete payment manually

2. **Additional Verification**
   - VFS might require additional steps
   - Run in non-headless mode
   - Complete manually when needed

3. **Check Success Verification**
   - Bot might be checking wrong indicators
   - Check logs for actual result

## Debugging Tips

### Enable Debug Logging

```yaml
logging:
  level: "DEBUG"  # Change from INFO to DEBUG
```

### View Live Logs

```bash
# Linux/Mac
tail -f logs/vfs_bot.log

# Windows
Get-Content logs\vfs_bot.log -Wait -Tail 50
```

### Take Manual Screenshots

Add to bot at any point:
```python
self.screenshot_helper.take_screenshot("debug_point_1")
```

### Test Individual Components

```python
# Test browser setup only
from src.browser_setup import BrowserSetup
config = {...}
browser = BrowserSetup(config)
driver = browser.create_driver()

# Test Telegram only
from src.telegram_notifier import TelegramNotifier
notifier = TelegramNotifier("token", "chat_id", True)
notifier.send_message("Test")
```

### Inspect Page Source

```python
# Add to bot.py where needed:
print(self.driver.page_source)
# Or save to file:
with open('page_source.html', 'w') as f:
    f.write(self.driver.page_source)
```

## Getting Help

If none of these solutions work:

1. ✅ Check all logs in `logs/vfs_bot.log`
2. ✅ Review all screenshots in `screenshots/`
3. ✅ Test components individually
4. ✅ Run in non-headless mode to observe behavior
5. ✅ Enable DEBUG logging
6. ✅ Verify VFS website hasn't changed significantly

## Common Error Messages Reference

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| `Config file not found` | Config files not created | Copy `.example` files |
| `YAML error` | Syntax error in config | Check indentation & quotes |
| `Telegram error` | Wrong token/chat ID | Verify with @BotFather |
| `Proxy connection failed` | Wrong proxy settings | Test proxy manually |
| `Chrome failed to start` | Chrome not installed | Install Chrome browser |
| `Could not find element` | Website changed | Update field selectors |
| `Login failed` | Wrong credentials | Check email/password |
| `No slots available` | No slots OR detection issue | Check manually first |
| `Element not clickable` | Timing issue | Increase delays |

---

**Still stuck? Check the README.md for more details or review the code comments in `src/` files.**
