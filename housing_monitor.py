#!/usr/bin/env python3
"""
Bad Leonfelden Housing Monitor
Monitors the housing website for updates and sends notifications via ntfy.sh
"""

import requests
import re
import time
import json
import os
from datetime import datetime
from typing import Optional

class HousingMonitor:
    def __init__(self, notification_method: str = None, **kwargs):
        """
        Initialize the housing monitor
        
        Args:
            notification_method: 'telegram', 'discord', or 'ntfy'
            **kwargs: Notification service credentials
                For Telegram: telegram_token, telegram_chat_id
                For Discord: discord_webhook_url
                For ntfy: ntfy_topic, ntfy_server (optional)
        """
        self.url = "https://www.bad-leonfelden.ooe.gv.at/Buergerservice/Bauen_Wohnen/Freie_Wohnungen"
        
        # Use environment variables if available, otherwise use kwargs
        self.notification_method = notification_method or os.getenv('NOTIFICATION_METHOD', 'telegram')
        self.state_file = os.getenv('STATE_FILE', kwargs.get('state_file', 'housing_monitor_state.json'))

        # Initialize all notification attributes
        self.telegram_token: Optional[str] = None
        self.telegram_chat_id: Optional[str] = None
        self.discord_webhook_url: Optional[str] = None
        self.ntfy_topic: Optional[str] = None
        self.ntfy_server: Optional[str] = None

        # Set up notification method
        if self.notification_method == "telegram":
            self.telegram_token = kwargs.get('telegram_token') or os.getenv('TELEGRAM_TOKEN')
            self.telegram_chat_id = kwargs.get('telegram_chat_id') or os.getenv('TELEGRAM_CHAT_ID')
            if not self.telegram_token or not self.telegram_chat_id:
                raise ValueError("Telegram requires: TELEGRAM_TOKEN and TELEGRAM_CHAT_ID environment variables")
        
        elif self.notification_method == "discord":
            self.discord_webhook_url = kwargs.get('discord_webhook_url') or os.getenv('DISCORD_WEBHOOK_URL')
            if not self.discord_webhook_url:
                raise ValueError("Discord requires: DISCORD_WEBHOOK_URL environment variable")
        
        elif self.notification_method == "ntfy":
            self.ntfy_topic = kwargs.get('ntfy_topic') or os.getenv('NTFY_TOPIC')
            self.ntfy_server = kwargs.get('ntfy_server') or os.getenv('NTFY_SERVER', "https://ntfy.sh")
            if not self.ntfy_topic:
                raise ValueError("ntfy requires: NTFY_TOPIC environment variable")
        
        # Load previous state
        self.last_known_date = self.load_state()
        
    def load_state(self) -> Optional[str]:
        """Load the last known update date from state file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return data.get('last_update_date')
        except Exception as e:
            print(f"Error loading state: {e}")
        return None
    
    def save_state(self, update_date: str):
        """Save the current update date to state file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_update_date': update_date,
                    'last_check': datetime.now().isoformat()
                }, f)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def fetch_page(self) -> Optional[str]:
        """Fetch the housing page content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_update_date(self, content: str) -> Optional[str]:
        """Extract the 'Stand:' date from the page content"""
        # Look for "Stand: DD.MM.YYYY" pattern
        pattern = r'Stand:\s*(\d{2}\.\d{2}\.\d{4})'
        match = re.search(pattern, content)
        
        if match:
            return match.group(1)
        return None
    
    def send_telegram_notification(self, message: str):
        """Send notification via Telegram Bot"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            response = requests.post(url, data=data)
            response.raise_for_status()
            print("Telegram notification sent successfully")
        except requests.RequestException as e:
            print(f"Error sending Telegram notification: {e}")
    
    def send_discord_notification(self, message: str, title: str = "Housing Update"):
        """Send notification via Discord Webhook"""
        if not self.discord_webhook_url:
            print("Discord webhook URL not configured, skipping Discord notification")
            return

        try:
            data = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 0x00ff00,  # Green color
                    "timestamp": datetime.now().isoformat(),
                    "footer": {"text": "Bad Leonfelden Housing Monitor"}
                }]
            }
            assert self.discord_webhook_url is not None  # Type checker hint
            response = requests.post(self.discord_webhook_url, json=data)
            response.raise_for_status()
            print("Discord notification sent successfully")
        except requests.RequestException as e:
            print(f"Error sending Discord notification: {e}")
    
    def send_email_notification(self, message: str, title: str = "Housing Update"):
        """Send notification via email (using a service like SendGrid, Mailgun, etc.)"""
        # This is a placeholder - you'd need to configure with your email service
        print(f"Email notification: {title} - {message}")
    
    def send_notification(self, message: str, title: str = "Housing Update"):
        """Send notification via configured method"""
        if hasattr(self, 'telegram_token') and hasattr(self, 'telegram_chat_id'):
            self.send_telegram_notification(message)
        elif hasattr(self, 'discord_webhook_url'):
            self.send_discord_notification(message, title)
        else:
            # Fallback to ntfy.sh
            try:
                response = requests.post(
                    f"{self.ntfy_server}/{self.ntfy_topic}",
                    data=message.encode('utf-8'),
                    headers={
                        "Title": title,
                        "Priority": "default",
                        "Tags": "house,announcement"
                    }
                )
                response.raise_for_status()
                print("ntfy notification sent successfully")
            except requests.RequestException as e:
                print(f"Error sending notification: {e}")
    
    def check_for_updates(self) -> bool:
        """Check for updates and send notification if found"""
        print(f"Checking for updates at {datetime.now()}")
        
        # Fetch page content
        content = self.fetch_page()
        if not content:
            print("Failed to fetch page content")
            return False
        
        # Extract current update date
        current_date = self.extract_update_date(content)
        if not current_date:
            print("Could not find update date on page")
            return False
        
        print(f"Current update date: {current_date}")
        print(f"Last known date: {self.last_known_date}")
        
        # Check if there's an update
        if self.last_known_date is None:
            # First run - just save the current date
            self.save_state(current_date)
            self.last_known_date = current_date
            print("Initial run - saved current state")
            
            # Send initial notification
            self.send_notification(
                f"🏠 Housing Monitor Started!\n\nNow monitoring Bad Leonfelden housing updates.\nCurrent update date: {current_date}\n\nYou'll be notified when new listings are posted!",
                "Housing Monitor Active"
            )
            return True
        
        elif current_date != self.last_known_date:
            # Update detected!
            message = f"🏠 <b>NEW HOUSING LISTINGS AVAILABLE!</b>\n\nThe Bad Leonfelden housing page has been updated!\n\n📅 Previous update: {self.last_known_date}\n📅 New update: {current_date}\n\n🔗 <a href='{self.url}'> Check the listings here</a>"
            
            self.send_notification(message, "New Housing Listings!")
            
            # Update our stored state
            self.save_state(current_date)
            self.last_known_date = current_date
            print("Update detected and notification sent!")
            return True
        
        else:
            print("No updates found")
            return False
    
    def run_continuous(self, check_interval_minutes: int = None):
        """Run the monitor continuously"""
        if check_interval_minutes is None:
            check_interval_minutes = int(os.getenv('CHECK_INTERVAL', 30))
            
        print(f"Starting continuous monitoring (checking every {check_interval_minutes} minutes)")
        print(f"Monitoring URL: {self.url}")
        print(f"Notification method: {self.notification_method}")
        
        while True:
            try:
                self.check_for_updates()
                print(f"Sleeping for {check_interval_minutes} minutes...")
                time.sleep(check_interval_minutes * 60)
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                print("Continuing monitoring...")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function to run the housing monitor"""
    import sys
    
    # Check if running in container mode (environment variables set)
    if os.getenv('NOTIFICATION_METHOD'):
        print("=== Bad Leonfelden Housing Monitor (Container Mode) ===")
        try:
            monitor = HousingMonitor()
            print(f"Notification method: {monitor.notification_method}")
            print(f"Monitoring: {monitor.url}")
            print("Container is running...")
            print()
            
            # Run once immediately, then start continuous monitoring
            monitor.check_for_updates()
            monitor.run_continuous()
        except ValueError as e:
            print(f"Configuration error: {e}")
            print("Please check your environment variables.")
            sys.exit(1)
    else:
        # Interactive mode for local development
        print("=== Bad Leonfelden Housing Monitor ===")
        print("Choose notification method:")
        print("1. Telegram Bot (Recommended)")
        print("2. Discord Webhook") 
        print("3. ntfy.sh")
        print()
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            # Telegram setup
            print("\nTelegram Bot Setup:")
            print("1. Message @BotFather on Telegram")
            print("2. Create bot with /newbot")
            print("3. Get your bot token")
            print("4. Message your bot, then visit: https://api.telegram.org/bot<TOKEN>/getUpdates")
            print("5. Find your chat_id in the response")
            print()
            
            token = input("Enter bot token: ").strip()
            chat_id = input("Enter your chat ID: ").strip()
            
            monitor = HousingMonitor("telegram", telegram_token=token, telegram_chat_id=chat_id)
            
        elif choice == "2":
            # Discord setup
            print("\nDiscord Webhook Setup:")
            print("1. Go to your Discord server")
            print("2. Server Settings → Integrations → Webhooks")
            print("3. Create webhook and copy URL")
            print()
            
            webhook_url = input("Enter Discord webhook URL: ").strip()
            monitor = HousingMonitor("discord", discord_webhook_url=webhook_url)
            
        elif choice == "3":
            # ntfy.sh setup
            topic = input("Enter ntfy.sh topic name: ").strip()
            monitor = HousingMonitor("ntfy", ntfy_topic=topic)
            
        else:
            print("Invalid choice!")
            sys.exit(1)
        
        print(f"\nMonitoring: {monitor.url}")
        print("Press Ctrl+C to stop")
        print()
        
        # Run once immediately, then start continuous monitoring
        monitor.check_for_updates()
        monitor.run_continuous(check_interval_minutes=30)

if __name__ == "__main__":
    main()