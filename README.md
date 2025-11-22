# VFS Appointment Booking Bot

An intelligent automation bot for booking VFS Global visa appointments (Qatar to Portugal). Built with Python and Selenium, featuring anti-detection measures, Telegram notifications, and proxy support.

## Features

- ✅ **Automated Login** - Securely logs into your VFS account
- 🔍 **Slot Detection** - Continuously monitors for available appointment slots
- 📝 **Auto Form Filling** - Automatically fills application forms with your details
- 📱 **Telegram Notifications** - Real-time updates on slot availability and booking status
- 🔒 **Proxy Support** - Works with your existing proxy configuration
- 🤖 **Anti-Detection** - Human-like behavior with random delays and undetected Chrome
- 🔄 **Continuous Monitoring** - Keeps checking until a slot is found
- 📸 **Screenshot Capture** - Takes screenshots at key moments for verification
- 📊 **Detailed Logging** - Comprehensive logs for debugging
- ⚙️ **Highly Configurable** - Customize timing, behavior, and preferences

## Requirements

- Python 3.8 or higher
- Chrome browser installed
- VFS Global account (Qatar to Portugal)
- Telegram bot (for notifications)
- Proxy server (if accessing from restricted locations)

## Installation

### 1. Clone or Download This Repository

```bash
cd /path/to/vfs-booking-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure the Bot

#### A. Create Configuration Files

Copy the example configuration files:

```bash
cp config/config.yaml.example config/config.yaml
cp config/credentials.yaml.example config/credentials.yaml
```

#### B. Setup Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions to create a new bot
3. Copy the bot token provided
4. Start a chat with your new bot
5. Get your chat ID:
   - Search for [@userinfobot](https://t.me/userinfobot) on Telegram
   - Start the bot and it will show your chat ID

#### C. Edit config.yaml

Open `config/config.yaml` and update:

```yaml
# Telegram Configuration
telegram:
  enabled: true
  bot_token: "YOUR_BOT_TOKEN_HERE"  # From BotFather
  chat_id: "YOUR_CHAT_ID_HERE"      # From userinfobot

# Proxy Configuration (if using)
browser:
  use_proxy: true
  proxy_host: "your.proxy.server"    # Your proxy server
  proxy_port: "8080"                 # Your proxy port
  proxy_user: "username"             # Optional
  proxy_pass: "password"             # Optional

# Automation Settings
automation:
  auto_book: false  # Set to true ONLY if you want automatic booking
  continuous_mode: true
  check_interval: 3600  # Check every hour
```

#### D. Edit credentials.yaml

Open `config/credentials.yaml` and fill in your details:

```yaml
# VFS Account
vfs_account:
  email: "your.email@example.com"
  password: "your_password"

# Applicant Information
applicant:
  first_name: "John"
  last_name: "Doe"
  date_of_birth: "01/01/1990"
  # ... fill in all other required fields
```

**⚠️ IMPORTANT:** Make sure all fields match EXACTLY as they appear on the VFS website.

## Usage

### Basic Usage

```bash
python main.py
```

### Advanced Usage

```bash
# Run in headless mode (no browser window)
python main.py --headless

# Disable Telegram notifications
python main.py --no-telegram

# Run once and exit (no continuous monitoring)
python main.py --one-shot

# Use custom configuration file
python main.py --config my_config.yaml --credentials my_creds.yaml
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--config <file>` | Specify custom config file |
| `--credentials <file>` | Specify custom credentials file |
| `--headless` | Run browser in headless mode |
| `--no-telegram` | Disable Telegram notifications |
| `--one-shot` | Run once and exit |

## Configuration Guide

### Timing Configuration

The bot uses random delays to appear human-like. Adjust these in `config.yaml`:

```yaml
timing:
  page_load_wait: [3, 6]      # Wait 3-6 seconds after page loads
  element_wait: [1, 3]        # Wait 1-3 seconds before interacting
  typing_delay: [0.1, 0.3]    # Delay between keystrokes
  click_delay: [0.5, 1.5]     # Delay before clicking
  form_field_delay: [2, 4]    # Delay between form fields
  navigation_delay: [3, 5]    # Delay after navigation
```

**Recommendations:**
- **Conservative (Safe):** Increase all delays by 50%
- **Aggressive (Fast):** Decrease delays, but risk detection
- **Default:** Good balance between speed and safety

### Automation Modes

#### Continuous Monitoring Mode (Recommended)

```yaml
automation:
  continuous_mode: true
  check_interval: 3600  # Check every hour (3600 seconds)
  auto_book: false      # Manual booking confirmation
