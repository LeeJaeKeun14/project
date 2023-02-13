import requests
import pandas as pd
import numpy as np
from datetime import datetime

def make_time(ls, start_point, end_point):
    df = pd.DataFrame(ls)
    df["seconds"] = df.time.apply(lambda x: datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x[11:13]), int(x[14:16]), int(x[17:19]), int(x[20:23]) * 1000))
    df = df[(df.seconds > start_point) & (df.seconds < end_point)]
    df.seconds = df.seconds - start_point
    df.seconds = df.seconds.apply(lambda x: x.seconds)
    return df
    
def make_line(df, name):
    line = []
    a = df.drop_duplicates("seconds")[:1].reset_index()
    a_num, a_x, a_y, a_r = a.seconds[0], a.x[0], a.y[0], a.r[0]

    for i in df.drop_duplicates("seconds")[1:].itertuples():
        b_num, b_x, b_y, b_r = i.seconds, i.x, i.y, i.r

        x_points = np.linspace(a_x, b_x, b_num - a_num)
        y_points = np.linspace(a_y, b_y, b_num - a_num)
        r_points = np.linspace(a_r, b_r, b_num - a_num)
        for n in range(b_num - a_num):
            line.append({
                "match_number" : match_name,
                "name" : name,
                "team" : name,
                "x" : x_points[n],
                "y" : y_points[n],
                "win" : False,
                "dead" : False,
                "view_dead" : True,
                "seconds" : n+a_num,
                "r" : r_points[n],
                "state" : name
            })
        a_num, a_x, a_y, a_r = b_num, b_x, b_y, b_r

    for i in range(a_num, total_time+5):
        line.append({
            "match_number" : match_name,
            "name" : name,
            "team" : name,
            "x" : a_x,
            "y" : a_y,
            "seconds" : i,
            "win" : False,
            "dead" : False,
            "view_dead" : True,
            "r" : a_r,
            "state" : name
        })
    return line

# read matchs
match_df = pd.read_csv("./data/matchs.csv")
url = match_df[(match_df.player_count > 60) & (match_df.map_name == "Erangel (Remastered)")]
urls = list(match_df[(match_df.player_count > 60) & (match_df.map_name == "Erangel (Remastered)")].reset_index(drop = True).telemetry_link)

