import time
import os
import sqlite3


def get_top30(game, dedication_index):
    edge_db = '{}.db'.format(game)
    conn = sqlite3.connect(edge_db)
    c = conn.cursor()
    user_list = c.execute('SELECT Id FROM user_db where dedication > {} ORDER BY FOLLOWERS DESC LIMIT 30'.format(dedication_index)).fetchall()
    return user_list

game = 'Chess'

# start initial craling for broadcasters, then wait 600s
os.system("scrapy crawl followers")
print('initial crawl finished, wait 600s')
time.sleep(600)

# crawler specifications
dedication_index = 0.7
converge = False
converge_game = False
top30_broadcaster = get_top30(game, dedication_index)

iter_total = 0
converge_times = 0
threshold = 30  # converge_times > threshold, 30 times

while not converge_game:
    iter_total += 1
    os.system("scrapy crawl followers")

    # first get the current top30 broadcasters
    # compare with the previous top30
    # if they are not equal, reset converge_times, otherwise converge_times++
    broadcaster = get_top30(game, dedication_index)
    if top30_broadcaster != broadcaster:
        top30_broadcaster = broadcaster
        converge_times = 0  # reset the converge
    else:
        converge_times += 1

    # at least converge times > threshold
    if converge_times > threshold:
        converge_game = True

    print('iter_total:{}, convegetimes:{}'.format(iter_total, converge_times))

    # wait 3600s and start next round
    time.sleep(3600)

