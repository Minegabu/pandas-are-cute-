import requests
import json
uuid123123 = "f95ceea60a084921a25b22bc726fafaa"
uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/lilycraft132").json()
print(uuid["id"])
profiles1 = requests.get("https://api.hypixel.net/player?key=9d49337e-bf1c-4825-84e4-71c529e778a3&uuid="+uuid["id"]).json()
profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
print(profliedata)
data1 = requests.get("https://api.hypixel.net/skyblock/profile?key=9d49337e-bf1c-4825-84e4-71c529e778a3&profile="+profliedata).json()
print(data1["profile"]["members"]["f95ceea60a084921a25b22bc726fafaa"]["coin_purse"])
print(data1["profile"]["banking"]["balance"])
print("😂") 
