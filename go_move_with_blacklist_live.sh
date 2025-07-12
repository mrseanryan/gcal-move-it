ECHO "This is NOT a dry run!"
ECHO ""
read -p "Press enter to continue OR CTRL+C to cancel"

poetry run python gcal_move_it.py move -b "^k ;^cancelled ;^done ;^n/a;=hol;^ill" $1 $2 $3 $4 $5
