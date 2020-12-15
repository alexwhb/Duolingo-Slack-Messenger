import json
import os
from functools import cached_property
from typing import Iterable, Optional
from datetime import datetime
import duolingo
from dotenv import load_dotenv


class Duo:
    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password

    @cached_property
    def api(self) -> duolingo:
        return duolingo.Duolingo(self._username, self._password)

    def get_friends_by_usernames(self, usernames: list) -> Iterable[dict]:
        friends = self.api.get_friends()
        for friend in friends:
            if friend["username"] in usernames:
                yield friend

    def get_my_total_account_points(self):
        total_points = 0
        for ln in self.api.get_languages(True):
            total_points += self.api.get_language_progress(ln)['points']

        return total_points

    @property
    def db_filename(self):
        """
        Returns:
            string: The filename / path to the db.json file
        """
        directory_path = os.path.expanduser("~")
        full_path = os.path.join(directory_path, '.duo_data')
        file_path = os.path.join(full_path, 'db.json')
        return file_path

    def read_db(self) -> dict:
        """
        Args:
            filename (string): The file name as a path
        Returns:
            object: The data as JSON.
        """
        with open(self.db_filename, 'r') as f:
            j = json.load(f)
            return dict(j)

    def write_db(self, data):
        """
        Args:
            filename (string): The file name as a path
            data (object): The object data to persist
        """
        if not os.path.exists(self.db_filename):
            os.makedirs(os.path.dirname(self.db_filename))

        with open(self.db_filename, 'w') as f:
            json.dump(data, f)

    def track_users(self, users: list):
        """
        collects all the users stats for the day and saves them to the local db

        Data will be stored like this
        users {
            'username' : {
                total points: 500
                history: {
                    '01-01-12': {
                                points: 500
                                point_diff: 100
                                }
                    '01-01-11': '400'
                }
            }
        }

        Args:
            users: list this is a list of user names
        """

        user_info = self.get_friends_by_usernames(users)
        try:
            stats = self.read_db()
        except FileNotFoundError:
            self.write_db({})
            stats = self.read_db()

        for user in user_info:
            self.update_stats_for_username(stats, user)

        # and get my account points
        user = {
            'username': 'alexwhb',
            'points': self.get_my_total_account_points()
        }
        self.update_stats_for_username(stats, user)
        self.write_db(stats)

    @staticmethod
    def last_active(username: str, stats: dict) -> Optional[datetime]:
        if stats[username]['point_diff'] > 0:
            return stats[username]['updated']  # datetime.strptime(stats[username]['updated'], '%Y-%m-%d %H:%M:%S.%f')
        else:
            for date in stats[username]['history']:
                history_stats = stats[username]['history'][date]
                if history_stats['point_diff'] > 0:
                    return stats[username][
                        'updated']  # datetime.strptime(date['exact_time_reported'], '%Y-%m-%d %H:%M:%S.%f')
        return None

    @staticmethod
    def streak_days(username: str, stats: dict) -> int:
        last_active = stats[username]['last_active']
        if last_active is None or last_active == 'None':
            return 0

        if isinstance(last_active, str):
            last_active = datetime.strptime(stats[username]['last_active'], '%Y-%m-%d %H:%M:%S.%f')

        now = datetime.now()
        diff = last_active - now
        if diff.days == 1:
            return stats[username]['streak_days'] + 1
        else:
            return 0

    @staticmethod
    def get_score_diff(username: str, current_score: int, data: dict) -> int:
        if username not in data:
            return 0
        else:
            sorted_keys = sorted(dict.keys(data[username]['history']))
            return current_score - data[username]['history'][sorted_keys[-1]]['points']

    def update_stats_for_username(self, stats, user):
        username = user['username']
        date = datetime.now().strftime("%m/%d/%y")
        if username in stats:
            stats[username]['total_points'] = user['points']
            stats[username]['point_diff'] = self.get_score_diff(username, user['points'], stats)
            stats[username]['last_active'] = str(self.last_active(username, stats))
            stats[username]['updated'] = str(datetime.now())
            stats[username]['streak_days'] = self.streak_days(username, stats)
            stats[username]['history'][date] = {
                'points': user['points'],
                'point_diff': self.get_score_diff(username, user['points'], stats),
                'exact_time_reported': str(datetime.now())
            }
        else:
            stats[user['username']] = {
                'total_points': user['points'],
                'point_diff': 0,
                'streak_days': 0,
                'last_active': None,
                'updated': str(datetime.now()),
                'history': {
                    date: {
                        'points': user['points'],
                        'point_diff': 0,
                        'exact_time_reported': str(datetime.now())
                    }
                }
            }


if __name__ == '__main__':
    load_dotenv()
    duo = Duo(os.getenv("DUO_USER_NAME"), os.getenv("DUO_PASSWORD"))
    duo.track_users(os.getenv("USERS_TO_TRACK").split(","))
