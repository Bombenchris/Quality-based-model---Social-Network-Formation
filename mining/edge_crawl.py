import sqlite3
from twitchAPI.twitch import Twitch
from tqdm import tqdm
import pandas as pd
import time
from ..mining import twitch_crawler_settings


class EdgesPipeline:

    def __init__(self, name):
        self.create_connection(name)
        self.create_table()

    def create_connection(self, name):
        self.conn = sqlite3.connect("{}.db".format(name))
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""create table IF NOT EXISTS edges_db(
                Source INTEGER,
                Target INTEGER,
                Type TEXT,
                Date TEXT,
                UNIQUE (Source, Target)
                )""")

    def get_broadcasters(self):
        df_broadcasters = pd.read_sql_query(
            "SELECT * FROM user_db ORDER BY FOLLOWERS DESC", self.conn)
        return df_broadcasters

    def store_db(self, item):
        self.curr.execute("""insert or replace into edges_db values (?,?,?,?)""", (
            item['SOURCE'],
            item['TARGET'],
            item['TYPE'],
            item['DATE']
        ))
        self.conn.commit()

    def follower_parse(self, user_id, loops):

        edgePage_cursor = []
        for loop in range(loops):
            if not edgePage_cursor:
                user_followers = twitch.get_users_follows(first=100, to_id=user_id)
                try:
                    edgePage_cursor.append(user_followers['pagination']['cursor'])
                except:
                    pass
            else:
                user_followers = twitch.get_users_follows(after=edgePage_cursor.pop(), first=100, to_id=user_id)

                try:
                    edgePage_cursor.append(user_followers['pagination']['cursor'])
                except:
                    pass

            items = {}
            for follower in user_followers['data']:
                try:
                    items['SOURCE'] = int(follower['from_id'])
                    items['TARGET'] = int(user_id)
                    items['TYPE'] = 'Directed'
                    items['DATE'] = follower['followed_at']
                    self.store_db(items)
                except:
                    pass


twitch = Twitch(twitch_crawler_settings.edges_crawler_id, twitch_crawler_settings.edges_crawler_secrete)
twitch.authenticate_app([])

game = twitch_crawler_settings.game
database = '{}.db'.format(game)

# start the EdgesPipeline
Pineline = EdgesPipeline(game)
data = Pineline.get_broadcasters()

# for each broadcaster, crawl all her followers
# then: fetch 100 followers per loop, total loops = follower // 100
for index, row in tqdm(data.iterrows()):
    id = str(row['Id'])
    follower = row['FOLLOWERS']
    loops = round(follower / 100) + 1
    print(str(loops) + ' loops required')
    Pineline.follower_parse(id, loops)
    time.sleep(5)
