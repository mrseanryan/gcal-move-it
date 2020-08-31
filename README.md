# gcal-move-it README

A command line tool to move events from one month to another, in a Google Calendar.

# setup

1. Get the credentials file
   Follow the instructions to activate the Google Calendar API, and get a credentials file:

https://developers.google.com/calendar/quickstart/python

2. Save the credentials file in this folder

So the file should be located at: `./credentials.json`

3. Install PIP and Python 2.x

- Python 2.7.13 or later
- PIP 10.01 or later

4. Install the Google client library

```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