```

The bot will:
1. Check for slots every hour
2. When a slot is found, it fills the form
3. Waits for you to manually confirm and complete payment

#### Fully Automatic Mode (Use with Caution)

```yaml
automation:
  continuous_mode: true
  check_interval: 3600
  auto_book: true  # Automatic booking
```

⚠️ **WARNING:** This will automatically complete the booking when a slot is found. Use only if you're confident in your configuration.

### Visa Type Configuration

For **Tourist Visa** (testing):
```yaml
vfs:
  visa_type: "tourist"
```

For **Work Visa** (production):
```yaml
vfs:
  visa_type: "work"
```

The bot will automatically request different fields based on visa type.

## How It Works

1. **Login:** Bot logs into your VFS account using credentials
2. **Navigate:** Navigates to appointment booking section
3. **Monitor:** Checks for available slots at configured intervals
4. **Notify:** Sends Telegram notification when slot found
5. **Fill Form:** Automatically fills application form with your details
6. **Book:** Either auto-books or waits for manual confirmation
7. **Confirm:** Takes screenshots and sends confirmation via Telegram

## Telegram Notifications

You'll receive notifications for:

- ✅ Bot started successfully
- 🎉 Appointment slot found (with screenshot)
- ✅ Booking successful (with reference number)
- ❌ Errors (with error details and screenshot)
- 🔄 Retry attempts
- ℹ️ No slots available

## Screenshots

The bot automatically captures screenshots at:

- Login page
- Available slots
- Filled forms
- Booking confirmation
- Errors

Screenshots are saved in the `screenshots/` directory.

## Logs

Detailed logs are saved to `logs/vfs_bot.log`. Check this file for:

- Debugging issues
- Tracking bot behavior
- Understanding what went wrong

## Troubleshooting

### Bot Can't Find Elements

**Problem:** Bot logs show "Could not find element: ..."

**Solutions:**
1. VFS website structure may have changed
2. Check `src/field_mappings.py` and update selectors
3. Run in non-headless mode to see what's happening
4. Take manual screenshots and compare

### Login Fails

**Problem:** Login verification fails

**Solutions:**
1. Double-check credentials in `credentials.yaml`
2. Try logging in manually first to ensure account is active
3. Check if VFS requires CAPTCHA (bot can't handle CAPTCHAs)
4. Verify proxy settings if using proxy

### Cloudflare Challenge Issues

**Problem:** Bot stuck on "Checking your browser" or Cloudflare challenge

**Solutions:**
1. **Wait longer** - Cloudflare challenges can take 1-2 minutes to resolve automatically
2. **Check timeout setting** - Increase `cloudflare.max_wait` in `config.yaml` (default: 120 seconds)
3. **Use session persistence** - The bot now saves cookies after successful bypass for faster subsequent runs
4. **Run in non-headless mode** - This helps the bot appear more like a real browser
5. **Check proxy configuration** - Some proxies may trigger more aggressive Cloudflare challenges
6. **Review logs** - Check `logs/vfs_bot.log` for detailed Cloudflare challenge information
7. **Look for timeout screenshot** - Check `/tmp/cloudflare_timeout.png` if bypass times out

**Enhanced Cloudflare Features:**
- Detects different challenge types (Turnstile, JavaScript challenge, Managed challenge)
- Automatically extends timeout for complex Turnstile challenges (up to 150s)
- Simulates human-like mouse movements during wait
- Saves successful session cookies for faster future runs
- Progressive checking (checks more frequently in first 30 seconds)

### Proxy Issues

**Problem:** Bot can't connect through proxy

**Solutions:**
1. Verify proxy host and port are correct
2. Check if proxy requires authentication
3. Ensure `proxy_scheme` is set correctly ("http" or "https") in `config.yaml`
4. Test proxy with browser first
5. Try without proxy to isolate issue

### No Slots Found

**Problem:** Bot keeps reporting "No slots available"

**Solutions:**
1. This might be accurate - slots are limited!
2. Increase check frequency (reduce `check_interval`)
3. Run during off-peak hours
4. Monitor manually to verify slots exist

### Telegram Not Working

**Problem:** No Telegram notifications received

**Solutions:**
1. Verify bot token is correct
2. Verify chat ID is correct
3. Make sure you've started a chat with your bot
4. Check Telegram is enabled in config
5. Test with: `python -c "from src.telegram_notifier import TelegramNotifier; t = TelegramNotifier('TOKEN', 'CHAT_ID'); t.send_message('Test')"`

## Security Notes

- ✅ Never commit `config/config.yaml` or `config/credentials.yaml` to git
- ✅ Keep your VFS password secure
- ✅ Keep your Telegram bot token private
- ✅ Review `auto_book` setting carefully
- ✅ Use environment variables for sensitive data in production

## Important Warnings

⚠️ **Use Responsibly:**
- This bot is for personal use only
- Don't abuse VFS systems with excessive requests
- Respect rate limits and timing configurations
- Be aware that automation may violate VFS terms of service

⚠️ **No Guarantees:**
- Slot availability depends on VFS systems
- Website changes may break the bot
- Success is not guaranteed

⚠️ **Testing:**
- Always test with tourist visa first
- Verify all fields are correct before enabling `auto_book`
- Monitor the first few runs manually

## Field Mapping for Work Visa

When configuring for work visa, ensure these fields are filled in `credentials.yaml`:

```yaml
applicant:
  # Personal (Required)
  first_name: "Your First Name"
  middle_name: "Middle Name (if any)"
  last_name: "Your Last Name"
  date_of_birth: "DD/MM/YYYY"
  gender: "Male/Female"
  marital_status: "Single/Married/Divorced/Widowed"

  # Passport (Required)
  passport_number: "A12345678"
  passport_issue_date: "DD/MM/YYYY"
  passport_expiry_date: "DD/MM/YYYY"
  passport_issue_place: "Doha, Qatar"
  nationality: "Your Nationality"

  # Contact (Required)
  email: "your.email@example.com"
  phone_country_code: "+974"
  phone_number: "12345678"

  # Address (Required)
  address_line1: "Building 123, Street 45"
  city: "Doha"
  country: "Qatar"

  # Employment (Required for Work Visa)
  occupation: "Software Engineer"
  employer_name: "Your Company Ltd"
  employer_address: "Company Address"
  employer_phone: "+97412345678"

  # Travel (Required)
  intended_travel_date: "DD/MM/YYYY"
  intended_stay_duration: "90"

  # Portugal Contact (Required)
  portugal_contact_name: "Company/Hotel Name"
  portugal_contact_address: "Address in Portugal"
  portugal_contact_phone: "+351123456789"
