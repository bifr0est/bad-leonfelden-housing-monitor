# Bad Leonfelden Housing Monitor 🏠

A Python application that monitors the [Bad Leonfelden housing website](https://www.bad-leonfelden.ooe.gv.at/Buergerservice/Bauen_Wohnen/Freie_Wohnungen) for new listings and sends instant notifications when updates are detected.

## Features ✨

- 🔄 **Automatic monitoring** - Checks for updates every 30 minutes (configurable)
- 📱 **Multiple notification methods** - Telegram, Discord, or ntfy.sh
- 🐳 **Docker support** - Easy deployment with Docker containers
- 💾 **Persistent state** - Remembers last update to avoid duplicate notifications
- 🔒 **Secure** - Runs as non-root user in container
- 📊 **Health checks** - Built-in container health monitoring

## Quick Start 🚀

### Option 1: Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bifr0est/bad-leonfelden-housing-monitor.git
   cd bad-leonfelden-housing-monitor
   ```

2. **Set up notifications** (choose one):

   **For Telegram (Recommended):**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a bot with `/newbot`
   - Get your bot token
   - Message your bot once
   - Get your chat ID from: `https://api.telegram.org/bot<TOKEN>/getUpdates`

   **For Discord:**
   - Go to Server Settings → Integrations → Webhooks
   - Create webhook and copy URL

3. **Configure docker-compose.yml:**
   ```yaml
   environment:
     - NOTIFICATION_METHOD=telegram
     - TELEGRAM_TOKEN=your_bot_token_here
     - TELEGRAM_CHAT_ID=your_chat_id_here
   ```

4. **Run:**
   ```bash
   docker-compose up -d
   ```

### Option 2: Docker Run

```bash
# Telegram
docker run -d \
  --name housing-monitor \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  -e NOTIFICATION_METHOD=telegram \
  -e TELEGRAM_TOKEN=your_token \
  -e TELEGRAM_CHAT_ID=your_chat_id \
  ghcr.io/bifr0est/bad-leonfelden-housing-monitor:latest

# Discord
docker run -d \
  --name housing-monitor \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  -e NOTIFICATION_METHOD=discord \
  -e DISCORD_WEBHOOK_URL=your_webhook_url \
  ghcr.io/bifr0est/bad-leonfelden-housing-monitor:latest
```

### Option 3: Python Script

```bash
git clone https://github.com/bifr0est/bad-leonfelden-housing-monitor.git
cd bad-leonfelden-housing-monitor
pip install -r requirements.txt
python housing_monitor.py
```

## Configuration ⚙️

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NOTIFICATION_METHOD` | Notification service (`telegram`, `discord`, `ntfy`) | `telegram` | Yes |
| `CHECK_INTERVAL` | Check interval in minutes | `30` | No |
| `TELEGRAM_TOKEN` | Telegram bot token | - | If using Telegram |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | - | If using Telegram |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL | - | If using Discord |
| `NTFY_TOPIC` | ntfy.sh topic name | - | If using ntfy |
| `NTFY_SERVER` | ntfy.sh server URL | `https://ntfy.sh` | No |

### Notification Setup Guides

<details>
<summary><b>🤖 Telegram Bot Setup</b></summary>

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the bot token (format: `123456789:ABCdef...`)
5. Message your new bot to start a conversation
6. Get your chat ID:
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Look for `"chat":{"id":12345678` in the response
   - Your chat ID is the number after `"id":`

</details>

<details>
<summary><b>💬 Discord Webhook Setup</b></summary>

1. Go to your Discord server
2. Click on Server Settings (gear icon)
3. Navigate to Integrations → Webhooks
4. Click "Create Webhook"
5. Choose a channel and name
6. Copy the webhook URL
7. Click "Save"

</details>

<details>
<summary><b>📱 ntfy.sh Setup</b></summary>

1. Choose a unique topic name (e.g., `my-housing-alerts-12345`)
2. Install the ntfy app on your phone or visit `https://ntfy.sh/your-topic`
3. Subscribe to your topic
4. Use your topic name in the `NTFY_TOPIC` environment variable

</details>

## Monitoring 📊

### Check if it's running:
```bash
docker logs housing-monitor
```

### View real-time logs:
```bash
docker logs -f housing-monitor
```

### Check container health:
```bash
docker ps  # Look for "healthy" status
```

## Development 🛠️

### Local Development

1. **Clone and setup:**
   ```bash
   git clone https://github.com/bifr0est/bad-leonfelden-housing-monitor.git
   cd bad-leonfelden-housing-monitor
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run locally:**
   ```bash
   python housing_monitor.py
   ```

### Building Docker Image

```bash
docker build -t housing-monitor .
```

## How It Works 🔍

1. **Monitoring**: The script checks the website every 30 minutes (configurable)
2. **Detection**: It extracts the "Stand: DD.MM.YYYY" timestamp from the bottom of the page
3. **Comparison**: Compares with the last known timestamp stored in a state file
4. **Notification**: If changed, sends a notification with the update details
5. **State**: Updates the stored timestamp to prevent duplicate notifications

## Notification Examples 📬

### Telegram
```
🏠 NEW HOUSING LISTINGS AVAILABLE!

The Bad Leonfelden housing page has been updated!

📅 Previous update: 20.07.2025
📅 New update: 25.07.2025

🔗 Check the listings here
```

### Discord
Rich embed with colors, timestamps, and formatting

### ntfy.sh
Simple text notification with title and tags

## Troubleshooting 🔧

### Common Issues

**Container not starting:**
```bash
docker logs housing-monitor
# Check for missing environment variables
```

**Not receiving notifications:**
```bash
# Check notification credentials
docker exec housing-monitor python -c "import os; print(os.environ)"
```

**State file issues:**
```bash
# Reset state (will trigger initial notification)
rm -rf data/housing_monitor_state.json
docker restart housing-monitor
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature-name`
6. Create a Pull Request

## License 📄

MIT License - see [LICENSE](LICENSE) file for details.

## Support 💬

- 🐛 **Issues**: [GitHub Issues](https://github.com/bifr0est/bad-leonfelden-housing-monitor/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/bifr0est/bad-leonfelden-housing-monitor/discussions)
- 📧 **Contact**: Open an issue for questions

---

**⭐ If this helps you find housing, please star the repository!**