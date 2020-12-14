from os import getenv
import sys
from dotenv import load_dotenv
from duo import Duo
from slack import Slack

if __name__ == "__main__":
    load_dotenv()
    slack = Slack()
    duo = Duo(getenv("DUO_USER_NAME"), getenv("DUO_PASSWORD"))
    if len(sys.argv) == 1:
        print("Sorry there's no command that matches that")

    if "reminder" in sys.argv:
        print("reminder will be called")
        slack.send_daily_reminder()

    if "user-stats" in sys.argv:
        # this will both update the record and spit out user stats
        print("user stats will be called")
        duo.track_users(getenv("USERS_TO_TRACK").split(","))
        slack.send_user_stats(duo.read_db())