```

## Project Structure

```
vfs-booking-bot/
├── config/
│   ├── config.yaml.example      # Example configuration
│   └── credentials.yaml.example # Example credentials
├── src/
│   ├── __init__.py
│   ├── bot.py                   # Main bot logic
│   ├── browser_setup.py         # Browser configuration
│   ├── telegram_notifier.py     # Telegram integration
│   ├── utils.py                 # Utility functions
│   └── field_mappings.py        # Form field mappings
├── logs/                        # Log files (auto-created)
├── screenshots/                 # Screenshots (auto-created)
├── requirements.txt             # Python dependencies
├── main.py                      # Entry point
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## Customization

### Adding Custom Delays

Edit `config.yaml` timing section to adjust delays.

### Changing Slot Selection Logic

Edit `src/bot.py`, method `select_best_slot()` to implement custom logic (e.g., prefer morning slots).

### Adding New Fields

1. Add field to `src/field_mappings.py`
2. Add value to `config/credentials.yaml`
3. Add to visa type requirements in `field_mappings.py`

## FAQ

**Q: Is this legal?**
A: This is automation for personal use. However, it may violate VFS terms of service. Use at your own risk.

**Q: Will this guarantee me an appointment?**
A: No. It only automates the booking process when slots become available.

**Q: Can I run multiple instances?**
A: Yes, but be careful not to overload VFS servers. Use different accounts.

**Q: Does it work for other countries?**
A: It's designed for Qatar→Portugal but can be adapted by changing URLs and field mappings.

**Q: What if the website changes?**
A: You'll need to update field selectors in `src/field_mappings.py`.

**Q: Can I contribute?**
A: Yes! Feel free to improve the code and submit updates.

## Support

For issues, questions, or improvements:

1. Check logs in `logs/vfs_bot.log`
2. Review screenshots in `screenshots/`
3. Check configuration files for errors
4. Test components individually

## License

This project is provided as-is for educational and personal use only. Use at your own risk.

## Disclaimer

This bot is not affiliated with, endorsed by, or connected to VFS Global or any government entity. The developers are not responsible for any consequences of using this software.

---

**Good luck with your visa application! 🇵🇹**
