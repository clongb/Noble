import requests
import pprint
import sheets
from zipfile import ZipFile
import json
from enum import IntFlag

API_KEY = "TOKEN" #Insert osu api key here

class Mod(IntFlag):
    NoMod = 0
    NF = 1
    EZ = 2
    TD = 4
    HD = 8
    HR = 16
    SD = 32
    DT = 64
    RX = 128
    HT = 256
    NC = 512
    FL = 1024
    Autoplay = 2048
    SO = 4096
    AP = 8192
    PF = 16384
    Key4 = 32768
    Key5 = 65536
    Key6 = 131072
    Key7 = 262144
    Key8 = 524288
    FadeIn = 1048576
    Random = 2097152
    Cinema = 4194304
    Target = 8388608
    Key9 = 16777216
    KeyCoop = 33554432
    Key1 = 67108864
    Key3 = 134217728
    Key2 = 268435456
    ScoreV2 = 536870912
    Mirror = 1073741824
    HDHR = HD|HR
    HDNF = HD|NF
    EZHD = EZ|HD
    EZNF = EZ|NF
    HRNF = HR|NF
    NFHDHR = NF|HD|HR
    NFDT= NF|DT
    HRSD = HR|SD
    HDSD = HD|SD
    HDHRSD = HD|HR|SD
    HDFL = HD|FL
    HRFL = HR|FL
    HDHRFL = HD|HR|FL
    HDRX = HD|RX
    HRRX = HR|RX
    HDHRRX = HD|HR|RX
    HDSO = HD|SO
    EZHDSO = EZ|HD|SO
    HRSO = HR|SO
    HDHRSO = HD|HR|SO
    HDHT = HD|HT
    HRHT = HR|HT
    HDHRHT = HD|HR|HT
    HRDT = HR|DT
    HDPF = HD|PF
    HRPF = HR|PF
    HDHRPF = HD|HR|PF

def get_mp_data(link: str):
    '''Returns the match json of a given osu multiplayer link

    Parameters
    ----------
    link: URL of the osu multiplayer match
    '''
    url = 'https://osu.ppy.sh/api/get_match'
    mp = ''
    for character in link:
        if character.isdigit():
            mp += character
    url = url + '?mp=' + mp + '&k=' + API_KEY
    response = requests.get(url)
    return response.json()

def get_username(player_id: str):
    '''Returns the username of a player given their user ID

    Parameters
    ----------
    player_id: User ID of a given player (found in their user URL)
    '''
    url = 'https://osu.ppy.sh/api/get_user'
    u = player_id
    m = 0
    type = 'id'
    url = url + '?u=' + u + '&m=' + str(m) + '&type=' + type + '&k=' + API_KEY
    response = requests.get(url)
    return response.json()[0]['username']

def get_userid(player: str):
    '''Returns the ID of a player given their username

    Parameters
    ----------
    player: Username of a given player
    '''
    url = 'https://osu.ppy.sh/api/get_user'
    u = player
    m = 0
    type = 'string'
    url = url + '?u=' + u + '&m=' + str(m) + '&type=' + type + '&k=' + API_KEY
    response = requests.get(url)
    return response.json()[0]['user_id']

def get_beatmaptitle(mapid: str):
    '''Returns the title of a beatmap given the beatmap id

    Parameters
    ----------
    mapid: ID of a specified beatmap (the number at the end of a beatmap URL)
    '''
    url = "https://osu.ppy.sh/api/get_beatmaps?k=" + API_KEY + "&b=" + mapid
    response = requests.get(url)
    artist = response.json()[0]['artist']
    difficulty = response.json()[0]['version']
    title = artist + ' - ' + response.json()[0]['title'] + ' ['+difficulty+']'

    return title
def get_map_data(mapid: str):
    '''Returns the json of a given osu beatmap that includes its map stats and metadata

    Parameters
    ----------
    mapid: ID of a specified beatmap (the number at the end of a beatmap URL)
    '''
    url = "https://osu.ppy.sh/api/get_beatmaps?k=" + API_KEY + "&b=" + mapid
    response = requests.get(url)

    return response.json()[0]

def get_colon_index(json: dict):
    '''Returns the index number in the mp match name that has a colon character

    Parameters
    ----------
    json: json from the osu mp link
    '''
    colon_index = len(json['match']['name'])
    for h in range(len(json['match']['name'])):
        if json['match']['name'][h] == ':':
            colon_index = h
            break
    return colon_index


