import cgi
from flask import Flask,render_template,g,request,redirect,url_for,send_from_directory,flash
import requests
import json
import sqlite3
app = Flask(__name__)
form = cgi.FieldStorage()
searchterm =  form.getvalue('searchbox')
DATABASE = "Pandas-are-cute.db"
key = "e84267a6-e22c-4f9d-8e5d-7e162e6dc79b"




def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db




def decimal_str(x: float, decimals: int = 10) -> str:
    return format(x, f".{decimals}f").lstrip().rstrip('0')



@app.route('/')
def home():
    return render_template("home.html")

@app.route('/data',methods=["get","POST"])
def add():
    if request.method == "POST":
        print(request.form.get("yess"))
        cursor = get_db().cursor()
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+request.form.get("yess")).json()
        profiles1 = requests.get("https://api.hypixel.net/player?key=" + key + "&uuid="+uuid["id"]).json()
        profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
        data = requests.get("https://api.hypixel.net/skyblock/profile?key="+ key + "&profile="+profliedata).json()
        purse = data["profile"]["members"][uuid["id"]]["coin_purse"]
        bank = data["profile"]["banking"]["balance"]
        sql = "INSERT INTO data (Purse,Bank,UUID) VALUES(?,?,?)"
        cursor.execute(sql,(purse,bank,uuid["id"]))
        get_db().commit()
        return redirect('/contents') 

@app.route('/contents',methods=["get"])
def data():
    cursor = get_db().cursor()
    sql = "SELECT max(Purse), max(Bank) FROM data"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("contents.html",results=results)

 


if __name__ == "__main__":
    app.run(debug=True)