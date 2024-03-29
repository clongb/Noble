import random
import discord
import mpcalc
import sheets
import os

from discord.ext.commands import Bot
#from discord.ext.commands import tasks

BOT_PREFIX = "-"
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
MSG_SENT = False
intents = discord.Intents.all()
intents.members = True
client = Bot(command_prefix=BOT_PREFIX, intents=intents)
client.remove_command('help')

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

@client.event
async def on_ready(): #Displays the number of servers the bot is running on in its activity status
    server_count = 0
    for guild in client.guilds:
        server_count += 1
    status = discord.Game('Running on ' + str(server_count) + ' servers')
    await client.change_presence(activity=status)

'''
@client.command(pass_context=True)
async def scores(ctx, link: str, warmup: str): #TODO: rewrite formula in numpy/debug
    Calculates the total score and match cost of every player in the lobby given through a osu multiplayer link

    Parameters
    ----------
    ctx:
    link:
    warmup:

    player_ids = []
    players = []
    player_scores = []
    map_scores = []
    averages = []
    ratings = []
    games = []
    all_maps_played = []
    individual_scores = []
    map_avgs = []
    map_max_score = -1
    avg_top_scores = 0
    highest_rating_index = 0
    cmp = 0
    highest_avg = 0
    highest_avg_per_map = 0
    response = mpcalc.get_mp_data(link)
    #pool_ids = mpcalc.get_mappool(response)

    games = response['games']
    if int(warmup) > 0:
        for m in range(0, int(warmup)):
            del games[0]

    for game in games:
        for score in game['scores']:
            if score['user_id'] not in player_ids:
                player_ids.append(score['user_id'])

    for k in range(len(player_ids)):
        received_player = mpcalc.get_player_score(response, games, True, False, False, player_id=player_ids[k])
        individual_scores.append(mpcalc.get_player_score(response, games, False, True, False, player_id=player_ids[k]))
        player_scores.append(received_player)
        players.append(mpcalc.get_username(player_ids[k]))
    for r in range(len(player_ids)):
        numerator = 0
        denominator = len(individual_scores[r])
        map_total = 0
        map_avg = 0
        avg_total = 0
        mid = 0
        median = 0
        swapped = True
        for n in range(len(individual_scores[r])):
            for game in games:
                map_scores = (mpcalc.get_player_score(response, games, False, True, True, map=game['beatmap_id']))
                for i in range(len(player_ids)):
                    map_total = 0
                    if player_ids[i] in map_scores:
                        map_total += int(map_scores[player_ids[i]]['score'])
                    all_maps_played.append(len(individual_scores[i]))
                if player_ids[r] in map_scores:
                    map_avg = map_total / (len(map_scores))
                    numerator += int(map_scores[player_ids[r]]['score'])/(map_avg)
        while swapped:
            swapped = False
            for i in range(len(all_maps_played)-1):
                if all_maps_played[i] > all_maps_played[i+1]:
                    all_maps_played[i], all_maps_played[i+1] = all_maps_played[i+1], all_maps_played[i]
                    swapped = True
        mid = int(len(all_maps_played)/2)
        median = all_maps_played[mid] if len(all_maps_played) % 2 != 0 else (all_maps_played[mid - 1] + all_maps_played[mid])/2
        ratings.append(round(((numerator/denominator)*(pow(denominator/median, (1/3)))),  2))
    for x in range(len(ratings)):
        if ratings[x] > ratings[highest_rating_index]:
            highest_rating_index = x
    colon_index = mpcalc.get_colon_index(response)
    embed = discord.Embed(
        title=response['match']['name'][:colon_index],
        description = response['match']['name'][colon_index + 1:],
        colour = discord.Color.blue()
    )

    user = ctx.author
    embed.set_author(name='Match scores for '+response['match']['name'][:colon_index], icon_url=user.avatar)
    embed.set_thumbnail(url='https://a.ppy.sh/'+player_ids[highest_rating_index])
    for i in range(len(players)):
        embed.add_field(name=players[i], value='▸ **'+player_scores[i][players[i]]+'** ▸ Match cost: **'+str(ratings[i])+'**', inline=False)
    embed.add_field(name='Match history:', value=link)
    await ctx.send(embed=embed)


@scores.error #Error message to be sent if the user input is invalid
async def scores_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('No link found.')
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send('Invalid link. (If argument is a match link and this shows up, pool is not in the database)')
'''

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
    embed.add_field(name='_ _', value='Total score: **'+str(total)+'**\nAverage score: **'+str(int(average))+'**\nAverage accuracy: **'+str(avg_acc)+'%**\nMatch cost: **'+str(rating)+'**', inline=False)
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

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)