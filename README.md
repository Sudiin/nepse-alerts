# NEPSE Stock Alert Agent 🚀

Automated alerts for NEPSE stocks. Get notified on **Telegram**, **Gmail**, or **Discord** when prices hit your buy points, sell targets, or stop-loss levels.

**100% free. Runs automatically every 15 minutes.**

---

## Quick Start (5 minutes)

### 1️⃣ Clone & Push to GitHub
```bash
git clone https://github.com/YOUR_USERNAME/nepse-alerts
cd nepse-alerts
git push
```

### 2️⃣ Set Up Telegram Bot (Optional)
- Chat **@BotFather** on Telegram → `/newbot`
- Get your token and chat ID
- Add to GitHub Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

### 3️⃣ Create Google Sheet Watchlist
- Go to [sheets.google.com](https://sheets.google.com)
- Create sheet with columns: `Symbol | Buy Point | Sell Target | Stop Loss`
- Add your NEPSE stocks (NABIL, SCBN, ADBL, etc.)
- Share with service account email
- Add Sheet ID to GitHub Secrets: `GOOGLE_SHEET_ID`, `GOOGLE_CREDENTIALS_JSON`

### 4️⃣ Run It!
- Go to **Actions** tab → **Run workflow**
- Get alerts on Telegram/Gmail/Discord

---

## Features

✅ **Multi-channel alerts** — Telegram, Gmail, Discord (pick any/all)
✅ **Smart deduplication** — No spam when price bounces at your target
✅ **Three alert types** — Buy point, Sell target, Stop loss
✅ **100% free** — GitHub Actions + free APIs
✅ **Auto-updates** — Runs every 15 mins, no setup needed

---

## File Structure

```
nepse-alerts/
├── .github/workflows/
│   └── nepse_alerts.yml          # GitHub Actions workflow
├── nepse_alert_agent.py          # Main script
├── alert_state.json              # Tracks sent alerts (auto-updated)
├── SETUP_GUIDE.md                # Detailed setup instructions
└── README.md                      # This file
```

---

## Configuration

All config is in **GitHub Secrets** + **Google Sheet**.

### Required Secrets:
- `GOOGLE_SHEET_ID` — Your watchlist sheet ID
- `GOOGLE_CREDENTIALS_JSON` — Service account JSON (for Google Sheets access)

### Optional Secrets (pick at least one):
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`
- `GMAIL_SENDER` + `GMAIL_APP_PASSWORD` + `GMAIL_RECIPIENT`
- `DISCORD_WEBHOOK_URL`

See **SETUP_GUIDE.md** for detailed instructions on each.

---

## How It Works

1. **Every 15 minutes**, GitHub Actions runs the script
2. Script scrapes NEPSE prices from [nepse.com.np](https://nepse.com.np)
3. Compares current price against your buy/sell/SL targets
4. If price hits a target **and we haven't already alerted**, sends notification
5. Saves alert state to avoid spam

Example alert:
```
🟢 NABIL hit BUY!
Price: 1520.5
Target: 1520
```

---

## Adding More Stocks

Just add rows to your Google Sheet:

| Symbol | Buy Point | Sell Target | Stop Loss |
|--------|-----------|-------------|-----------|
| NABIL  | 1500      | 1600        | 1450      |
| SCBN   | 650       | 700         | 620       |
| ADBL   | 560       | 610         | 540       |
| HBL    | 800       | 850         | 780       |

Script reads it automatically. No code changes needed.

---

## Troubleshooting

**Not getting alerts?**
- Check GitHub Actions logs: **Actions** → click the workflow run
- Verify secrets are set
- Make sure you messaged the Telegram bot first

**Google Sheets error?**
- Share the sheet with the service account email (from JSON)
- Verify `GOOGLE_CREDENTIALS_JSON` is complete (no line breaks)

**NEPSE scraper broken?**
- Website structure may have changed
- Check logs for BeautifulSoup errors
- Open issue or update the scraper code

---

## Local Testing

```bash
pip install requests beautifulsoup4 gspread oauth2client

export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export GOOGLE_SHEET_ID="your_sheet_id"
export GOOGLE_CREDENTIALS_JSON='{"full":"json","credentials":"here"}'

python nepse_alert_agent.py
```

---

## Customization

### Change check frequency:
Edit `.github/workflows/nepse_alerts.yml`:
```yaml
cron: '*/30 * * * *'  # Every 30 minutes
cron: '0 9-15 * * 1-5'  # Only during market hours, weekdays
```

### Disable a channel:
Just delete its secret from GitHub Settings. Script skips unconfigured channels.

### Change scraper:
Edit the `fetch_nepse_prices()` function in `nepse_alert_agent.py` if NEPSE changes their HTML structure.

---

## Cost

| Service | Cost |
|---------|------|
| GitHub Actions | Free (2,000 mins/month) |
| Telegram | Free |
| Gmail | Free |
| Discord | Free |
| Google Sheets | Free |
| **Total** | **$0** ✅ |

---

## Notes

- Alerts run 24/7, but NEPSE only trades 10am–3pm (you'll get buy alerts during those hours)
- Stock symbols are case-insensitive in the script
- Price comparisons: buy/SL are ≤, sell is ≥
- Alert state saved in `alert_state.json` to prevent duplicates

---

## Contributing

Found a bug? Prices not scraping correctly?
- Open an issue
- Update the scraper code
- Test locally first

---

## License

MIT — Use it, modify it, share it. Free and open.

---

**Happy trading! 🚀**

For detailed setup instructions, see **SETUP_GUIDE.md**.
