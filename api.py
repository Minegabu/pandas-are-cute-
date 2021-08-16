# get players stats on skyblock
# all the imports
import re
from tabulate import tabulate
import cgi
from flask import Flask, render_template, g, request, redirect, url_for, send_from_directory, flash
import requests
import json
import sqlite3
import math


# for making it easy to read
millnames = ['', ' K', ' M', ' B', ' T']
app = Flask(__name__)
form = cgi.FieldStorage()
searchterm = form.getvalue('searchbox')
# database
DATABASE = "Pandas-are-cute.db"
# api key
key = "e84267a6-e22c-4f9d-8e5d-7e162e6dc79b"
app.secret_key = b'_5# y2L"F4Q8z\n\xec]/'
global click_num
click_num = 1
global order
order = "name"
global order_of_sort
order_of_sort = "ASC"


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
    return render_template("friends.html")


# function to get the skill xp and turn it into level and percent to next level
def compute(skillxp):
    try:
        # get the skill data 
        skills = requests.get("https://api.hypixel.net/resources/skyblock/skills").json()
        # turn it into the right list of dictonarys
        levels = skills["collections"]["FARMING"]["levels"]
        # sort through the list of dictonarys
        sorted = [item for item in levels if item["totalExpRequired"] < skillxp] 
        # get the level
        max = sorted[-1]["level"]
        # get the exp to next level
        exptonextlevel = sorted[-1]['totalExpRequired']-sorted[max-2]["totalExpRequired"]
        # get the amount of exp already to next level
        exptotalnextlevel = skillxp-sorted[max-1]["totalExpRequired"]
        # percent to next level
        nextlevel = exptotalnextlevel/exptonextlevel
        # if you are over the level cap 
        if nextlevel > 1:
            nextlevel = 0
        return(round(nextlevel+max, 2))
    except:
        # if you are over 50 on a skill that caps out at 50
        sorted = [item for item in levels if item["totalExpRequired"] > skillxp] 
        max = sorted[-1]["level"]
        return(max)


# adding all the data for the player
@app.route('/pursedata', methods=["get", "POST"])
def add():
    if request.method == "POST":
        global ign
        ign = request.form.get("yess")
        # getting their ingamename
        try:
            global uuid
            uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+ign).json()
            ign1 = request.form.get("yess")
        except:
            flash("Player does not exist")
            return redirect('/')

        # getting their user id
        global uuidglobal
        uuidglobal = uuid["id"]
        cursor = get_db().cursor()
        # getting the profile data
        try:
            profiles1 = requests.get("https://api.hypixel.net/player?key=" + key + "&uuid="+uuid["id"]).json()
            profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
            global cutename
            # finding profile name
            cutename = profiles1["player"]["stats"]["SkyBlock"]["profiles"][profliedata]["cute_name"]
            # getting all the relevant data
            data = requests.get("https://api.hypixel.net/skyblock/profile?key="+ key + "&profile="+profliedata).json()
            profiles2 = requests.get("https://api.hypixel.net/skyblock/profiles?key="+key+"&uuid="+uuid["id"]).json()
            purse = millify(round(data["profile"]["members"][uuid["id"]]["coin_purse"]))
        except:
            flash("Player has not played skyblock")
            return redirect('/')
        try:
            bank = millify(round(data["profile"]["banking"]["balance"]))
        except:
            flash("Banking api off")
            return redirect('/')
        # finding the total skill xp
        farmingtotal =  profiles2["profiles"][-1]["members"][uuid["id"]]["experience_skill_farming"]
        try:
            miningtotal = profiles2["profiles"][-1]["members"][uuid["id"]]["experience_skill_mining"]
        except:
            miningtotal = 100
        try:
            enchantingtotal = profiles2["profiles"][-1]["members"][uuid["id"]]["experience_skill_enchanting"]
        except:
            enchantingtotal = 100
        try:
            alchemytotal = profiles2["profiles"][-1]["members"][uuid["id"]]["experience_skill_alchemy"]
        except:
            alchemytotal = 100
        try:
            combattotal = profiles2["profiles"][-1]["members"][uuid["id"]]["experience_skill_combat"]
        except:
            combattotal = 100
        try:
            tamingtotal = profiles2["profiles"][-1]["members"][uuid["id"]]["experience_skill_taming"]
        except:
            tamingtotal = 100
        try:
            fishingtotal = profiles2["profiles"][-1]["members"][uuid["id"]]["experience_skill_fishing"]
        except:
            fishingtotal = 100
        try:
            foragingtotal = profiles2["profiles"][-1]["members"][uuid["id"]]["experience_skill_foraging"]
        except:
            foragingtotal = 100
        # converting it into level
        mininglevel = compute(miningtotal)
        enchantinglevel = compute(enchantingtotal)
        alchemylevel = compute(alchemytotal)
        combatlevel = compute(combattotal)
        taminglevel = compute(tamingtotal)
        fishinglevel = compute(fishingtotal)
        foraginglevel = compute(foragingtotal)
        farminglevel = compute(farmingtotal)
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
        sql = "SELECT * FROM data WHERE UUID='" + uuid["id"] +"'"
        cursor.execute(sql)    
        results = cursor.fetchall()
        return render_template("contents.html", results=results,  name=ign, profile=cutename)
    else:
        # when it is not post
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+ign).json()
        cursor = get_db().cursor()
        sql = "SELECT * FROM data WHERE UUID ='" + uuid["id"] +"'"
        sql2 = "SELECT * FROM data WHERE UUID= '" + uuid["id"] + "'"
        cursor.execute(sql)
        cursor.execute(sql2)
        results = cursor.fetchall()
        return render_template("contents.html", results=results, name=ign, profile=cutename)


