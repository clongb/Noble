#!/usr/bin/python
import random
import discord
import mpcalc
import sheets
import os
from dotenv import load_dotenv
import asyncio
from threading import Thread
import subprocess
import time
import json
import string
import random

from discord.ext.commands import Bot
from discord import app_commands
from discord.ext import tasks, commands

load_dotenv()

BOT_PREFIX = "-"
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
MSG_SENT = False
intents = discord.Intents.all()
intents.members = True
client = Bot(command_prefix=BOT_PREFIX, intents=intents)
client.remove_command('help')
node_processes = []
observers = []
verifications = []

def run_verification():
    verifications.append(subprocess.Popen(["node", "./osubot/verification.js"]))
    print('Starting verification...\n')
    output = verifications[-1]

def run_node_server():
    node_processes.append(subprocess.Popen(["node", "./osubot/app.js"]))
    print('Starting server...\n')
    output = node_processes[-1]

def run_observer():
    observers.append(["python", "./fileobserver.py"])
    print('Starting observer...\n')
    output = subprocess.Popen(observers[-1]) 

def get_dict_value(nested_dict, value, prepath=()):
    for k, v in nested_dict.items():
        path = prepath + (k,)
        if v == value:
            return path
        elif hasattr(v, 'items'):
            p = get_dict_value(v, value, path)
            if p is not None:
                return p
            
def add_match(interaction: discord.Interaction, map1: str, map2: str, map3: str, map4: str, map5: str, phase: str, defender: str):
    maps = {
        "map1": map1.upper(),
        "map2": map2.upper(),
        "map3": map3.upper(),
        "map4": map4.upper(),
        "map5": map5.upper(),
    }

    rev_dict = {}
 
    for key, value in maps.items():
        rev_dict.setdefault(value, set()).add(key)
     
    result = [key for key, values in rev_dict.items()
                              if len(values) > 1]
        
    with open("userdb.json", "r") as openfile:
        user_json = json.load(openfile)
    with open("matchdb.json", "r") as openfile:
        match_json = json.load(openfile)

    if (match_json["matches"] == {}):
        match_index = 0
    else:
        match_index = str(int(list(match_json["matches"])[-1])+1)
    user_index = get_dict_value(user_json, interaction.user.name)[1]
    maps["player"] = user_json["users"][user_index]["osu_username"]
    maps["discord_id"] = interaction.user.name
    maps["phase"] = phase
    maps["defense_attempts"] = 0
    maps["attack_attempts"] = 0
    if phase == "attacker":
        maps["defender"] = defender
    
    match_json["matches"][match_index] = maps
    index = -1
  
    for j in match_json["matches"].values():
        index = -1
        for v in j.values():
            index += 1
            if (v == user_json["users"][user_index]["osu_username"] and j["phase"] == "defender") and  index == 5:
                match_json["matches"][match_index]["defense_attempts"] += 1
            if (v == user_json["users"][user_index]["osu_username"] and j["phase"] == "attacker") and  index == 5:
                match_json["matches"][match_index]["attack_attempts"] += 1
    
    if (match_json["matches"][match_index]["defense_attempts"] > 2 or match_json["matches"][match_index]["attack_attempts"] > 2 or result != []):
        return False
    
    json_object = json.dumps(match_json, indent=4, default=dict)
    
    with open("temp.json", "w") as outfile:
        outfile.write(json_object)

    return True

