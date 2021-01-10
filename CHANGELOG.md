### Added

- Pin an event to a day of the week, by adding the prefix `[p]` to the summary. When the event is moved to the next month, the date will be adjusted to have the same day of the week.

## [1.4] - 8 January 2021

### Added

- (Internal) Added target date handling unit tests.

### Changed

- fix: improved handling of manually-moved recurring event (it was bypassing the filter for 'not today or after')

## [1.3] - 4 October 2020

### Added

- Added 'clean' command to clean up duplicate URLs and email address, if an event was edited in mobile version of Google Calendar

### Changed

- Added command 'move' to move the events

## [1.2] - 1 Sept 2020

### Changed

- Migrate to Python 3.7.9

## [1.1] - 1 Sept 2020

### Changed

- (Internal) Minor refactoring - #6
- Output total event count, before filtering - #4
- Adjust retrieval message - fixes #1
- Document the built-in hard-coded filtering - #7
- Simplify installation of dependencies - #2

## [1.0] - 31 Aug 2020

### Added

- Initial version: reads events for given month from Google Calendar. Applies white and black list filtering. Moves events to the following month.
