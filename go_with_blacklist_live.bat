@ECHO OFF
ECHO This is NOT a dry run! Press CTRL+C to cancel
PAUSE

python gcal-move-it.py -b "^k ;^cancelled ;^done ;^n/a;=hol" %1