class Menu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        
        try:
            with open("temp.json", "r") as openfile:
                match_json = json.load(openfile)
            
            os.remove("temp.json")
            json_object = json.dumps(match_json, indent=4, default=dict)
            
            await interaction.response.defer(ephemeral=True)
            await asyncio.sleep(4)
            
            if not node_processes:
                with open("matchdb.json", "w") as outfile:
                    outfile.write(json_object)
                server = Thread(target=run_node_server)
                await interaction.followup.send("Match confirmed! Invites will be sent soon. If you did not get it or lost the invite, DM fooders `.invite` on osu! for another link.", ephemeral=True)
                server.start()
            else:
                 #json_object["matches"].pop("0")
                 with open("matchdb.json", "w") as outfile:
                    outfile.write(json_object)
                 await interaction.followup.send("There is currently a lobby in progress. Please wait until it's finished.", ephemeral=True)
    
        except FileNotFoundError:
            await interaction.followup.send("Slow down! You are spamming the button too much.", ephemeral=True)

        
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True

        try:
            os.remove("temp.json")
            await interaction.response.defer(ephemeral=True)
            await asyncio.sleep(4)
            await interaction.followup.send("Match setup has been cancelled.", ephemeral=True)
        except FileNotFoundError:
            await interaction.followup.send("Slow down! You are spamming the button too much.", ephemeral=True)
        

'''
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send('Command does not exist.')
'''

@client.command(pass_context=True)
async def roll(ctx): #Rolls a random number between 1-100
    num = random.randint(1, 100)
    num = str(num)
    response = 'You rolled a ' + num
    await ctx.send(response)

@client.command(pass_context=True)
async def help(ctx): #Lists all possible commands that the user can call
    embed = discord.Embed( #Setup the discord embed with the title, author, thumbnail, and all fields
        title='Noble commands (prefix -)',
        colour=discord.Color.blurple()
    )

    user = ctx.author
    embed.set_author(name='Command list', icon_url=user.avatar)
    embed.set_thumbnail(url='https://i.imgur.com/ob2enPt.png')
    embed.add_field(name='misc:', value='▸ **roll**, **help**', inline=False)
    embed.add_field(name='osu (note that these only work for tournament matches):', value='▸ **scores** (args: *link*): Lists the total score for each player within a match link and gives their match cost.\n_ _\n'
                                                                                          '▸ **stats** (args: *link*, *player name*): Lists the maps played and scores of an individual player, as well as their total and average scores.\n_ _\n'
                                                                                          '▸ **map** (args: *link*, *keyword*): Given a keyword, searches for a map within the mp link and displays the scores for each player as well as the total and average score for that map. If teamvs enabled, shows total and averages for both teams.', inline=False)
    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def stats(ctx, link: str, player: str, warmup: str): 
    '''Gets the stats of a specific player; shows all of the maps that they played and their scores on each one.

    Parameters
    ----------
    ctx: Context in which command is invoked under
    link: Osu multiplayer link for the match to be parsed
    player: Name of the player to return stats for
    warmup: Number of warmups played in the match
    '''
    userid = mpcalc.get_userid(player) #Call osu api to get the user id
    response = mpcalc.get_mp_data(link) #Parse the mp link json
    player = mpcalc.get_username(userid)
    map_ids = []
    map_names = []
    games = []
    #all_maps = []
    accuracies = []
    acc_sum = 0.0
    #pool_ids = mpcalc.get_mappool(response)
    rating = 0

    games = response['games'] 
    if int(warmup) > 0: #Ignore warmup maps
        for m in range(0, int(warmup)):
            del games[0]

    scores = mpcalc.get_player_score(response, games, False, True, False, player_id=userid) #Put all of the player's map scores into a new variable called scores

    for game in games: 
        if game['beatmap_id'] not in map_ids and game['beatmap_id'] in scores:
            map_ids.append(game['beatmap_id']) #Get all beatmap ids from the json
        for score in game['scores']: #Accuracy is not given in the json, so we manually calculate it based on 300/100/50/miss count and add it to the dict of the given map
            if userid in score['user_id']:
                if game['beatmap_id'] in map_ids:
                    scores[game['beatmap_id']]['accuracy'] = round(((50*int(
                                                            scores[game['beatmap_id']]['50'])+100*int(
                                                            scores[game['beatmap_id']]['100'])+300*int(
                                                            scores[game['beatmap_id']]['300']))/(300*(int(
                                                            scores[game['beatmap_id']]['50'])+int(
                                                            scores[game['beatmap_id']]['100'])+int(
                                                            scores[game['beatmap_id']]['300'])+int(
                                                            scores[game['beatmap_id']]['miss']))))*100, 2)
    for id in map_ids:
        map_names.append(mpcalc.get_beatmaptitle(id)) #Put all map names and accuracies in their own arrays
        accuracies.append(scores[id]['accuracy'])
    colon_index = mpcalc.get_colon_index(response)
    total = int(mpcalc.get_player_score(response, games, True, False, False, player_id=userid)[player])
    average = total/(len(map_ids))
    for acc in accuracies:
        acc_sum += acc
    avg_acc = round((acc_sum) / (len(map_ids)), 2)

    rating = round(((average / 1000000) * 1.15) * ((len(map_ids) / (len(games)))) * 2, 2)

    embed = discord.Embed( #Create embed
        title=response['match']['name'][:colon_index],
        description=response['match']['name'][colon_index + 1:],
        colour=discord.Color.blue()
    )

    user = ctx.author 
    embed.set_author(name='Player stats for ' + player, icon_url=user.avatar, url='https://osu.ppy.sh/u/'+userid) #Set all the embed fields
    embed.set_thumbnail(url='https://a.ppy.sh/'+userid)
    for n in range(len(map_ids)): #For loop to set all of the fields of individual map scores
        if scores[map_ids[n]]['mods'] != None:
            mod = ' **+'+mpcalc.Mod(int(scores[map_ids[n]]['mods'])).name+'**' #Convert any given mod enums
        else:
            mod = ''
        embed.add_field(name='Map '+str(n+1)+':', value='[**'+map_names[n]+'**](https://osu.ppy.sh/b/'+map_ids[n]+')'+mod+
                                                        '\n▸ **'+scores[map_ids[n]]['score']+'** ▸ '+str(scores[map_ids[n]]['accuracy'])+'%'+
                                                        '\n▸ **'+scores[map_ids[n]]['combo']+'x/'+mpcalc.get_map_data(map_ids[n])['max_combo']+'x** ▸ '+
                                                        scores[map_ids[n]]['300']+'/'+
                                                        scores[map_ids[n]]['100']+'/'+
                                                        scores[map_ids[n]]['50']+'/'+
                                                        scores[map_ids[n]]['miss'], inline=False)
    embed.add_field(name='_ _', value='Total score: **'+str(total)+'**\nAverage score: **'+str(int(average))+'**\nAverage accuracy: **'+str(avg_acc)+'%**', inline=False)
    embed.add_field(name='Match history:', value=link)
    await ctx.send(embed=embed)

