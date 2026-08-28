from flask import Flask, render_template, redirect, request, session
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# =========================
# CONFIGURATION
# =========================

app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

DISCORD_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI",
    "http://127.0.0.1:5000/callback"
)

DISCORD_API = "https://discord.com/api"


# =========================
# HOME / DASHBOARD
# =========================

@app.route("/")
def home():
    user = session.get("user")

    return render_template(
        "index.html",
        user=user
    )


# =========================
# DISCORD LOGIN
# =========================

@app.route("/login")
def login():

    discord_url = (
        f"{DISCORD_API}/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20guilds"
    )

    return redirect(discord_url)


# =========================
# DISCORD CALLBACK
# =========================

@app.route("/callback")
def callback():

    code = request.args.get("code")

    if not code:
        return "Discord login failed.", 400

    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI
    }

    token_response = requests.post(
        f"{DISCORD_API}/oauth2/token",
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if token_response.status_code != 200:
        print("Discord token error:", token_response.text)
        return "Failed to authenticate with Discord.", 400

    token_data = token_response.json()

    access_token = token_data.get("access_token")

    if not access_token:
        return "Discord did not provide an access token.", 400


    # =========================
    # GET DISCORD USER
    # =========================

    user_response = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    if user_response.status_code != 200:
        print("Discord user error:", user_response.text)
        return "Failed to get Discord user.", 400

    user = user_response.json()


    # =========================
    # SAVE USER TO SESSION
    # =========================

    session["user"] = user
    session["access_token"] = access_token


    # =========================
    # DEBUG
    # =========================

    print("Discord user logged in:")
    print("Username:", user.get("username"))
    print("Display name:", user.get("global_name"))
    print("User ID:", user.get("id"))


    return redirect("/")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# MODERATION
# =========================

@app.route("/moderation")
def moderation():

    user = session.get("user")

    return render_template(
        "moderation.html",
        user=user
    )


# =========================
# TICKETS
# =========================

@app.route("/tickets")
def tickets():

    user = session.get("user")

    return render_template(
        "tickets.html",
        user=user
    )


# =========================
# GIVEAWAYS
# =========================

@app.route("/giveaways")
def giveaways():

    user = session.get("user")

    return render_template(
        "giveaways.html",
        user=user
    )


# =========================
# SETTINGS
# =========================

@app.route("/settings")
def settings():

    user = session.get("user")

    return render_template(
        "settings.html",
        user=user
    )


# =========================
# RUN WEBSITE
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )