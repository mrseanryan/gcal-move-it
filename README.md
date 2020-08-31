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

5. Install dependencies

```
pip install Babel
```

# use

See the built-in help:

```
python gcal-move-it.py
```

Try a dry run, that does not modify your calendar:

```
python gcal-move-it.py 1 -d
```

Move events from March to the next month (April):

```
python gcal-move-it.py 3
```

# references

[Google Calendar API](https://developers.google.com/calendar/v3/reference/events/list)
[Google Calendar API - Concepts](https://developers.google.com/calendar/concepts)
[Quickstart example](https://developers.google.com/calendar/quickstart/python)
[Python Babel library (used for dates)](http://babel.pocoo.org/en/latest/)

# license

License is [MIT](./LICENSE)
