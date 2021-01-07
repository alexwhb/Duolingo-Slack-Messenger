import json
from os import getenv

import requests


class Slack:
    def __init__(self):
        self._webhook_url = getenv("SLACK_WEB_HOOK_URL")

    def send_message(self, message_text):
        payload = {"text": message_text}
        requests.post(self._webhook_url,
                      data=json.dumps(payload))

    @staticmethod
    def _slack_link(text: str, url: str):
        return f"<{url}|{text}>"

    def send_daily_reminder(self):
        """This will check each of the subscribed users around 3PM if they've not logged any points...
        a reminder to do so"""

        message = f"This is your daily reminder to do some foreign language study on {self._slack_link('Duo Lingo', 'https://www.duolingo.com')}"

        self.send_message(message)

    @staticmethod
    def _format_streak(streak_days: int):
        if streak_days > 0:
            return f"Your streak *{streak_days} days* :tada:"
        else:
            return "Sadly you have no streak going :sob::sob::sob:"

    def send_user_stats(self, stats_data: dict):
        """
        This will slack all users their point break downs for the day.
        Returns:

        """
        for username in dict.keys(stats_data):
            output_message = f"*{username}* Stats:\n" \
                             f"\tTotal XP: *{stats_data[username]['total_points']:,}* :star:\n" \
                             f"\tPoints since last last day active: *+{stats_data[username]['point_diff']}XP*\n" \
                             f"\t{self._format_streak(stats_data[username]['streak_days'])}\n\n\n"
            self.send_message(output_message)
