@ECHO OFF
ECHO This is NOT a dry run! Press CTRL+C to cancel
PAUSE

uv run python gcal_move_it.py clean %1
