import requests
import json
while 1:
    username = input("What is your username")
    uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/" +username).json()
    print(uuid["id"])
    data = requests.get("https://api.hypixel.net/player?key=53c394a2-94ee-4549-aafd-5e8aa1227188&uuid="+uuid["id"]).json()
    skywarsWins = data["player"]["stats"]["SkyWars"]["wins"]
    bedwarsWins = data["player"]["stats"]["Bedwars"]["wins_bedwars"]
    print("You have this many skywars wins:" + str(skywarsWins))
    print("You have this many bedwars wins:" + str(bedwarsWins)) 
    print("Your stupid!")