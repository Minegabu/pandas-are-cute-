'''
import requests
import json
import asyncio
from operator import itemgetter
import base64
from flask import Flask,render_template,g,request,redirect,url_for,send_from_directory,flash
import sqlite3
DATABASE = "Pandas-are-cute.db"
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

uuid123123 = "f95ceea60a084921a25b22bc726fafaa"
uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/lilycraft132").json()

print(uuid["id"])
profiles1 = requests.get("https://api.hypixel.net/player?key=e84267a6-e22c-4f9d-8e5d-7e162e6dc79b&uuid="+uuid["id"]).json()
profiles2 = requests.get("https://api.hypixel.net/skyblock/profiles?key=e84267a6-e22c-4f9d-8e5d-7e162e6dc79b&uuid="+uuid["id"]).json()
skilldata = requests.get("https://api.hypixel.net/resources/skyblock/skills").json()
profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
skills = profiles2["profiles"][0]['members'][uuid["id"]]["dungeons"]
def compute(skillxp):
    try:
        skills = requests.get("https://api.hypixel.net/resources/skyblock/skills").json()
        levels = skills["collections"]["FARMING"]["levels"]
        farmingtotal = 1000000
        sorted = [item for item in levels if item["totalExpRequired"] < skillxp] 
        nextlevel = [item for item in levels if item["totalExpRequired"] > skillxp] 
        max = sorted[-1]["level"]
        exptonextlevel = sorted[-1]['totalExpRequired']-sorted[max-2]["totalExpRequired"]
        exptotalnextlevel = skillxp-sorted[53]["totalExpRequired"]
        nextlevel = exptotalnextlevel/exptonextlevel
        return(round(nextlevel+max,2))
    except:
        sorted = [item for item in levels if item["totalExpRequired"] > skillxp] 
        max = sorted[-1]["level"]
        return(max)
data1 = requests.get("https://api.hypixel.net/skyblock/profile?key=e84267a6-e22c-4f9d-8e5d-7e162e6dc79b3&profile="+profliedata).json()
farmingtotal =  profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_farming"]
miningtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_mining"]
enchantingtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_enchanting"]
alchemytotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_alchemy"]
combattotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_combat"]
tamingtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_taming"]
fishingtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_fishing"]
foragingtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_foraging"]
mininglevel = compute(miningtotal)
print(mininglevel)
enchantinglevel = compute(enchantingtotal)
alchemylevel = compute(alchemytotal)
combatlevel = compute(combattotal)
taminglevel = compute(tamingtotal)
fishinglevel = compute(fishingtotal)
foraginglevel = compute(foragingtotal)
skindata = requests.get("https://sessionserver.mojang.com/session/minecraft/profile/"+uuid["id"]).json()
skinbase64 = skindata["properties"][-1]
#base64_skin = skinbase64["value"]_bytes.decode('ascii')
#skin = skinbase64["textures"]["SKIN"]["url"]
print(skinbase64)
skin = base64.b64decode(skinbase64["value"])
print(skin)
print(skin[3])


a="banana"

for i in range(1,4):
    globals()[ a+str(i)]=i

print(banana1)
print(banana2)
print(banana3)
'''
list1 = ['g','e','e','k', 's']  
print(",".join(list1)) 

