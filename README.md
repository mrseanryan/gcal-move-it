# :calendar: gcal_move_it README

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
- Move non-recurring events from one month to the next month. (exception: a recurring event that was manually moved IS included)
- Only events that occurred before today are moved.

Usage: gcal_move_it.py move <source month 1..12> [options]

The options are:
[-b --blacklist - Specify a blacklist to exclude some events]
[-d --dryrun - Perform a dry run, without actually modifying the calendar]
[-h --help]
[-s --skipMovedRecurring] - Skip events that are recurring but were manually moved
[-t --targetdate - Specify an exact target date (instead of the default which is 'one month later')]
[-w --whitelist - Specify a whitelist to include only some events]

Examples:
gcal_move_it.py clean 1
gcal_move_it.py move 1
gcal_move_it.py move 1 -w urgent;important
gcal_move_it.py move 1 -b "cancelled;^done" -d -w urgent;important
gcal_move_it.py move 1 -w subject_1;subject_2 -t 2021-01-13
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

Events are filtered, before deciding which events to process.

The following built-in rulies for filtering are _always_ applied.

Events must be:

- all-day, for 1 day
- not a timed event (is all-day)
- not recurring (except if was manually moved)

Exceptions:

- For the 'move' command, the event must be before today.

Besides that, the optional black and white lists are applied, as specified via options on the command line.

# notes on prefixes

A Google Calendar event can have a prefix added to its summary, to help filter via gcal-move-it.

## standard prefixes

| Prefix | Description         | Detail                                                                                                                                                                                                                                                     |
| ------ | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[p]`  | `p`inned to weekday | If an event has the prefix `[p]` then it is considered as `p`inned to that day of the week. When the event is moved to the next month, the date will be adjusted to have the same day of the week. Note: the option `-targetdate` overrides this behavior. |

## custom prefixes

Together with the `blacklist` or `whitelist` options, you can use whatever custom prefixes or tags you like in your events. Below are some examples.

| Prefix | Description            | Detail                                                                   |
| ------ | ---------------------- | ------------------------------------------------------------------------ |
| `k`    | O`K` meaning is 'done' | The event is done, so it will NOT be moved to next month                 |
| `done` | Done                   | The event is done, so it will NOT be moved to next month                 |
| `n/a`  | `N`ot `A`pplicable     | The event is no longer applicable, so it will NOT be moved to next month |

# setup

1. Get the credentials file

   Use the [Google Console](https://console.cloud.google.com/) to create a new project, and add the **Google Calendar API** to that project.

   Option A

   - Go to APIs & Services
   - Create Credentials
   - Select `OAuth 2.0 Client IDs`
   - Select `Application Type` = `Desktop app`
   - Type a suitable name (include the machine name)
   - Download the credentials file

   Option B

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

# libraries used

gcal-move-it uses a few nice libraries:

| Library       | URL                                             | Description                                              |
| ------------- | ----------------------------------------------- | -------------------------------------------------------- |
| calendar      | https://docs.python.org/3/library/calendar.html | For calendar operations like ‘get weekday for this date’ |
| parameterized | https://pypi.org/project/parameterized/         | Easily parameterize your unit tests                      |

# tools used

| Tool | URL                           | Description                                                                                                               |
| ---- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| pip  | https://pypi.org/project/pip/ | pip used with a config file, makes it easy to restore a Python project on another machine (even between Windows and Mac!) |

# references

[Google Calendar API](https://developers.google.com/calendar/v3/reference/events/list)

[Google Calendar API - Concepts](https://developers.google.com/calendar/concepts)

[Google Calendar API - Python client API](http://googleapis.github.io/google-api-python-client/docs/dyn/calendar_v3.events.html)

[Quickstart example](https://developers.google.com/calendar/quickstart/python)

[Python Babel library (used for dates)](http://babel.pocoo.org/en/latest/)

# license

License is [MIT](./LICENSE)
