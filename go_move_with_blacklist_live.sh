ECHO "This is NOT a dry run!"
ECHO ""
read -p "Press enter to continue OR CTRL+C to cancel"

python3 gcal_move_it.py move -b "^k ;^cancelled ;^done ;^n/a;=hol" $1 $2 $3 $4 $5
