# get players stats on skyblock
# all the imports
import re
from tabulate import tabulate
import cgi
from flask import Flask, render_template, g, request, redirect, url_for, send_from_directory, flash, session
import requests
import json
import sqlite3
import math
import base64
import urllib
# for making it easy to read
millnames = ['', ' K', ' M', ' B', ' T']
app = Flask(__name__)
form = cgi.FieldStorage()
searchterm = form.getvalue('searchbox')
# database
DATABASE = "Pandas-are-cute.db"
# api key
key = "a98a685a-9633-421e-8c4b-ae129568f494"
app.secret_key = b'_5# y2L"F4Q8z\n\xec]/'

import base64
import urllib.request
import json



 
# connect the database
def get_db():
    db = getattr(g,  '_database',  None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# turn the numbers into readable numbers that people can understand
def millify(n):
    n = float(n)
    millidx = max(0, min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    return '{:.0f}{}'.format(n / 10**(3 * millidx),  millnames[millidx])


# the homepage function
@app.route('/')
def home():
    return render_template("home.html")


# addfriends route
@app.route('/addfriends')
def friendadd():
    return render_template("friends.html", name = session['ign'], profile = session['cutename'])


# function to get the skill xp and turn it into level and percent to next level
def compute(skill):
    skillname = "experience_skill_" + skill
    profiles2 = requests.get("https://api.hypixel.net/skyblock/profiles?key="+key+"&uuid="+session['uuid']).json()
    try:
        skilltotal = profiles2["profiles"][-1]["members"][session['uuid']][skillname]
    except:
        skilltotal = 23212
    try:
        # get the skill data
        skills = requests.get("https://api.hypixel.net/resources/skyblock/skills").json()
        # turn it into the right list of dictonarys
        levels = skills["collections"]["FARMING"]["levels"]
        # sort through the list of dictonarys
        sorted = [item for item in levels if item["totalExpRequired"] < skilltotal]
        # get the level
        max = sorted[-1]["level"]
        # get the exp to next level
        exptonextlevel = sorted[-1]['totalExpRequired']-sorted[max-2]["totalExpRequired"]
        # get the amount of exp already to next level
        exptotalnextlevel = skilltotal-sorted[max-1]["totalExpRequired"]
        # percent to next level
        nextlevel = exptotalnextlevel/exptonextlevel
        # if you are over the level cap
        if nextlevel > 1:
            nextlevel = 0
        return(round(nextlevel+max, 2))
    except:
        # if you are over 50 on a skill that caps out at 50
        sorted = [item for item in levels if item["totalExpRequired"] > skilltotal]
        max = sorted[-1]["level"]
        return(max)

def f_compute(skill):
    frienduuid = session['fuuid']
    skillname1 = "experience_skill_" + skill
    profiles3 = requests.get("https://api.hypixel.net/skyblock/profiles?key="+key+"&uuid="+frienduuid).json()
    try:
        skilltotal = profiles3["profiles"][-1]["members"][frienduuid][skillname1]
    except:
        skilltotal = 23132
    try:
        # get the skill data
        skills = requests.get("https://api.hypixel.net/resources/skyblock/skills").json()
        # turn it into the right list of dictonarys
        levels = skills["collections"]["FARMING"]["levels"]
        # sort through the list of dictonarys
        sorted = [item for item in levels if item["totalExpRequired"] < skilltotal]
        # get the level
        max = sorted[-1]["level"]
        # get the exp to next level
        exptonextlevel = sorted[-1]['totalExpRequired']-sorted[max-2]["totalExpRequired"]
        # get the amount of exp already to next level
        exptotalnextlevel = skilltotal-sorted[max-1]["totalExpRequired"]
        # percent to next level
        nextlevel = exptotalnextlevel/exptonextlevel
        # if you are over the level cap
        if nextlevel > 1:
            nextlevel = 0
        return(round(nextlevel+max, 2))
    except:
        # if you are over 50 on a skill that caps out at 50
        sorted = [item for item in levels if item["totalExpRequired"] > skilltotal]
        max = sorted[-1]["level"]
        return(max)

@app.route('/pursedata', methods=["get","POST"])
def display():
    cursor = get_db().cursor()
    sql = "SELECT * FROM data WHERE UUID='" + session['uuid'] + "'"
    cursor.execute(sql)
    results =  cursor.fetchall()
    return render_template("contents.html", name=session['ign'], results=results, profile=session['cutename'], skin=session['skin'])

# adding all the data for the player
@app.route('/adddata', methods=["get", "POST"])
def add():
    if request.method == "POST":
        #get the username
        try:
            ign = request.form.get("yess")
            session['ign'] = ign
            uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+ign).json()
            session['uuid'] = uuid['id']
        except:
            flash("This username does not exist")
            return redirect('/')
        # getting their user id
        cursor = get_db().cursor()
        skin = "https://crafatar.com/avatars/"+session['uuid']
        session['skin'] = skin
        # getting the profile data
        try:
            profiles1 = requests.get("https://api.hypixel.net/player?key=" + key + "&uuid="+uuid["id"]).json()
            profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
            # finding profile name
            cutename = profiles1["player"]["stats"]["SkyBlock"]["profiles"][profliedata]["cute_name"]
            session['cutename'] = cutename
            # getting all the relevant data
            data = requests.get("https://api.hypixel.net/skyblock/profile?key="+ key + "&profile="+profliedata).json()
            purse = millify(round(data["profile"]["members"][uuid["id"]]["coin_purse"]))
        except:
            flash("Player has not played skyblock")
            return redirect('/')
        try:
            bank = millify(round(data["profile"]["banking"]["balance"]))
        except:
            bank = 0
        # converting it into level
        mininglevel = compute("mining")
        enchantinglevel = compute("enchanting")
        alchemylevel = compute("alchemy")
        combatlevel = compute("combat")
        taminglevel = compute("taming")
        fishinglevel = compute("fishing")
        foraginglevel = compute("foraging")
        farminglevel = compute("farming")
        if alchemylevel > 50:
            alchemylevel = 50
        if taminglevel > 50:
            taminglevel = 50
        if foraginglevel > 50:
            foraginglevel = 50

        # some saftey checks
        # updating the relevant data for the user
        cursor = get_db().cursor()
        sql = "SELECT id FROM data WHERE uuid='" +uuid["id"]+ "'"
        cursor.execute(sql)
        u_id = str(cursor.fetchone())
        u_id = re.sub('[^0-9]',  '',  u_id)
        # incase the user does not exist
        if len(u_id) == 0:
            cursor.execute("INSERT INTO data (uuid, purse, bank, farming, taming, mining, enchanting, combat, fishing, foraging, alchemy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (uuid["id"], purse, bank, farminglevel, taminglevel, mininglevel, enchantinglevel, combatlevel, fishinglevel, foraginglevel, alchemylevel))
        else:
            cursor.execute("""UPDATE data SET purse=? WHERE uuid=?""", (purse, uuid["id"]))
            cursor.execute("""UPDATE data SET bank=? WHERE uuid=?""", (bank, uuid["id"]))
            cursor.execute("""UPDATE data SET farming=? WHERE uuid=?""", (farminglevel, uuid["id"]))
            cursor.execute("""UPDATE data SET taming=? WHERE uuid=?""", (taminglevel, uuid["id"]))
            cursor.execute("""UPDATE data SET mining=? WHERE uuid=?""", (mininglevel, uuid["id"]))
            cursor.execute("""UPDATE data SET enchanting=? WHERE uuid=?""", (enchantinglevel, uuid["id"]))
            cursor.execute("""UPDATE data SET combat=? WHERE uuid=?""", (combatlevel, uuid["id"]))
            cursor.execute("""UPDATE data SET fishing=? WHERE uuid=?""", (fishinglevel, uuid["id"]))
            cursor.execute("""UPDATE data SET foraging=? WHERE uuid=?""", (foraginglevel, uuid["id"]))
            cursor.execute("""UPDATE data SET alchemy=? WHERE uuid=?""", (alchemylevel, uuid["id"]))
            cursor.execute("""UPDATE data SET name=? WHERE uuid=?""", (ign, uuid["id"]))
        get_db().commit()
        return redirect('/pursedata')


@app.route('/skilldata', methods=["get", "POST"])
def skill():
    # displaying the skill data 
    cursor = get_db().cursor()
    sql = "SELECT * FROM data WHERE UUID='" + session['uuid'] + "'"
    cursor.execute(sql)
    results =  cursor.fetchall()
    return render_template("contents1.html", name=session['ign'], results=results, profile=session['cutename'], skin=session['skin'])


# adding friends
@app.route('/friends', methods=["get", "POST"])
def friend():
    if request.method == "POST":
        friend = str(request.form.get("ign1"))
        try:
            # getting the username
            # getting the friends user id
            try:    
                f_uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+friend).json()
                session['fuuid']=f_uuid['id']
            except:
                flash("This user does not exist")
                return redirect('/addfriends')
            try:
                profiles1 = requests.get("https://api.hypixel.net/player?key=" + key + "&uuid="+f_uuid["id"]).json()
            except: 
                flash("Player has no profiles")
                return render_template("friend.html")
            # getting all the relevant data
            f_profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[-1]
            f_data = requests.get("https://api.hypixel.net/skyblock/profile?key="+ key + "&profile="+f_profliedata).json()
            f_purse = millify(round(f_data["profile"]["members"][f_uuid["id"]]["coin_purse"]))
            f_bank = millify(round(f_data["profile"]["banking"]["balance"]))
            f_mininglevel = f_compute("mining")
            f_enchantinglevel = f_compute("enchanting")
            f_alchemylevel = f_compute("alchemy")
            f_combatlevel = f_compute("combat")
            f_taminglevel = f_compute("taming")
            f_fishinglevel = f_compute("fishing")
            f_foraginglevel = f_compute("foraging")
            f_farminglevel = f_compute("farming") 
            cursor = get_db().cursor()
            sql = "SELECT id FROM data WHERE uuid='" +f_uuid["id"]+ "'"
            cursor.execute(sql)
            f_id = str(cursor.fetchone())
            f_id = re.sub('[^0-9]',  '',  f_id)

            if len(f_id) == 0:
                # incase the user does not exist
                cursor.execute("INSERT INTO data (name, purse, bank, farming, taming, mining, enchanting, combat, fishing, foraging, alchemy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (f_uuid["id"], f_purse, f_bank, f_farminglevel, f_taminglevel, f_mininglevel, f_enchantinglevel, f_combatlevel, f_fishinglevel, f_foraginglevel, f_alchemylevel))
            else:
                # updating user
                cursor.execute("""UPDATE data SET bank=? WHERE uuid=?""", (f_purse, f_uuid["id"]))
                cursor.execute("""UPDATE data SET name=? WHERE uuid=?""", (friend, f_uuid["id"]))
                cursor.execute("""UPDATE data SET purse=? WHERE uuid=?""", (f_bank, f_uuid["id"]))
                cursor.execute("""UPDATE data SET farming=? WHERE uuid=?""", (f_farminglevel, f_uuid["id"]))
                cursor.execute("""UPDATE data SET taming=? WHERE uuid=?""", (f_taminglevel, f_uuid["id"]))
                cursor.execute("""UPDATE data SET mining=? WHERE uuid=?""", (f_mininglevel, f_uuid["id"]))
                cursor.execute("""UPDATE data SET enchanting=? WHERE uuid=?""", (f_enchantinglevel, f_uuid["id"]))
                cursor.execute("""UPDATE data SET combat=? WHERE uuid=?""", (f_combatlevel, f_uuid["id"]))
                cursor.execute("""UPDATE data SET fishing=? WHERE uuid=?""", (f_fishinglevel, f_uuid["id"]))
                cursor.execute("""UPDATE data SET foraging=? WHERE uuid=?""", (f_foraginglevel, f_uuid["id"]))
                cursor.execute("""UPDATE data SET alchemy=? WHERE uuid=?""", (f_alchemylevel, f_uuid["id"]))
            sql2 = "SELECT id FROM data WHERE uuid='" +session['uuid'] + "'"
            cursor.execute(sql2)
            u_id = str(cursor.fetchone())
            u_id = re.sub('[^0-9]',  '',  u_id)
            # inserting friend
            cursor.execute("INSERT INTO friends (id, friend_id) VALUES (?, ?)", (u_id, f_id))
            get_db().commit()

            return redirect('/displayfriends') 
        except:
            flash("That username does not exist")


@app.route('/displayfriends', methods=["get"])
def friends():
            try:
                # get friends
                cursor = get_db().cursor()
                # finding the id 
                sql = "SELECT id FROM data WHERE uuid='" + session['uuid'] + "'"
                cursor.execute(sql)
                u_id = str(cursor.fetchone())
                u_id = re.sub('[^0-9]',  '',  u_id)
                # finding the friend id
                friendsql = "SELECT friend_id FROM friends WHERE id='" +u_id+ "'"
                cursor.execute(friendsql)
                # getting the friend data
                allfriends = cursor.fetchall()
                allfriends = ''.join(str(e) for e in allfriends)
                allfriends = allfriends.replace(")", "")
                allfriends = allfriends.replace("(", "")
                allfriends = allfriends[:-1]
                s_friend = "SELECT name, purse, bank, farming, taming, mining, enchanting, combat, fishing, foraging, alchemy FROM data WHERE id in ("+allfriends+", "+u_id+")"
                cursor.execute(s_friend)
                results = cursor.fetchall()
                return render_template("friends1.html",  results=results,  name = session['ign'] , profile = session['cutename'],)
            except:
                flash("You have no friends L")
                return redirect('/addfriends')


if __name__ == "__main__":
    app.run(debug=True)
