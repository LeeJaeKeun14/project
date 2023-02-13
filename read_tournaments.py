import requests
import pandas as pd

# api_key read
with open("_api_key.txt", "r") as f:
    api_key = f.read()
    
# make header
header = {
  "Authorization": api_key,
  "Accept": "application/vnd.api+json"
}

# read tournaments ids
url = "https://api.pubg.com/tournaments"

r = requests.get(url, headers=header)
json_r = r.json()

ls = []
for i in json_r["data"]:
    ls.append({
        "tournament_id" : i["id"],
        "time" : i["attributes"]["createdAt"]
    })

# save tournaments_ids
tournament_df = pd.DataFrame(ls)
tournament_df.to_csv("./data/tournaments.csv", index=False)
