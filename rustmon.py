#encoding: utf-8

from logging.handlers import TimedRotatingFileHandler
import datetime
import logging
import pathlib
import json
import requests
import time

API_KEY         = ''
rust_server_id  = '5866832' # Reddit low pop EU

http_headers = {
    'Authorization': f'Bearer {API_KEY}',
    }

api_resource = f'https://api.battlemetrics.com/servers/{rust_server_id}?include=player'

logs_dir = 'battlerustLogs/'
logs_file = 'battlerust.log'

# create logs directory
base_dir = pathlib.Path(__file__).resolve().parent
logs_dir = base_dir.joinpath(logs_dir)
logs_file = logs_dir.joinpath(logs_file)
pathlib.Path(logs_dir).mkdir(parents=True, exist_ok=True)

# create logger
logger = logging.getLogger('RustMon')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)10s[%(process)d] %(levelname)7s: %(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

# file logger
fh = TimedRotatingFileHandler(logs_file, when="d", interval=1, backupCount=60)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

# start app
logger.info(f'==> LOGS DIR: {logs_dir}')
logger.info(f'==> LOGS FILE: {logs_file}')
logger.info(f'==> API RESOURCE: {api_resource}')

# Arrays
players_temp = {}
players_online = {}
players_offline = {}

first_run = True

while True:
    
    players = {}
    with requests.get(api_resource, headers=http_headers) as r:

        if r.status_code == 200:
            d = r.json()
            included = d['included']

            server_name = d['data']['attributes']['name']
            server_players_now  = d['data']['attributes']['players']
            server_players_max  = d['data']['attributes']['maxPlayers']
            player_count = f'[{server_players_now}/{server_players_max}]'
            
            for i in included:
                if i['type'] == 'player':
                    player_id = i['id']
                    player_name = i['attributes']['name']

                    players[player_id] = player_id
                    
                    if players_online.get(player_id):
                        pass
                    else:
                        if not first_run:
                            logger.info(f'{player_name} ({player_id}) joined the game {player_count}')
                        players_online[player_id] = player_name

            for x in list(players_online.keys()):
                if players.get(x) is None:
                    logger.info(f'{players_online.get(x)} ({x}) left the game {player_count}')
                    players_online.pop(x)
    if first_run:
        logger.info(f'Now watching: {server_name} {player_count}')
        first_run = False

    time.sleep(10)





def mainloop():
    print('Running...')
