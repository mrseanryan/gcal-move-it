@ECHO OFF
ECHO This is NOT a dry run! Press CTRL+C to cancel
PAUSE

python gcal_move_it.py -b "^k ;^cancelled ;^done ;^n/a;=hol" %1
