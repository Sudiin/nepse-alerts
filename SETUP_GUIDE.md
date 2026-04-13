# NEPSE Stock Alert Agent - Setup Guide

> 100% free. Runs automatically. Multi-channel alerts (Telegram, Gmail, Discord).

---

## Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `nepse-alerts`
3. Make it **Public** (required for free Actions)
4. Click **Create repository**

---

## Step 2: Upload Code Files

### Add Python script:
```bash
# Copy nepse_alert_agent.py to your repo root
```

### Add GitHub Actions workflow:
```bash
# Create folder structure:
mkdir -p .github/workflows

# Copy the workflow file:
# .github/workflows/nepse_alerts.yml
```

File structure should look like:
```
nepse-alerts/
  ├── .github/
  │   └── workflows/
  │       └── nepse_alerts.yml
  ├── nepse_alert_agent.py
  ├── alert_state.json
  └── README.md
```

---

## Step 3: Set Up Telegram Bot (Recommended - Easiest)

### A. Create Telegram Bot:
1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Follow prompts:
   - Name: `NEPSE Alert Bot`
   - Username: `nepse_alert_yourname_bot` (must be unique)
4. Copy the **API Token** (looks like: `123456789:ABCDEFGHIJKLMNOPQRSTUVWxyz`)

### B. Get Your Chat ID:
1. Start a DM with your bot (click the link it gives you)
2. Send any message
3. Go to `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Replace `<YOUR_TOKEN>` with your token from step A
4. Find the `"chat":{"id":` number - that's your **Chat ID**

### C. Add to GitHub Secrets:
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add:
   - `TELEGRAM_BOT_TOKEN` = your token
   - `TELEGRAM_CHAT_ID` = your chat ID

---

## Step 4: Set Up Gmail (Optional)

### A. Enable Gmail API:
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and **Windows Computer** (or your device)
3. Google generates a 16-char password - copy it

### B. Add to GitHub Secrets:
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add:
   - `GMAIL_SENDER` = your email (e.g., `you@gmail.com`)
   - `GMAIL_APP_PASSWORD` = the 16-char password from step A
   - `GMAIL_RECIPIENT` = where to send alerts (can be same email)

---

## Step 5: Set Up Discord (Optional)

### A. Create Webhook:
1. In your Discord server, right-click a channel → **Edit Channel**
2. Go to **Integrations** → **Webhooks**
3. Click **New Webhook** → **Copy Webhook URL**

### B. Add to GitHub Secrets:
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add:
   - `DISCORD_WEBHOOK_URL` = the URL from step A

---

## Step 6: Set Up Google Sheet (Watchlist)

### A. Create Google Sheet:
1. Go to [sheets.google.com](https://sheets.google.com)
2. Create new sheet, name it "NEPSE Watchlist"
3. Copy the Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`

### B. Add headers (Row 1):
| Symbol | Buy Point | Sell Target | Stop Loss |
|--------|-----------|-------------|-----------|
| AAPL   | 150       | 165         | 145       |
| NABIL  | 1500      | 1600        | 1450      |

Example for NEPSE stocks:
| Symbol | Buy Point | Sell Target | Stop Loss |
|--------|-----------|-------------|-----------|
| NABIL  | 1520      | 1600        | 1480      |
| SCBN   | 650       | 700         | 620       |
| ADBL   | 560       | 610         | 540       |

### C. Create Service Account:
1. Go to [console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create new service account (name: `nepse-bot`)
3. Go to **Keys** → **Add Key** → **JSON**
4. Download the JSON file
5. **Share your Google Sheet** with the email from the JSON file (find `client_email`)

### D. Add to GitHub Secrets:
1. Open the downloaded JSON file in a text editor
2. Copy the **entire JSON contents**
3. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
4. Add:
   - `GOOGLE_SHEET_ID` = your sheet ID
   - `GOOGLE_CREDENTIALS_JSON` = paste the entire JSON (all on one line)

---

## Step 7: Test It

1. Go to your repo → **Actions** tab
2. Click **NEPSE Stock Alerts** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait 10 seconds, refresh
5. Click the run to see logs
6. Check Telegram/Gmail/Discord for test alert

---

## Step 8: Customize

### Change check frequency:
Edit `.github/workflows/nepse_alerts.yml`:
```yaml
- cron: '*/15 * * * *'  # every 15 min
- cron: '0 */1 * * *'   # every hour
- cron: '*/30 * * * *'  # every 30 min
```

### Add more stocks:
Just add rows to your Google Sheet. Script reads them automatically.

### Disable a channel:
Delete the secret from GitHub Settings, script skips it.

---

## Troubleshooting

**No alerts showing up?**
- Check GitHub Actions logs: **Actions** tab → click the workflow run
- Verify secrets are set (they won't show in logs for security)
- Test manually: click **Run workflow**

**Google Sheets not connecting?**
- Make sure you shared the sheet with the service account email
- Verify `GOOGLE_CREDENTIALS_JSON` is the full JSON (no line breaks)

**Telegram not working?**
- Verify you messaged @BotFather and got a token
- Make sure you sent a message to your bot first
- Test token: `https://api.telegram.org/bot<TOKEN>/getMe` should return your bot

**Price not updating?**
- NEPSE might be down (check [nepse.com.np](https://nepse.com.np) manually)
- Check GitHub Actions logs for scraping errors
- Website structure may have changed (may need to update scraper)

---

## Advanced: Running Locally

Want to test before pushing to GitHub?

```bash
# Install dependencies
pip install requests beautifulsoup4 gspread oauth2client

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export GOOGLE_SHEET_ID="your_sheet_id"
export GOOGLE_CREDENTIALS_JSON='{"full": "json", "here": "..."}'

# Run
python nepse_alert_agent.py
```

---

## Cost

✅ **100% FREE**
- GitHub Actions: 2,000 free minutes/month (this uses ~1 min per run)
- Telegram: Free
- Gmail: Free
- Discord: Free
- Google Sheets: Free

---

## Next Steps

1. ✅ Create repo
2. ✅ Upload code
3. ✅ Set up Telegram (or Gmail/Discord)
4. ✅ Create Google Sheet with watchlist
5. ✅ Add secrets to GitHub
6. ✅ Test with manual workflow run
7. ✅ Sit back and get alerts!

Questions? Check the logs in GitHub Actions for detailed error messages.

Happy trading! 🚀
