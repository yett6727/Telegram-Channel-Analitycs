A complete analytics dashboard for Telegram channels with automated data collection.

## Features

- 📊 Real-time channel statistics
- 📈 Interactive charts and visualizations
- 🏆 Top performing posts tracking
- 📅 Daily metrics and trends
- 👥 Member growth tracking
- 🔄 Automated data collection

## Installation

1. **Install Python dependencies:**
```bash
pip install telethon flask pandas schedule
```

2. **Get Telegram API credentials:**
   - Go to https://my.telegram.org
   - Login with your phone number
   - Navigate to 'API Development Tools'
   - Create a new application
   - Copy your `API_ID` and `API_HASH`

3. **Configure the application:**
   Edit `config.py` and add:
   - Your `API_ID`
   - Your `API_HASH`
   - Your phone number (with country code)
   - Your channel username (e.g., '@yourchannel')

## Usage

### First Time Setup

Run the data collector to authenticate with Telegram:
```bash
python data_collector.py
```

You'll be prompted to enter the authentication code sent to your Telegram app.

### Running the Application

1. **Start the data collector** (in background):
```bash
python data_collector.py &
```

2. **Start the web server**:
```bash
python app.py
```

3. **Open your browser**:
Navigate to `http://localhost:5000`

## Project Structure

```
telegram_analytics/
├── app.py              # Flask web server
├── data_collector.py   # Telethon data collection
├── database.py         # Database operations
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── static/
│   ├── style.css      # Styling
│   └── script.js      # Frontend logic
└── templates/
    └── index.html     # Main page
```

## Configuration Options

Edit `config.py` to customize:

- `COLLECTION_INTERVAL`: Data collection frequency (default: 3600 seconds / 1 hour)
- `CHANNEL_USERNAME`: Target channel to analyze
- `DATABASE_PATH`: SQLite database location

## Troubleshooting

**Authentication Issues:**
- Make sure your phone number includes the country code
- Check that API_ID and API_HASH are correct
- Delete `session.session` file and try again

**No Data Showing:**
- Wait for the first data collection cycle to complete
- Check that your channel username is correct
- Verify you have access to the channel

**Permission Errors:**
- Ensure the channel is public or you're a member
- Some channels may restrict API access

## Notes

- The application collects data from the last 30 days on each run
- Member growth tracking requires multiple data collection cycles
- All data is stored locally in SQLite database
- Session files are created for Telegram authentication