# gcal_move_it README

A command line tool to bulk process events in a Google Calendar:

- clean the description of events, to remove duplicate URLs and email addresses, if the event was edited in the mobile version of Google Calendar
- move events from one month to another

# use

See the built-in help:

```
python gcal_move_it.py
```

```
# clean:
- clean descriptions that have doubled-up URLs or email addresses

Usage: gcal_move_it.py clean <month 1..12> [options]

# move:
- Move non-recurring events from one month to the next month.
- Only events that occurred before today are moved.

Usage: gcal_move_it.py move <source month 1..12> [options]

The options are:
[-b blacklist - Specify a blacklist to exclude some events]
[-d dryrun - Perform a dry run, without actually modifying the calendar]
[-h help]
[-t targetdate - Specify an exact target date (instead of the default which is 'one month later')]
[-w whitelist - Specify a whitelist to include only some events]

Examples:
gcal_move_it.py clean 1
gcal_move_it.py move 1
gcal_move_it.py move 1 -w urgent;important
gcal_move_it.py move 1 -b "cancelled;^done" -d -w urgent;important
```

Try a dry run, that does not modify your calendar:

```
python gcal_move_it.py move 1 -d
```

Move events from March to the next month (April):

```
python gcal_move_it.py move 3
```

Clean events in February:

```
python gcal_move_it.py clean 2
```

# notes on filtering

Events are filtered, before deciding which events to move.

The following built-in rulies for filtering are _always_ applied.

Events must be:

- all-day, for 1 day
- not a timed event (is all-day)
- is before today
- not recurring

Besides that, the optional black and white lists are applied, as specified via options on the command line.

# setup

1. Get the credentials file

   Use the [Google Console](https://console.cloud.google.com/) to create a new project, and add the **Google Calendar API** to that project.

   To create the credentials file, add a service account. Download the key in JSON format (the UI can be tricky to use!).

   See the [Google documentation](https://cloud.google.com/docs/authentication/getting-started) for more details.

2. Save the credentials file in this folder

So the file should be located at: `./credentials.json`

3. Install Python 3.7.x and pip

- Python 3.7.9 or later
- pip 20.2.2 or later

4. Install dependencies

```
pip install -r pip.config
```

# references

[Google Calendar API](https://developers.google.com/calendar/v3/reference/events/list)

[Google Calendar API - Concepts](https://developers.google.com/calendar/concepts)

[Google Calendar API - Python client API](http://googleapis.github.io/google-api-python-client/docs/dyn/calendar_v3.events.html)

[Quickstart example](https://developers.google.com/calendar/quickstart/python)

[Python Babel library (used for dates)](http://babel.pocoo.org/en/latest/)

# license

License is [MIT](./LICENSE)
