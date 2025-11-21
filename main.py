#!/usr/bin/env python3
"""
VFS Appointment Booking Bot - Main Entry Point
Automated appointment booking for VFS Global visa applications
"""

import os
import sys
import yaml
import argparse
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot import VFSBookingBot
from src.utils import setup_logging


def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Config file not found: {config_path}")
        print("Please copy config/config.yaml.example to config/config.yaml and fill in your details")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in config file: {e}")
        sys.exit(1)


def load_credentials(credentials_path: str) -> dict:
    """
    Load credentials from YAML file

    Args:
        credentials_path: Path to credentials file

    Returns:
        Credentials dictionary
    """
    try:
        with open(credentials_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Credentials file not found: {credentials_path}")
        print("Please copy config/credentials.yaml.example to config/credentials.yaml and fill in your details")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in credentials file: {e}")
        sys.exit(1)


def validate_config(config: dict, credentials: dict) -> bool:
    """
    Validate configuration and credentials

    Args:
        config: Configuration dictionary
        credentials: Credentials dictionary

    Returns:
        True if valid, False otherwise
    """
    errors = []

    # Check required config sections
    required_sections = ['vfs', 'browser', 'timing', 'automation', 'telegram', 'logging']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing config section: {section}")

    # Check VFS credentials
    if 'vfs_account' not in credentials:
        errors.append("Missing vfs_account in credentials")
    else:
        if not credentials['vfs_account'].get('email'):
            errors.append("VFS email not configured")
        if not credentials['vfs_account'].get('password'):
            errors.append("VFS password not configured")

    # Check applicant data
    if 'applicant' not in credentials:
        errors.append("Missing applicant information in credentials")

    # Check Telegram config if enabled
    if config.get('telegram', {}).get('enabled', False):
        telegram_config = config['telegram']
        if not telegram_config.get('bot_token') or telegram_config['bot_token'] == 'YOUR_BOT_TOKEN_HERE':
            errors.append("Telegram bot_token not configured")
        if not telegram_config.get('chat_id') or telegram_config['chat_id'] == 'YOUR_CHAT_ID_HERE':
            errors.append("Telegram chat_id not configured")

    # Check proxy config if enabled
    if config.get('browser', {}).get('use_proxy', False):
        browser_config = config['browser']
        if not browser_config.get('proxy_host'):
            errors.append("Proxy enabled but proxy_host not configured")
        if not browser_config.get('proxy_port'):
            errors.append("Proxy enabled but proxy_port not configured")

    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the errors in your config files before running the bot.\n")
        return False

    return True


def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          VFS Appointment Booking Bot v1.0                   ║
║          Qatar to Portugal Visa Automation                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_summary(config: dict, credentials: dict):
    """Print configuration summary"""
    print("\n📋 Configuration Summary:")
    print(f"  VFS Account: {credentials['vfs_account']['email']}")
    print(f"  Visa Type: {config['vfs']['visa_type'].upper()}")
    print(f"  Route: {config['vfs']['country_from'].upper()} → {config['vfs']['country_to'].upper()}")
    print(f"  Center: {config['vfs']['appointment_center']}")
    print(f"  Applicant: {credentials['applicant'].get('first_name', 'N/A')} {credentials['applicant'].get('last_name', 'N/A')}")
    print(f"  Proxy Enabled: {'Yes' if config['browser'].get('use_proxy') else 'No'}")
    print(f"  Telegram Notifications: {'Enabled' if config['telegram']['enabled'] else 'Disabled'}")
    print(f"  Continuous Mode: {'Yes' if config['automation']['continuous_mode'] else 'No'}")
    if config['automation']['continuous_mode']:
        interval = config['automation']['check_interval']
        print(f"  Check Interval: {interval}s ({interval // 60} minutes)")
    print(f"  Auto-Book: {'Yes' if config['automation'].get('auto_book') else 'No (Manual)'}")
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='VFS Appointment Booking Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Run with default config
  python main.py --config custom_config.yaml        # Use custom config
  python main.py --no-telegram                      # Disable Telegram notifications
  python main.py --headless                         # Run in headless mode

For more information, see README.md
        """
    )

    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    parser.add_argument(
        '--credentials',
        default='config/credentials.yaml',
        help='Path to credentials file (default: config/credentials.yaml)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (override config)'
    )
    parser.add_argument(
        '--no-telegram',
        action='store_true',
        help='Disable Telegram notifications (override config)'
    )
    parser.add_argument(
        '--one-shot',
        action='store_true',
        help='Run once and exit (disable continuous mode)'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Load configuration
    print("Loading configuration...")
    config = load_config(args.config)
    credentials = load_credentials(args.credentials)

    # Apply command-line overrides
    if args.headless:
        config['browser']['headless'] = True
        print("  ✓ Headless mode enabled")

    if args.no_telegram:
        config['telegram']['enabled'] = False
        print("  ✓ Telegram notifications disabled")

    if args.one_shot:
        config['automation']['continuous_mode'] = False
        print("  ✓ One-shot mode enabled")

    # Validate configuration
    if not validate_config(config, credentials):
        sys.exit(1)

    print("  ✓ Configuration loaded and validated\n")

    # Setup logging
    logger = setup_logging(config['logging'])

    # Print summary
    print_summary(config, credentials)

    # Confirmation prompt
    if not config['automation'].get('auto_book', False):
        print("⚠️  AUTO-BOOK is DISABLED - You will need to complete the booking manually")

    try:
        response = input("Ready to start? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cancelled by user")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(0)

    print("\n" + "="*60)
    print("🚀 Starting VFS Booking Bot...")
    print("="*60 + "\n")

    # Create and start bot
    try:
        bot = VFSBookingBot(config, credentials)
        bot.start()
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user")
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    print("\n" + "="*60)
    print("Bot execution completed")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
