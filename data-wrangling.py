import cassiopeia as cass
from cassiopeia.core import Summoner
from cassiopeia import Queue
from numpy.core.fromnumeric import shape

from riotwatcher import LolWatcher, ApiError

import numpy as np
import pandas as pd

import random

from datetime import timedelta
import time


def get_player_stats(player):
    return np.array([player.summoner_spell_d.id, player.summoner_spell_f.id, player.champion.id, player.side, player.individual_position,
                        player.stats.assists, player.stats.damage_dealt_to_buildings, player.stats.damage_dealt_to_objectives, 
                        player.stats.damage_dealt_to_turrets, player.stats.deaths, player.stats.gold_earned, player.stats.kda, 
                        player.stats.kills, player.stats.level, player.stats.time_CCing_others, player.stats.total_damage_dealt, 
                        player.stats.total_damage_taken, player.stats.total_minions_killed, player.stats.turret_kills, 
                        player.stats.vision_score, player.stats.win])
                        

def get_match_stats(match):
    match_stats = np.empty(shape = (0,21))
    players = match.participants

    # Random Summoner Choice to Ensure Independence
    random_summoner = random.choice(players)
    match_stats = np.r_[match_stats, [get_player_stats(random_summoner)]]
        
 
    return match_stats

def get_match_history_stats(history):

    history_stats = np.empty(shape = (0,21))


    for match in history:
        if match.duration < timedelta(minutes=15, seconds= 30):
            # skip remake and ff15
            pass
        else:
            history_stats = np.r_[history_stats, get_match_stats(match)]



    return history_stats

def get_summoner_list_stats(summoners):

    summoner_stats = np.empty(shape=(0,21))

    
    i = 0
    for summoner in summoners:

        i+= 1
        
        s = Summoner(name=summoner, region='EUW')

        match_history = cass.get_match_history(continent=s.region.continent, puuid=s.puuid, queue=Queue.ranked_solo_fives)
        summoner_stats = np.r_[summoner_stats, get_match_history_stats(match_history)]

        print(str(i) + ' Summoner')
        print('Sleep for 10 Seconds')
        time.sleep(10)
    
    return summoner_stats
        


def implement_data_dragon(data, api):
    watcher = LolWatcher(api_key)
    # check league's latest version
    latest = watcher.data_dragon.versions_for_region('na1')['n']['champion']
    # Lets get some champions static information
    static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')

    # champ static list data to dict for looking up
    champ_dict = {}
    for key in static_champ_list['data']:
        row = static_champ_list['data'][key]
        champ_dict[row['key']] = row['id']

    print(shape(champ_dict))
        
    for index, row in data.iterrows():
        row['champion'] = champ_dict[str(row['champion'])]

    return data

def get_challenger_accounts():
    
    challenger_data = cass.get_challenger_league(cass.Queue.ranked_solo_fives, region=cass.Region('EUW'))

    names = []

    for s in challenger_data.entries:
        names.append(s.summoner.name)

    return names
        
#%% Main run                 
if __name__ == "__main__":
    api_key = "RGAPI-05ab3243-4e06-48e7-9476-c26382faae0d"
    cass.set_riot_api_key(api_key)
    
    

    
    summoner_list = random.sample(get_challenger_accounts(), 300)
    data = pd.DataFrame(get_summoner_list_stats(summoner_list), columns=np.array(['d_spell', 'f_spell', 'champion', 'side', 'role', 'assists', 'damage_objectives', 'damage_building', 'damage_turrets', 'deaths', 
    'gold_earned', 'kda', 'kills', 'level', 'time_cc', 'damage_total' , 'damage_taken', 'total_minions_killed', 'turret_kills', 'vision_score', 'result']))

    data = implement_data_dragon(data, api_key)


    data.to_csv('2match.csv', index=True)
# %%
