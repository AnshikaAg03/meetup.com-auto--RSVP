## Meetup RSVP Bot

A command-line automation tool that automatically RSVPs to events on Meetup for selected groups. This tool ensures you never miss high-demand events by registering as soon as they become available.

##  Features
-  Automated RSVP for Meetup events
-   Persistent login using Playwright (no repeated authentication)
-   etches upcoming events from selected groups
-  Fast and reliable registration for limited-seat events
-  Modular and maintainable code structure
-  Designed to run on Linux (cron-compatible)
-  How It Works

## The project is divided into three main components:

# Authentication (auth/login.py)
- Uses Playwright to launch a Chrome browser
- Stores session data locally using a persistent profile
- Requires one-time manual login
- Session is reused for future runs
#  Event Fetching (meetup/events.py)
- Navigates to /events page of a Meetup group
- Extracts event URLs dynamically
- Filters invalid or duplicate links
- Returns a list of upcoming events
# Auto RSVP (meetup/auto_rsvp.py)
- Opens each event page
- Detects RSVP button
- Automatically registers the user

## Project Structure 
```
Meetup-RSVP-Bot/
│
├── auth/
│   └── login.py          # Handles login and session persistence
│
├── meetup/
│   ├── __init__.py
│   ├── events.py         # Scrapes event URLs
│   └── auto_rsvp.py      # Performs RSVP automation
│
├── chrome_profile/       # Stores browser session (auto-created)
└── README.md
```

## Installation
-  Clone the repository
git clone https://github.com/your-username/Meetup-RSVP-Bot.git
cd Meetup-RSVP-Bot
- Install dependencies
    1. pip install playwright
    2. playwright install

## Setup Authentication

Run the login script:

``` 
python auth/login.py
```
A Chrome window will open
Log in manually to Meetup
Keep the window open for a few seconds
Session will be saved automatically

## Automating with Cron (Linux)

- To run the bot every hour:

``` 
crontab -e
 ```

- Add:

```
0 * * * * /usr/bin/python3 /path/to/your/script.py
```



