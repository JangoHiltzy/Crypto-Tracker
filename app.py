# APP.PY
from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import requests
from bs4 import BeautifulSoup
import time
from threading import Thread
import os
import signal

# INITIALIZE THE FLASK APPLICATION
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

# INITIALIZE SOCKET.IO FOR REAL-TIME COMMUNICATION
socketio = SocketIO(app)


# FUNCTION TO FETCH CRYPTOCURRENCY DATA FROM YAHOO FINANCE
def fetch_crypto_data():
    url = "https://finance.yahoo.com/crypto/"

    # DEFINE HEADERS TO MIMIC A REAL BROWSER REQUEST
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    # LIST TO HOLD THE PARSED CRYPTOCURRENCY DATA
    crypto_data = []

    # SEND REQUEST TO THE WEBSITE
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # RAISE AN EXCEPTION FOR HTTP ERRORS

    # PARSE THE HTML CONTENT USING BEAUTIFULSOUP
    soup = BeautifulSoup(response.content, "html.parser")

    # FIND ALL TABLE ROWS THAT CONTAIN CRYPTOCURRENCY DATA
    rows = soup.find_all("tr", class_="row false yf-42jv6g")

    # ITERATE OVER EACH ROW TO EXTRACT THE REQUIRED DATA
    for row in rows:
        columns = row.find_all("span", class_="yf-42jv6g")
        img_tag = row.find("img", class_="yf-ravs5v logo stacked")
        long_name_tag = row.find("span", class_="yf-ravs5v longName")

        # CHECK IF THE REQUIRED DATA IS PRESENT IN THE ROW
        if len(columns) >= 4 and img_tag and long_name_tag:
            logo_url = img_tag.get("src", "")  # EXTRACT LOGO URL
            name = long_name_tag.text.strip()  # EXTRACT CRYPTOCURRENCY NAME
            price = columns[1].text.strip().split()[0]  # EXTRACT PRICE
            change = columns[2].text.strip()  # EXTRACT PRICE CHANGE
            change_percent = columns[3].text.strip()  # EXTRACT CHANGE PERCENTAGE
            market_cap = columns[5].text.strip().split()[0]  # EXTRACT MARKET CAP
            circulating_supply = (
                columns[9].text.strip().split()[0]
            )  # EXTRACT CIRCULATING SUPPLY

            # ADD THE EXTRACTED DATA TO THE LIST
            crypto_data.append(
                (
                    name,
                    price,
                    change,
                    change_percent,
                    logo_url,
                    market_cap,
                    circulating_supply,
                )
            )

    # RETURN THE LIST OF CRYPTOCURRENCY DATA
    return crypto_data


# FUNCTION TO CONTINUOUSLY FETCH AND EMIT UPDATED DATA TO CONNECTED CLIENTS
def data_update_thread():
    while True:
        data = fetch_crypto_data()  # FETCH LATEST CRYPTOCURRENCY DATA
        socketio.emit("update_data", data)  # EMIT THE DATA TO ALL CONNECTED CLIENTS
        time.sleep(30)  # WAIT FOR 30 SECONDS BEFORE FETCHING AGAIN


# ROUTE FOR THE HOME PAGE
@app.route("/")
def index():
    return render_template("index.html")  # RENDER THE INDEX.HTML TEMPLATE


# ROUTE TO RESTART THE SERVER
@app.route("/restart")
def restart():
    """Endpoint to restart the server"""
    os.kill(os.getpid(), signal.SIGINT)  # SEND SIGINT TO RESTART THE SERVER
    return redirect(url_for("index"))  # REDIRECT TO THE HOME PAGE


# HANDLE CLIENT CONNECTIONS TO SOCKET.IO
@socketio.on("connect")
def handle_connect():
    Thread(target=data_update_thread).start()  # START THE DATA UPDATE THREAD


# RUN THE FLASK APPLICATION
if __name__ == "__main__":
    socketio.run(app)  # RUN THE APP WITH SOCKET.IO
