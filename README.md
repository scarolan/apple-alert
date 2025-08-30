# 🍎 Apple Deal Alert

A Python web scraper that monitors Hannaford.com for apple deals and sends email alerts when prices drop below your threshold.

## 🍏 Features

- 🕷️ Scrapes Hannaford.com for apple products and prices
- 💰 Alerts when apples are priced at or below your threshold (default: $1.50/lb)
- 📧 Sends email notifications via Gmail SMTP relay
- 🍂 Seasonal mode - only runs during apple season (Aug-Oct)
- 🔄 Retry logic with exponential backoff for reliability
- 🛡️ Curl version included if Python requests fails

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd apple-alert
   ```

2. **Install dependencies:**
   ```bash
   pip install beautifulsoup4 requests
   ```

3. **Set up your SMTP password:**
   ```bash
   export SMTP_PASSWORD="your_gmail_app_password"
   ```

4. **Run the script:**
   ```bash
   # Standard version (uses Python requests)
   python3 apple-alert.py
   
   # Curl version (in case Python requests does not work)
   python3 apple-alert-curl.py
   ```

## 📁 Files

- **`apple-alert.py`** - Main script using Python requests library
- **`apple-alert-curl.py`** - Alternative version using curl
## ⚙️ Configuration

Edit the configuration section at the top of either script:

```python
MIN_PRICE_PER_LB = 1.50    # Price threshold for alerts
EMAIL_TO = "your@email.com"
EMAIL_FROM = "your@email.com"
ONLY_IN_SEASON = True      # Only run during apple season
SEASON_MONTHS = {8, 9, 10} # August, September, October
```

## 🕐 Automation with Cron

Add to your crontab to run weekly on Sundays at 8 AM:

```bash
# Edit crontab
crontab -e

# Add this line:
CRON_TZ=America/New_York
0 8 * * 0 SMTP_PASSWORD=your_password_here /path/to/apple-alert-curl.py
```

## 🔐 Security

- **Never commit passwords** - Use environment variables
- **Gmail App Passwords** - Use a dedicated app password, not your main password
- **Environment Variables** - Set `SMTP_PASSWORD` environment variable

## 🐛 Troubleshooting

### "Read timed out" errors in containers
- Use `apple-alert-curl.py` instead
- The curl version seems to work better in Docker containers and cloud environments

### No apple products found
- Website structure may have changed
- Check if Hannaford.com is accessible from your location
- Verify the search URL is still valid

### Email not sending
- Ensure `SMTP_PASSWORD` environment variable is set
- Use a Gmail App Password, not your regular password
- Check Gmail SMTP relay settings

## 🍎 Sample Output

```
🔥 Apple deal(s) at or below $1.50/lb detected:
- $0.99/lb :: Gala Apples (per lb)
- $1.29/lb :: Honeycrisp Apples (per lb)
- $1.49/lb :: Granny Smith Apples (per lb)
[info] Alert email sent to your@email.com
```

## 📧 Email Alert Example

```
Subject: 🍎 Apple Deal Alert - 3 deal(s) found!

Great news! We found some apple deals under $1.50/lb:

• $0.99/lb - Gala Apples (per lb)
• $1.29/lb - Honeycrisp Apples (per lb) 
• $1.49/lb - Granny Smith Apples (per lb)

Happy shopping!

Sent at: 2025-08-30 08:00:15
```

## 🤝 Contributing

Feel free to submit issues and pull requests! Some ideas for improvements:

- Support for additional grocery stores
- Price history tracking
- Different notification methods (Slack, Discord, etc.)
- Mobile app integration

## 📄 License

MIT License - feel free to use and modify as needed!

---

*Made with 🍎 and Python*