@stats.error
async def stats_error(ctx, error): #Error message to be sent if the user input is invalid
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('Please specify a link and/or a player in the match to calculate.')
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send('Invalid link or player not found in mp link. (If argument is a match link and this shows up, pool is not in the database)')

@client.command(pass_context=True)
async def map(ctx, link: str, keyword: str, warmup: str):
    '''Searches the player scores on a specific map through a given keyword

    Parameters
    ----------
    ctx: Context in which command is invoked under
    link: Osu multiplayer link for the match to be parsed
    keyword: Keyword used to search for a map in the mp link
    warmup: Number of warmups played in the match
    '''
    keywordl = keyword.lower()
    response = mpcalc.get_mp_data(link) #Parse the mp link json
    player_ids = []
    games = []
    players = []
    red = {}
    red_ids = []
    blue = {}
    blue_ids = []
    colon_index = mpcalc.get_colon_index(response)
    #pool_ids = mpcalc.get_mappool(response)
    first_team = ''
    first_map = True
    change_first_map = False
    total = 0
    red_total = 0
    blue_total = 0
    difference = 0
    winner = ''
    red_printed = False
    blue_printed = False
    map_id = ''
    changed = False

    games = response['games']
    if int(warmup) > 0: #Ignore warmup maps
        for m in range(0, int(warmup)):
            del games[0]

    for game in games: #Iterates through every map played to find one that matches the keyword and gets the map id for use in get_player_score as well as player id/score data for both red and blue team individually for averaging.
        if map_id == '':
            if keywordl in mpcalc.get_beatmaptitle(game['beatmap_id']).lower() or map_id == game['beatmap_id']:
                if first_map:
                    change_first_map = True
                for score in game['scores']:
                    if score['user_id'] not in player_ids:
                        player_ids.append(score['user_id'])
                        map_id = game['beatmap_id']
                        if game['team_type'] == '2':
                            if score['team'] == '2':
                                red[score['user_id']] = score['score']
                                red_ids.append(score['user_id'])
                                if first_map and first_team == '': #Gets the team of the first score in the response json
                                    first_team = score['team']
                            elif score['team'] == '1':
                                blue[score['user_id']] = score['score']
                                blue_ids.append(score['user_id'])
                                if first_map and first_team == '':
                                    first_team = score['team']
        if change_first_map:
            first_map = False
            change_first_map = False

    map_scores = (mpcalc.get_player_score(response, games, False, True, True, map=map_id)) #Put all of the player's scores on the map obtained from map_id into a new variable called scores

    for game in games:
        if game['beatmap_id'] == map_scores[player_ids[0]]['map']:
            for t in range(len(game['scores'])): #Accuracy is not given in the json, so we manually calculate it based on 300/100/50/miss count and add it to the dict of the given player
                if game['scores'][t]['user_id'] in player_ids:
                    map_scores[game['scores'][t]['user_id']]['accuracy'] = round(((50 * int(
                        map_scores[game['scores'][t]['user_id']]['50']) + 100 * int(
                        map_scores[game['scores'][t]['user_id']]['100']) + 300 * int(
                        map_scores[game['scores'][t]['user_id']]['300'])) / (300 * (int(
                        map_scores[game['scores'][t]['user_id']]['50']) + int(
                        map_scores[game['scores'][t]['user_id']]['100']) + int(
                        map_scores[game['scores'][t]['user_id']]['300']) + int(
                        map_scores[game['scores'][t]['user_id']]['miss'])))) * 100, 2)

    for v in range(len(player_ids)): #Calculate the average player score for the specified map
        total += int(map_scores[player_ids[v]]['score'])
    average = total / (len(map_scores))
    for x in range(len(blue_ids)): #Calculate average score for red and blue team separately
        blue_total += int(blue[blue_ids[x]])
    for y in range(len(red_ids)):
        red_total += int(red[red_ids[y]])
    blue_average = blue_total / (len(map_scores)/2)
    red_average = red_total / (len(map_scores)/2)
    if blue_total > red_total: #Calculate total score difference and determine a winner
        difference = blue_total - red_total
        winner = 'Blue team'
    elif red_total > blue_total:
        difference = red_total - blue_total
        winner = 'Red team'

    embed = discord.Embed( #Create embed
        title=response['match']['name'][:colon_index],
        description=response['match']['name'][colon_index + 1:],
        colour=discord.Color.blue()
    )

    user = ctx.author
    embed.set_author(name='Map stats for ' + mpcalc.get_beatmaptitle(
        map_scores[player_ids[0]]['map']) + ' (keyword: ' + keyword + ')', icon_url=user.avatar)
    embed.set_thumbnail(url='https://i.imgur.com/ob2enPt.png')
    embed.set_image(url='https://assets.ppy.sh/beatmaps/' + mpcalc.get_map_data(map_scores[player_ids[0]]['map'])[
        'beatmapset_id'] + '/covers/cover.jpg')
    for z in range(len(player_ids)): #Put the username of every player into an array
        players.append(mpcalc.get_username(player_ids[z]))
    if len(player_ids) % 2 == 1:
        player_ids.append('')
        players.append('') #Add blank values to evenly divide the array during the embed field loop
        changed = True

    for c in range(int(len(player_ids) / 2)): #For loop to set all of the fields of player scores
        if c == int(len(player_ids) / 2) - 1 and changed: #If the player list length is odd and the for loop is at the end of the list, make value_str blank to avoid dict calls
            value_str = '\u200b'
        else:
            if map_scores[player_ids[c + int(len(player_ids) / 2)]]['mods'] != None: #Add mods used in the score if applicable
                mod2 = ' **+' + mpcalc.Mod(
                    int(map_scores[player_ids[c + int(len(player_ids) / 2)]]['mods'])).name + '**'
            else:
                mod2 = ''
            value_str = '[**' + players[c + int(len(player_ids) / 2)] + '**](' + 'https://osu.ppy.sh/u/' + \
                        player_ids[c + int(len(player_ids) / 2)] + ')\n▸ **' + \
                        map_scores[player_ids[c + int(len(player_ids) / 2)]]['score'] + '** ▸ ' + str(
                        map_scores[player_ids[c + int(len(player_ids) / 2)]]['accuracy']) + '%' + '\n▸ **' + \
                        map_scores[player_ids[c + int(len(player_ids) / 2)]]['combo'] + 'x/' + \
                        mpcalc.get_map_data(map_scores[player_ids[0]]['map'])['max_combo'] + 'x** ▸ ' + \
                        map_scores[player_ids[c + int(len(player_ids) / 2)]]['300'] + '/' + \
                        map_scores[player_ids[c + int(len(player_ids) / 2)]]['100'] + '/' + \
                        map_scores[player_ids[c + int(len(player_ids) / 2)]]['50'] + '/' + \
                        map_scores[player_ids[c + int(len(player_ids) / 2)]]['miss'] + ' ' + mod2 #Make value_str the score from the other half of the player_id array (team 2 scores)
        if map_scores[player_ids[c]]['mods'] != None: #Add mods used in the score if applicable
            mod = ' **+' + mpcalc.Mod(int(map_scores[player_ids[c]]['mods'])).name + '**' 
        else:
            mod = ''
        embed.add_field(name='\u200b',
                        value='[**' + players[c] + '**](' + 'https://osu.ppy.sh/u/' + player_ids[c] + ')\n▸ **' +
                        map_scores[player_ids[c]]['score'] + '** ▸ ' + str(
                        map_scores[player_ids[c]]['accuracy']) + '%' + '\n▸ **' +
                        map_scores[player_ids[c]]['combo'] + 'x/' + mpcalc.get_map_data(
                        map_scores[player_ids[0]]['map'])['max_combo'] + 'x** ▸ ' +
                        map_scores[player_ids[c]]['300'] + '/' +
                        map_scores[player_ids[c]]['100'] + '/' +
                        map_scores[player_ids[c]]['50'] + '/' +
                        map_scores[player_ids[c]]['miss'] + ' ' + mod, inline=True) #Insert team 1 scores
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.add_field(name='\u200b', value=value_str, inline=True) #Add value_str scores as embed field
    if response['games'][2]['team_type'] == '2': #If the game type is on Team VS, list red and blue team averages and total score depending on whether or not red or blue was the first team to be printed
        for n in range(0, 2):
            if blue_printed or first_team == '2' and n == 0:
                embed.add_field(name='\u200b', value='Red team average: **'+str(int(red_average))+'**', inline=True)
                if n == 0:
                    embed.add_field(name='\u200b', value='\u200b', inline=True)
                    red_printed = True
            elif red_printed or first_team == '1' and n == 0:
                embed.add_field(name='\u200b', value='Blue team average: **' + str(int(blue_average)) + '**', inline=True)
                if n == 0:
                    embed.add_field(name='\u200b', value='\u200b', inline=True)
                    blue_printed = True
        red_printed = False
        blue_printed = False
        for o in range(0, 2):
            if first_team == '2' and o == 0 or blue_printed == True:
                embed.add_field(name='\u200b', value='Red team total: **' + str(red_total)+'**', inline=True)
                if o == 0:
                    embed.add_field(name='\u200b', value='\u200b', inline=True)
                    red_printed = True
            elif first_team == '1' and o == 0 or red_printed == True:
                embed.add_field(name='\u200b', value='Blue team total: **' + str(blue_total)+'**', inline=True)
                if o == 0:
                    embed.add_field(name='\u200b', value='\u200b', inline=True)
                    blue_printed = True
        embed.add_field(name='\u200b', value='Difference: **' + str(difference) + '**', inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.add_field(name='\u200b', value='Winner: **' + winner + '**', inline=True)
    embed.add_field(name='\u200b',
                    value='Average score: **' + str(int(average)) + '**\n[Match history](' + link + ')',
                    inline=True)
    embed.add_field(name='\u200b', value='Total score: **' + str(total) + '**\n' + '[Beatmap link](' + 'https://osu.ppy.sh/b/' + map_id + ')', inline=True)
    await ctx.send(embed=embed)

@map.error
async def map_error(ctx, error): #Error message to be sent if the user input is invalid
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('No keyword or link found (type something after link to search for map)')
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send('Invalid mp link')

@client.command(pass_context=True)
async def add_roles(ctx, role_name: str):
    '''Adds a specific role to all discord members listed in a google spreadsheet

    Parameters
    ----------
    ctx: Context in which command is invoked under
    role_name: Name of the role to give to the discord members
    '''
    user = ctx.author
    server = ctx.message.author
    tags = mpcalc.get_discord_ids(sheets.get_values(tab='TAB', spreadsheet_id='ID', cells='RANGE')) #Insert spreadsheet id, range, and tab here
    members = []
    changed = 0
    if ctx.message.author.guild_permissions.administrator: #If the user calling the command has perms, do a for loop to add the discord role to every member in the spreadsheet
        for i in range(len(tags)):
            if ctx.guild.get_member_named(tags[i]) != None:
                members.append(ctx.guild.get_member(ctx.guild.get_member_named(tags[i]).id))
        for j in range(len(members)):
            if members[j] != None:
                role = discord.utils.get(members[j].guild.roles, name=role_name)
                if role not in members[j].roles:
                    await members[j].add_roles(role)
                    changed = changed+1
        text = "Added roles to "+str(changed)+" members."
        await ctx.send(text)
    else:
        text = "Sorry <@"+str(user.id)+">, you do not have permissions to do that! Silly boy!".format(ctx.message.author)
        await ctx.send(text)

@client.command(pass_context=True)
async def claim(ctx, stage: str, slot: str):
    '''Lets a user claim a slot to map in the mappool by writing their discord name, slot, and tournament stage to a google sheet

    Parameters
    ----------
    ctx: Context in which command is invoked under
    stage: The stage of the tournament the user wants to map for
    slot: The type of map the user wants to make
    '''
    user = ctx.author
    stageU = stage.upper()
    if(slot != None):
        slotU = slot.upper()
    else:
        slotU = None
    role = discord.utils.get(user.guild.roles, name="Mapper")
    if role in user.roles:
        mapper = str(user).split('#')[0]
        status = 'planning'
        try:
            sheets.write_to_sheet(os.environ.get('SHEET_TAB_NAME'), os.environ.get('GOOGLE_SHEET_ID'), os.environ.get('SHEET_GID'), stageU, slotU, mapper, '', '', '', '', '', '', '', '', status)
            text = "**" + stageU + ": " + slotU + "** has been claimed by <@" + str(user.id) + ">."
            await ctx.send(text)
        except sheets.StatError as e:
             await ctx.send(str(e))

    else:
        text = "Sorry <@" + str(user.id) + ">, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(text)

@claim.error 
async def claim_error(ctx, error): #Error message to be sent if the user input is invalid
    if isinstance(error, sheets.StatError):
        await ctx.send('Invalid round/mod. (Acceptable rounds: TBD, QL, RO32, RO16, QF, SF, F, GF) (Acceptable mods: NM, HD, HR, DT, FM, TB)')
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('You did not put a round or map')


@client.command(pass_context=True)
async def drop(ctx, stage: str, slot: str):
    '''Lets a user drop a map they have previously claimed by deleting their name, slot, and stage from the google sheet

    Parameters
    ----------
    ctx: Context in which command is invoked under
    stage: The stage of the tournament the user wants to map for
    slot: The type of map the user wants to make
    '''
    user = ctx.author
    stageU = stage.upper()
    if (slot != None):
        slotU = slot.upper()
    else:
        slotU = None
    role = discord.utils.get(user.guild.roles, name="Mapper")
    if role in user.roles:
        mapper = str(user).split('#')[0]
        try:
            sheets.remove_row(os.environ.get('SHEET_TAB_NAME'), os.environ.get('GOOGLE_SHEET_ID'), os.environ.get('SHEET_GID'), stageU, slotU, mapper)
            text = "**" + stageU + ": " + slotU + "** has been dropped."
            await ctx.send(text)
        except sheets.StatError as e:
             await ctx.send(str(e))
    else:
        text = "Sorry <@" + str(user.id) + ">, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(text)

@drop.error
async def drop_error(ctx, error): #Error message to be sent if the user input is invalid
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('You did not put a round or map')

@client.tree.command(name="attack", description="Start an attack lobby on an opposing clan")
async def start_attack(interaction: discord.Interaction, defender: str):
    view = Menu()
    phase = "attacker"
                
    with open("matchdb.json", "r") as openfile:
        match_json = json.load(openfile)

    defender_index = get_dict_value(match_json, defender)[1]

    map1 = match_json["matches"][defender_index]["map1"]
    map2 = match_json["matches"][defender_index]["map2"]
    map3 = match_json["matches"][defender_index]["map3"]
    map4 = match_json["matches"][defender_index]["map4"]
    map5 = match_json["matches"][defender_index]["map5"]
    
    try:
        if add_match(interaction, map1, map2, map3, map4, map5, phase, defender):
            await interaction.response.send_message(f"Press confirm to start your clan attack. Make sure you are online on osu! to receive the invite.", view=view, ephemeral=True)
        else:
            await interaction.response.send_message("Please check if you have entered any duplicate maps or if you have already attacked 2 times.")
    except TypeError:
        await interaction.response.send_message("Your osu! account is unlinked, use `/osu-link <username>` to link your account first.")

@client.tree.command(name="defend", description="Start a defense lobby")
async def start_defense(interaction: discord.Interaction, map1: str, map2: str, map3: str, map4: str, map5: str):
    view = Menu()
    phase = "defender"
    mods = ["nm", "hd", "hr", "dt"]
    hasMod = {
        map1: False,
        map2: False,
        map3: False,
        map4: False,
        map5: False
    }

    for mod in mods:
        for map in hasMod:
            if mod in map.lower() and len(map) == 3 and map[2].isdigit():
                if mod == "nm" and int(map[2]) <= 5:
                    hasMod[map] = True
                elif int(map[2]) <= 2:
                    hasMod[map] = True

    try:
        if (False in hasMod.values()):
            await interaction.response.send_message("Please input a valid map from the mappool (i.e.: NM1, NM2, etc.)")
        elif add_match(interaction, map1, map2, map3, map4, map5, phase, ""):
            await interaction.response.send_message(f"Press confirm to start your clan defense. Make sure you are online on osu! to receive the invite. (Maps: {map1}, {map2}, {map3}, {map4}, {map5})", view=view, ephemeral=True)
        else:
            await interaction.response.send_message("Please check if you have entered any duplicate maps or if you have already defended 2 times.")
    except TypeError:
        await interaction.response.send_message("Your osu! account is unlinked, use `/osu-link <username>` to link your account first.")

@client.tree.command(name="osu-link", description="Link your osu! account to Noble")
async def osu_link(interaction: discord.Interaction, username: str):
    with open("code.json", "r") as openfile:
        code_json = json.load(openfile)
    
    code_json["code"] = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=5))
    code_json["osu_username"] = username
    code_json["discord"] = f"{interaction.user.name}"
    code_json["user_id"] = f"{interaction.user.id}"

    code = code_json["code"]
    code_object = json.dumps(code_json, indent=4, default=dict)

    with open("code.json", "w") as outfile:
        outfile.write(code_object)

    server = Thread(target=run_verification)
    await interaction.response.send_message(f"To complete account verification, please send fooders this code on osu!: `{code}`", ephemeral=True)
    server.start()

