import pandas as pd

from chicken_dinner.models.tournament import Tournament
from chicken_dinner.pubgapi import PUBG
from chicken_dinner.pubgapi import PUBGCore

# api_key read
with open("_api_key.txt", "r") as f:
    api_key = f.read()

# use PUBGCore
PUBG = PUBG(api_key=api_key, shard='pc-tournament', gzip=True)
PUBGCore = PUBGCore(api_key=api_key, shard='pc-tournament', gzip=True)

# read tournaments_ids
tournaments_df = pd.read_csv("./data/tournaments.csv")

# One tournament has many matchs
# One match has many rosters
# A roster means team 
match_ls = []
roster_ls = []

for num, tor in enumerate(tournaments_df.itertuples()):
    print(num)
    
    # read matchs in tournament
    matchlist = PUBG.tournament(tor.tournament_id).match_ids
    for i in matchlist:
        match = PUBG.match(i)
        
        # find winner team and winner player
        won = ""
        won_players = []
        # match player count
        count = 0
        
        # read rosters in match
        for roster in match.rosters:
            # winner find
            if roster.stats["rank"] == 1:
                won = roster.participants[0].name.split("_")[0]
                for participant in roster.participants:
                    won_players.append(participant.name)
            # read players in orster
            for participant in roster.participants:
                count += 1
                
                # observer name error
                try:
                    team_name = participant.name.split("_")[0]
                    player_name = participant.name.split("_")[1]
                except:
                    team_name = ""
                    player_name = participant.name
                    
                roster_dict = {
                    "match_id" : match.id,
                    
                    "team_rank" : roster.stats["rank"],
                    "team_name" : team_name,
                    "player_id" : participant.name,
                    "player_name" : player_name
                }
                roster_dict.update(participant.stats)
                roster_dict["player_id"] = participant.name
                roster_ls.append(
                    roster_dict
                )

        # error Tiger_Main -> Taego
        try: 
            map_name = match.map_name
        except:
            map_name = match.data["attributes"]["mapName"]
        
        match_ls.append({
            "country" : tor.tournament_id.split("-")[0],
            "tournament_id" : tor.tournament_id,
            "match_id" : match.id,
            "created_at" : match.created_at,
            "game_mode" : match.game_mode,
            "map_name" : map_name,
            "duration" : match.duration,
            # statistic
            "team_count" : len(match.rosters),
            "player_count" : count,
            "win_team" : won,
            "win_players" : ", ".join(won_players),
            
            "telemetry_link" : match.telemetry_url
        })

# save match and roster
match_df = pd.DataFrame(match_ls)
roster_df = pd.DataFrame(roster_ls)

match_df.to_csv("./data/matchs.csv", index=False)
roster_df.to_csv("./data/rosters.csv", index=False)