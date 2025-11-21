# Quick Start Guide

Get up and running with the VFS Booking Bot in 5 minutes!

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Chrome browser installed
- [ ] VFS Global account (Qatar to Portugal)
- [ ] Telegram account
- [ ] Proxy server details (if needed)

## Step-by-Step Setup

### 1. Install Python Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

### 2. Setup Telegram Bot (3 minutes)

1. Open Telegram, search for **@BotFather**
2. Send: `/newbot`
3. Choose a name: `My VFS Bot`
4. Choose a username: `myvfs_123_bot`
5. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
6. **Start a chat with your bot** (click the link BotFather sends)
7. Search for **@userinfobot** and start it
8. **Copy your chat ID** (looks like: `987654321`)

### 3. Configure the Bot (5 minutes)

#### Copy configuration files:

```bash
cp config/config.yaml.example config/config.yaml
cp config/credentials.yaml.example config/credentials.yaml
```

#### Edit config/config.yaml:

Find these lines and update:

```yaml
telegram:
  enabled: true
  bot_token: "PASTE_YOUR_BOT_TOKEN_HERE"
  chat_id: "PASTE_YOUR_CHAT_ID_HERE"
```

If using proxy:

```yaml
browser:
  use_proxy: true
  proxy_host: "your.proxy.server"
  proxy_port: "8080"
```

#### Edit config/credentials.yaml:

```yaml
vfs_account:
  email: "your.vfs.email@example.com"
  password: "your_vfs_password"

applicant:
  first_name: "John"
  last_name: "Doe"
  date_of_birth: "01/01/1990"
  email: "john.doe@example.com"
  phone_country_code: "+974"
  phone_number: "12345678"
  passport_number: "A12345678"
  passport_expiry_date: "01/01/2030"
  # ... fill other fields as needed
```

### 4. Test Run

```bash
python main.py
```

You should see:
- Configuration loaded ✓
- Browser window opens
- Telegram message: "Bot started successfully" 📱

## Recommended Settings for First Run

In `config/config.yaml`:

```yaml
vfs:
  visa_type: "tourist"  # Test with tourist first

automation:
  continuous_mode: false  # Run once for testing
  auto_book: false        # Manual confirmation

browser:
  headless: false  # See what's happening
```

## What to Expect

### First Run (Testing)

1. Browser opens and navigates to VFS
2. Bot logs in with your credentials
3. Bot navigates to appointment booking
4. Bot checks for available slots
5. If slot found:
   - Telegram notification sent 📱
   - Form automatically filled
   - Bot waits for you to complete manually

### Production Run (Continuous Mode)

```yaml
automation:
  continuous_mode: true
  check_interval: 1800  # Check every 30 minutes
  auto_book: false      # Still recommend manual
```

## Troubleshooting First Run

### "Config file not found"
```bash
# Make sure you copied the example files:
ls config/
# Should show: config.yaml and credentials.yaml
```

### "Telegram notifications not working"
```bash
# Test Telegram separately:
python -c "from src.telegram_notifier import TelegramNotifier; TelegramNotifier('YOUR_TOKEN', 'YOUR_CHAT_ID', True).send_message('Test')"
```

### "Could not find email field"
- VFS website might have changed
- Run in non-headless mode to see the page
- Check if you need to handle CAPTCHA manually

### "Login failed"
- Verify credentials are correct
- Try logging in manually first
- Check if account is locked

## Running in Background

### Linux/Mac:
```bash
nohup python main.py > output.log 2>&1 &
```

### Windows:
Use Task Scheduler or run in a separate terminal

### Using screen (Linux):
```bash
screen -S vfsbot
python main.py
# Press Ctrl+A, then D to detach
# Reattach with: screen -r vfsbot
```

## Monitoring the Bot

### Check logs:
```bash
tail -f logs/vfs_bot.log
```

### Check screenshots:
```bash
ls -lt screenshots/
```

### Telegram:
You'll receive real-time updates on your phone!

## Next Steps

Once first run is successful:

1. ✅ Switch to work visa: `visa_type: "work"`
2. ✅ Enable continuous mode
3. ✅ Adjust check interval
4. ✅ Consider enabling auto_book (after testing!)
5. ✅ Run in background

## Important Notes

⚠️ **Always test with tourist visa first!**

⚠️ **Verify all fields are correct before enabling auto_book**

⚠️ **Monitor first few runs manually**

⚠️ **Keep bot token and credentials secure**

## Support

If you encounter issues:

1. Check `logs/vfs_bot.log`
2. Review `screenshots/` folder
3. Read the full README.md
4. Test each component individually

---

**Ready? Run `python main.py` and good luck! 🍀**