@client.tree.command(name="osu-unlink", description="Unlink your osu! account to Noble")
async def osu_unlink(interaction: discord.Interaction):
    try:
        with open("userdb.json", "r") as openfile:
            user_json = json.load(openfile)
        
        discord_name = interaction.user.name

        user_index = get_dict_value(user_json, discord_name)[1]
        username = user_json["users"][user_index]["osu_username"]
        user_json["users"].pop(user_index)

        json_object = json.dumps(user_json, indent=4, default=dict)
            
        with open("userdb.json", "w") as outfile:
                outfile.write(json_object)
        await interaction.response.send_message(f"Successfully unlinked your osu account `{username}`")
    except TypeError:
        await interaction.response.send_message("Could not find user.")

@tasks.loop(seconds=1.0)
async def logger():
    channel = client.get_channel(1263685122306347079)
    logged = False

    if os.path.exists("./templog.txt") and not logged:
        file = open("templog.txt", "r")
        templine = file.readline()
        logged = True
        file.close()
        await channel.send(templine)
    if os.path.exists("./templog.txt") and logged:
        os.remove("./templog.txt")
        logged = False
                
@tasks.loop(seconds=1.0)
async def process_check():
    #channel = client.get_channel(1265881389786730611) public bot channel
    channel = client.get_channel(1255892723790250118)
    if node_processes:
        poll = node_processes[0].poll()
        if poll is not None:
            print("Server has been closed")
            node_processes.pop()
            #channel.send("The previous lobby has finished")