def get_discord_ids(list):
    '''Returns a single dimensional array of discord IDs given a two dimensional list of IDs (in this use case, the list would be from a google spreadsheet)

    Parameters
    ----------
    list: 2D array containing the IDs (since google sheets converts data to 2D arrays)
    '''
    id_indexes = []
    discord_ids = []
    for j in range(len(list)):
        if list[j] != []:
            discord_ids.append(list[j][0])
        else:
            continue
    return discord_ids


def get_user_team(json: dict, player_id: str):
    '''Returns the color team that the given player is on in a team VS match

    Parameters
    ----------
    json: json from the osu mp link
    player_id: User ID of a given player (found in their user URL)
    '''
    team = ''
    for game in json['games']:
        if game['team_type'] == '2':
            for score in game['scores']:
                if score['user_id'] == player_id:
                    team = (score['team'])
    return team

def get_player_score(json: dict, games: list, returning_total: bool, data: bool, searching_map: bool, player_id='', map=''):
    '''Depending on how the function is used, returns the dict of a player or map and the score statistics of either a given map or all of the maps played in the multiplayer json

    Parameters
    ----------
    json: json from the osu mp link
    games: The list of maps played in the multiplayer link that also includes data regarding map scores and the players that played each map (corresponds to the keyword 'games' in the json)
    returning_total: True when the use case of the function is to return a player's total score
    data: True when requesting more in-depth statistics on a player's map score
    searching_map: True if score data for a specific map is to be returned instead
    player_id: User ID of a given player (found in their user URL)
    '''
    if player_id != '':
        player = get_username(player_id)
    map_scores = {}
    total_score = 0
    mods = None
    #map_ids = get_mappool(json)

    for game in games: 
        if searching_map: #Insert a score dict with all of the score statistics into a list of scores from the same map
            if map == game['beatmap_id']:
                for score in game['scores']:
                    if score['user_id'] not in map_scores:
                        if score['enabled_mods'] != None:
                            mods = score['enabled_mods']
                        elif game['mods'] == '0':
                            mods = None
                        else:
                            mods = game['mods']
                        map_scores[score['user_id']] = {'score': score['score'],
                                                        '300': score['count300'],
                                                        '100': score['count100'],
                                                        '50': score['count50'],
                                                        'miss': score['countmiss'],
                                                        'combo': score['maxcombo'],
                                                        'mods': mods,
                                                        'map': map,
                                                        'team': get_user_team(json, score['user_id']),
                                                        'id': score['user_id']
                                                        }
        else:
            for score in game['scores']: 
                if player_id == score['user_id']:
                    if game['beatmap_id'] in map_scores:
                        if returning_total and int(score['score']) > int(map_scores[game['beatmap_id']]): #Make map_scores an array of all the map scores without adding any additional stats
                            map_scores[game['beatmap_id']] = int(score['score'])
                        elif data and int(score['score']) > int(map_scores[game['beatmap_id']]['score']): #Puts score statistics dictionaries into map_scores instead of just the raw score value
                            if score['enabled_mods'] != None:
                                mods = score['enabled_mods']
                            elif game['mods'] == '0':
                                mods = None
                            else:
                                mods = game['mods']
                            map_scores[game['beatmap_id']] = {'score': score['score'],
                                                              '300': score['count300'],
                                                              '100': score['count100'],
                                                              '50': score['count50'],
                                                              'miss': score['countmiss'],
                                                              'combo': score['maxcombo'],
                                                              'mods': mods,
                                                              }
                            mods = None
                    else: #Returning total scores/score data in one map rather than a player's total score
                        map_scores[game['beatmap_id']] = int(score['score'])
                        if data:
                            if score['enabled_mods'] != None:
                                mods = score['enabled_mods']
                            elif game['mods'] == '0':
                                mods = None
                            else:
                                mods = game['mods']
                            map_scores[game['beatmap_id']] = {'score': score['score'],
                                                              '300': score['count300'],
                                                              '100': score['count100'],
                                                              '50': score['count50'],
                                                              'miss': score['countmiss'],
                                                              'combo': score['maxcombo'],
                                                              'mods': mods,
                                                              }
                            mods = None
    if returning_total: #Return total score for a player
        total_score = sum(map_scores.values())
        return {player: str(total_score)}
    else:
        return map_scores
