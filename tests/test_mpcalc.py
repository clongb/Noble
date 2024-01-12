import mpcalc

def test_get_mp_data():
    response = mpcalc.get_mp_data("https://osu.ppy.sh/community/matches/111271525") 
    assert response['match']['name'] == "OWC2023: (Poland) VS (Australia)"

def test_get_username():
    assert mpcalc.get_username("7562902") == "mrekk"

def test_get_userid():
    assert mpcalc.get_username("mrekk") == "7562902"

def test_get_beatmaptitle():
    assert mpcalc.get_beatmaptitle("4368595") == "Powerwolf - Sermon of Swords [Pilgrims of Dark]"

def test_get_map_data():
    response = mpcalc.get_map_data("4368595")
    assert response['max_combo'] == "1247"

def test_get_colon_index():
    json = mpcalc.get_mp_data("https://osu.ppy.sh/community/matches/111271525")
    assert mpcalc.get_colon_index(json) == 7

def test_get_discord_ids():
    id_list = [["John"],["Carl"]]
    assert mpcalc.get_discord_ids(id_list) == ["John", "Carl"]

def test_get_user_team():
    json = mpcalc.get_mp_data("https://osu.ppy.sh/community/matches/111271525")
    player_id = "7562902"
    assert mpcalc.get_user_team(json, player_id) == "1"

def test_get_player_score():
    json = mpcalc.get_mp_data("https://osu.ppy.sh/community/matches/111271525")
    games = json['games']
    player_id = "7562902"
    map_id = "4368595"
    total = mpcalc.get_player_score(json, games, returning_total=True, data=False, searching_map=False, player_id=player_id)
    player_stats = mpcalc.get_player_score(json, games, returning_total=False, data=True, searching_map=False, player_id=player_id)
    map_stats = mpcalc.get_player_score(json, games, returning_total=False, data=True, searching_map=True, map=map_id)
    assert total == {"mrekk": "9357259"}
    assert player_stats[0] == {'score': "908831",
                               '300': "1321",
                               '100': "21",
                               '50': "0",
                               'miss': "1",
                               'combo': "1422",
                               'mods': "65",
                              }
    assert len(player_stats) == 11
    assert map_stats[0] == {'score': "720677",
                            '300': "882",
                            '100': "4",
                            '50': "0",
                            'miss': "1",
                            'combo': "914",
                            'mods': "0",
                            'map': map_id,
                            'team': "2",
                            'id': player_id 
                           }
    assert len(map_stats) == 8
