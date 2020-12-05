import scrapy
from ..items import FollowersItem
from twitchAPI.twitch import Twitch
from twitch import TwitchClient
from mining import twitch_crawler_settings


class twitch_follower(scrapy.Spider):
    name = 'followers'
    start_urls = [
        'http://twitch.tv'
    ]
    items = FollowersItem()
    game = twitch_crawler_settings.game

    twitch = Twitch(twitch_crawler_settings.broadcasters_crawler_id,
                    twitch_crawler_settings.broadcasters_crawler_secrete)
    twitch_v5 = TwitchClient(twitch_crawler_settings.broadcasters_crawler_id,
                             twitch_crawler_settings.broadcasters_crawler_secrete)
    twitch.authenticate_app([])
    pagination_cursor = []
    edgePage_cursor = []
    i = 1

    def parse(self, response):

        twitch_follower.items['GAME'] = twitch_follower.game
        game = twitch_follower.twitch.get_games(names=twitch_follower.game)
        gaming_id = game['data'][0]['id']

        # page range
        if not twitch_follower.pagination_cursor:
            streams = twitch_follower.twitch.get_streams(first=100, game_id=gaming_id, language='en')
            twitch_follower.pagination_cursor.append(streams['pagination']['cursor'])
        else:
            # go to next page
            streams = twitch_follower.twitch.get_streams(after=twitch_follower.pagination_cursor.pop(), first=100,
                                                         game_id=gaming_id, language='en')
            twitch_follower.pagination_cursor.append(streams['pagination']['cursor'])
            print(twitch_follower.i)
            twitch_follower.i += 1

        list_streams = streams['data']
        UniqueList_streams = list({myObject['user_id']: myObject for myObject in list_streams}.values())

        for user in UniqueList_streams:
            user_id = user['user_id']

            channel = twitch_follower.twitch_v5.channels.get_by_id(channel_id=user_id)
            videos = twitch_follower.twitch_v5.channels.get_videos(channel_id=user_id, limit=100)
            gaming_hour = 0
            total_hour = 0

            user_followers = channel['followers']
            view_count = channel['views']
            created_at = channel['created_at']
            updated_at = channel['updated_at']

            if videos:
                for video in videos:
                    total_hour += video['length']
                    if video['game'] == twitch_follower.game:
                        gaming_hour += video['length']
                if total_hour != 0:
                    dedication = gaming_hour / total_hour

            if gaming_hour > 1800:  # filter out gaming hour <= 30mins broadcasters
                twitch_follower.items['ID'] = int(user_id)
                twitch_follower.items['USER'] = int(user_id)
                twitch_follower.items['FOLLOWERS'] = int(user_followers)
                twitch_follower.items['view_count'] = int(view_count)

                twitch_follower.items['created_at'] = created_at
                twitch_follower.items['updated_at'] = updated_at

                twitch_follower.items['gaming_hour'] = round(gaming_hour / 3600, 2)
                twitch_follower.items['total_hour'] = round(total_hour / 3600, 2)
                twitch_follower.items['dedication'] = round(dedication, 2)

                yield twitch_follower.items

        if 'cursor' in twitch_follower.twitch.get_streams(after=twitch_follower.pagination_cursor[0], first=100,
                                                          game_id=gaming_id, language='en')['pagination']:
            yield scrapy.Request('http://twitch.tv', callback=self.parse)