for match_number, url in enumerate(urls[:20]):
    print(match_number)
    r = requests.get(url)
    json_r = r.json()

    event_dict = {}
    event_t = {}

    start_time = 0
    end_time = 0

    move_ls = []
    safety_ls =[]
    poison_ls = []
    red_ls = []
    for i in json_r:
        key = [j for j in i.keys()][0]
        try:
            if event_dict[key]:
                event_dict[key] += 1
        except:
            event_dict[key] = 1
        
        if key == "gameState":
            safety_ls.append({
                "x" : i["gameState"]["safetyZonePosition"]["x"],
                "y" : i["gameState"]["safetyZonePosition"]["y"],
                "r" : i["gameState"]["safetyZoneRadius"],
                "time" : i["_D"]
            })
            poison_ls.append({
                "x" : i["gameState"]["poisonGasWarningPosition"]["x"],
                "y" : i["gameState"]["poisonGasWarningPosition"]["y"],
                "r" : i["gameState"]["poisonGasWarningRadius"],
                "time" : i["_D"]
            })
            red_ls.append({
                "x" : i["gameState"]["redZonePosition"]["x"],
                "y" : i["gameState"]["redZonePosition"]["y"],
                "r" : i["gameState"]["redZoneRadius"],
                "time" : i["_D"]
            })
        
        key = i["_T"]
        try:
            if event_t[key]:
                event_t[key] += 1
        except:
            event_t[key] = 1
        
        if i["_T"] == "LogMatchStart":
            start_time = i["_D"]
            
        if i["_T"] == "LogMatchEnd":
            end_time = i["_D"]
            
        try:
            move_ls.append({
                "name" : i["character"]["name"].split("_")[1],
                "team" : i["character"]["name"].split("_")[0],
                "health" : i["character"]["health"],
                "location_x" : i["character"]["location"]["x"],
                "location_y" : i["character"]["location"]["y"],
                "location_z" : i["character"]["location"]["z"],
                "ranking" : i["character"]["ranking"],
                "time" : i["_D"]
            })
        except:
            continue

    move_df = pd.DataFrame(move_ls)
    
    move_df["team"] = move_df["team"].astype("str")
    move_df["win"] = False
    winner = move_df[move_df.ranking == 1].team.unique()[0]
    move_df["win"][move_df.team == winner] = True
    
    move_df["seconds"] = move_df.time.apply(lambda x: datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x[11:13]), int(x[14:16]), int(x[17:19]), int(x[20:23]) * 1000))

    x = start_time
    start_point = datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x[11:13]), int(x[14:16]), int(x[17:19]), int(x[20:23]) * 1000)
    match_name = str(start_point.year) + "/" + str(start_point.month) + "/" + str(start_point.day) + " " + str(start_point.hour)+":" + str(start_point.minute)
    x = end_time
    end_point = datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x[11:13]), int(x[14:16]), int(x[17:19]), int(x[20:23]) * 1000)
    total_time = (end_point - start_point).seconds

    move_df = move_df[(move_df.seconds > start_point) & (move_df.seconds < end_point)]
    move_df.seconds = move_df.seconds - start_point
    move_df.seconds = move_df.seconds.apply(lambda x: x.seconds)

    players = list(move_df.name.unique())

    player_move = []

    for player in players:
        a = move_df[move_df.name == player].drop_duplicates("seconds")[:1].reset_index()

        name = a.name[0]
        team = a.team[0]
        win = a.win[0]
        a_num = a.seconds[0]
        a_health = a.health[0]
        a_x = a.location_x[0]
        a_y = a.location_y[0]

        for i in move_df[move_df.name == player].drop_duplicates("seconds")[1:].itertuples():
            b_num = i.seconds
            b_health = i.health
            b_x = i.location_x
            b_y = i.location_y
            
            x_points = np.linspace(a_x, b_x, b_num - a_num)
            y_points = np.linspace(a_y, b_y, b_num - a_num)
            for n in range(b_num - a_num):
                player_move.append({
                    "match_number" : match_name,
                    "name" : name,
                    "team" : team,
                    "x" : x_points[n],
                    "y" : y_points[n],
                    "seconds" : n+a_num,
                    "win" : win,
                    "dead" : False,
                    "view_dead" : True,
                    "r" : 0,
                    "state" : "player"
                })
            
            a_num = b_num
            a_health = b_health
            a_x = b_x
            a_y = b_y

        dead_time = 0
        for i in range(a_num, total_time+5):
            
            dead = True
            view_dead = True
            if win == True and a_health > 0:
                dead = False
            if dead == True and dead_time > 19:
                view_dead = False
            player_move.append({
                "match_number" : match_name,
                "name" : name,
                "team" : team,
                "x" : a_x,
                "y" : a_y,
                "seconds" : i,
                "win" : win,
                "dead" : dead,
                "view_dead" : view_dead,
                "r" : 0,
                "state" : "player"
            })
            dead_time += 1
    
    safety_df = make_time(safety_ls, start_point, end_point)
    poison_df = make_time(poison_ls, start_point, end_point)
    red_df = make_time(red_ls, start_point, end_point)

    safety_line = make_line(safety_df, "safety")
    poison_line = make_line(poison_df, "poison")
    red_line = make_line(red_df, "red")
    
    safety_line2 = make_line(safety_df, "safety_a")
    poison_line2 = make_line(poison_df, "poison_a")
    red_line2 = make_line(red_df, "red_a")

    # make file
    pd.DataFrame(player_move + safety_line + poison_line + red_line + safety_line2 + poison_line2 + red_line2).to_csv(f"./data/move_datas/move/{match_number}.csv", index=False)

# join 20 file
ls = []
for i in range(20):
    ls.append(pd.read_csv(f"./data/move_datas/move/{i}.csv"))
pd.concat(ls).to_csv("./data/move_datas/total_move_20.csv", index=False)