@app.route('/button')
def button():
    # way to sort the friends list 
    global order
    global click_num
    global order_of_sort
    click_num = click_num + 1
    if click_num == 2:
        order = "purse"
        flash("Sorted by purse")
        order_of_sort = "DESC"
    elif click_num == 3:
        order = "bank"
        flash("Sorted by bank")
    else:
        click_num = 0
        order = "name" 
        order_of_sort = "ASC"
    return redirect('/displayfriends')


@app.route('/skilldata', methods=["get", "POST"])
def skill():
    # displaying the skill data 
    global uuidglobal
    cursor = get_db().cursor()
    sql = "SELECT * FROM data WHERE UUID='" + uuidglobal + "'"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("contents1.html", name=ign, results=results, profile=cutename)


# adding friends
@app.route('/friends', methods=["get", "POST"])
def friend():
    if request.method == "POST":
        friend = str(request.form.get("ign1"))
        try:
            
            # getting the username
            # getting the friends user id
            f_uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+friend).json()
            try:
                profiles1 = requests.get("https://api.hypixel.net/player?key=" + key + "&uuid="+f_uuid["id"]).json()
            except:
                flash("Player has no profiles")
                return render_template("friend.html")
            # getting all the relevant data
            f_profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[-1]
            f_data = requests.get("https://api.hypixel.net/skyblock/profile?key="+ key + "&profile="+f_profliedata).json()
            f_profiles2 = requests.get("https://api.hypixel.net/skyblock/profiles?key="+key+"&uuid="+f_uuid["id"]).json()
            f_purse = millify(round(f_data["profile"]["members"][f_uuid["id"]]["coin_purse"]))
            f_bank = millify(round(f_data["profile"]["banking"]["balance"]))
            try:
                f_miningtotal = f_profiles2["profiles"][-1]["members"][f_uuid["id"]]["experience_skill_mining"]
            except:
                f_miningtotal = 100
            try:
                f_enchantingtotal = f_profiles2["profiles"][-1]["members"][f_uuid["id"]]["experience_skill_enchanting"]
            except:
                f_enchantingtotal = 100
            try:
                f_alchemytotal = f_profiles2["profiles"][-1]["members"][f_uuid["id"]]["experience_skill_alchemy"]
            except:
                f_alchemytotal = 100
            try:
                f_combattotal = f_profiles2["profiles"][-1]["members"][f_uuid["id"]]["experience_skill_combat"]
            except:
                f_combattotal = 100 
            try:
                f_tamingtotal = f_profiles2["profiles"][-1]["members"][f_uuid["id"]]["experience_skill_taming"]
            except:
                f_tamingtotal = 100
            try:
                f_fishingtotal = f_profiles2["profiles"][-1]["members"][f_uuid["id"]]["experience_skill_fishing"]
            except:
                f_fishingtotal = 100
            try:
                f_foragingtotal = f_profiles2["profiles"][-1]["members"][f_uuid["id"]]["experience_skill_foraging"]
            except:
                f_foragingtotal = 100 
            try:
                f_farmingtotal = f_profiles2["profiles"][-1]["members"][f_uuid["id"]]["experience_skill_farming"]
            except:
                f_farmingtotal = 100
            f_mininglevel = compute(f_miningtotal)
            f_enchantinglevel = compute(f_enchantingtotal)
            f_alchemylevel = compute(f_alchemytotal)
            f_combatlevel = compute(f_combattotal)
            f_taminglevel = compute(f_tamingtotal)
            f_fishinglevel = compute(f_fishingtotal)
            f_foraginglevel = compute(f_foragingtotal)
            f_farminglevel = compute(f_farmingtotal) 

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

            sql2 = "SELECT id FROM data WHERE uuid='" +uuidglobal+ "'"
            cursor.execute(sql2)
            u_id = str(cursor.fetchone())
            u_id = re.sub('[^0-9]',  '',  u_id)
            sql1 = "SELECT user_id FROM friends WHERE user_id='"+u_id+"'"+" AND friend_id = '"+f_id+"'"
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
                friend = str(request.form.get("ign1"))
                cursor = get_db().cursor()
                # finding the id 
                sql = "SELECT id FROM data WHERE uuid='" + uuidglobal + "'"
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
                s_friend = "SELECT name, purse, bank, farming, taming, mining, enchanting, combat, fishing, foraging, alchemy FROM data WHERE id in ("+allfriends+", "+u_id+") ORDER BY "+order+" "+order_of_sort+""
                cursor.execute(s_friend)
                results = cursor.fetchall()
                return render_template("friends1.html",  results=results,  name = ign , profile =cutename, )
            except:
                flash("You have no friends L")
                return redirect('/skilldata')


if __name__ == "__main__":
    app.run(debug=True)