@tasks.loop(seconds=1.0)
async def verification_check():
    channel = client.get_channel(1265881389786730611) #public bot channel
    #channel = client.get_channel(1255892723790250118) #heheheha
    if verifications:
        poll = verifications[0].poll()
        with open("code.json", "r") as openfile:
            code_json = json.load(openfile)
        if poll == 1 and code_json != {}:
            id = code_json["user_id"]
            code_json.clear()
            
            code_object = json.dumps(code_json, indent=4, default=dict)

            with open("code.json", "w") as outfile:
                outfile.write(code_object)

            verifications.pop()

            await channel.send(f"<@{id}> Verification has timed out.")
        elif poll == 0 and code_json != {}:
            with open("userdb.json", "r") as openfile:
                user_json = json.load(openfile)

            if (user_json["users"] == {}):
                user_index = 0
            else:
                user_index = str(int(list(user_json["users"])[-1])+1)
        
            user_json["users"][user_index] = {
                "discord": code_json["discord"], 
                "osu_username": code_json["osu_username"]
            }
            id = code_json["user_id"]
            code_json.clear()

            user_object = json.dumps(user_json, indent=4, default=dict)

            with open("userdb.json", "w") as outfile:
                outfile.write(user_object)

            code_object = json.dumps(code_json, indent=4, default=dict)

            with open("code.json", "w") as outfile:
                outfile.write(code_object)

            verifications.pop()    
            await channel.send(f"<@{id}> Successfully verified your osu! account!")
            


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    server_count = 0

    for guild in client.guilds:
        server_count += 1
    status = discord.Game('Running on ' + str(server_count) + ' servers')
    await client.change_presence(activity=status)

    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    observer = Thread(target=run_observer)
    observer.start()
    logger.start()
    process_check.start()
    verification_check.start()
    
client.run(TOKEN)