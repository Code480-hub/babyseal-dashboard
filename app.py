from flask import Flask, render_template, redirect, request, session
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# =========================
# CONFIGURATION
# =========================

app.secret_key = os.getenv("FLASK_SECRET_KEY")

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

DISCORD_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI",
    "http://127.0.0.1:5000/callback"
)

DISCORD_API = "https://discord.com/api"

# Your Discord bot token is NOT needed for OAuth login.
# If you later want the dashboard to check whether the bot
# is inside a server, put your bot token in Render as:
#
# DISCORD_BOT_TOKEN=your_bot_token
#
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


# =========================
# HELPER FUNCTIONS
# =========================

def get_discord_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}"
    }


def get_user_guilds(access_token):
    """
    Get the Discord servers the logged-in user belongs to.
    """

    response = requests.get(
        f"{DISCORD_API}/users/@me/guilds",
        headers=get_discord_headers(access_token),
        timeout=10
    )

    if response.status_code != 200:
        return []

    return response.json()


def can_manage_guild(guild):
    """
    Check whether the logged-in user can manage this server.

    Discord guild permissions are returned as a bitfield.

    ADMINISTRATOR = 0x8
    MANAGE_GUILD = 0x20
    """

    try:
        permissions = int(guild.get("permissions", 0))
    except (TypeError, ValueError):
        permissions = 0

    ADMINISTRATOR = 0x8
    MANAGE_GUILD = 0x20

    return bool(
        permissions & ADMINISTRATOR
        or permissions & MANAGE_GUILD
    )


def get_bot_guild_ids():
    """
    Get the guilds that the Baby Seal bot is currently in.

    This requires DISCORD_BOT_TOKEN to be set.

    If the token isn't configured, we return None instead of
    blocking the dashboard.
    """

    if not DISCORD_BOT_TOKEN:
        return None

    response = requests.get(
        f"{DISCORD_API}/users/@me/guilds",
        headers={
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
        },
        timeout=10
    )

    if response.status_code != 200:
        return None

    try:
        guilds = response.json()
        return {str(guild["id"]) for guild in guilds}
    except (TypeError, ValueError, KeyError):
        return None


def get_manageable_guilds(access_token):
    """
    Return servers that:
    1. The user can manage.
    2. Baby Seal is in the server, when a bot token is configured.

    If no bot token is configured, all manageable servers are returned.
    """

    guilds = get_user_guilds(access_token)

    manageable = []

    bot_guild_ids = get_bot_guild_ids()

    for guild in guilds:

        if not can_manage_guild(guild):
            continue

        guild_id = str(guild.get("id"))

        # If we know which servers the bot is in,
        # only show servers where the bot is installed.
        if bot_guild_ids is not None:
            if guild_id not in bot_guild_ids:
                continue

        manageable.append(guild)

    return manageable


# =========================
# HOME / DASHBOARD
# =========================

@app.route("/")
def home():

    user = session.get("user")

    # If the user isn't logged in, show the normal homepage.
    if not user:
        return render_template(
            "index.html",
            user=None,
            guilds=[],
            selected_guild=None
        )

    access_token = session.get("access_token")

    if not access_token:
        session.clear()

        return render_template(
            "index.html",
            user=None,
            guilds=[],
            selected_guild=None
        )

    # Get servers the user can manage.
    guilds = get_manageable_guilds(access_token)

    # Get the currently selected server.
    selected_guild_id = session.get("selected_guild_id")

    selected_guild = None

    if selected_guild_id:
        for guild in guilds:
            if str(guild.get("id")) == str(selected_guild_id):
                selected_guild = guild
                break

    # If there is no selected server, automatically select
    # the first manageable server.
    if selected_guild is None and guilds:
        selected_guild = guilds[0]
        session["selected_guild_id"] = selected_guild["id"]

    return render_template(
        "index.html",
        user=user,
        guilds=guilds,
        selected_guild=selected_guild
    )


# =========================
# SELECT SERVER
# =========================

@app.route("/select-server", methods=["POST"])
def select_server():

    if "user" not in session:
        return redirect("/login")

    access_token = session.get("access_token")

    if not access_token:
        session.clear()
        return redirect("/login")

    guild_id = request.form.get("guild_id")

    if not guild_id:
        return redirect("/")

    # Get servers the user can actually manage.
    guilds = get_manageable_guilds(access_token)

    # Only allow selecting a server from the verified list.
    allowed = any(
        str(guild.get("id")) == str(guild_id)
        for guild in guilds
    )

    if not allowed:
        return "You do not have permission to manage this server.", 403

    session["selected_guild_id"] = guild_id

    return redirect("/")


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

    try:
        token_response = requests.post(
            f"{DISCORD_API}/oauth2/token",
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=10
        )
    except requests.RequestException:
        return "Failed to connect to Discord.", 500

    if token_response.status_code != 200:
        return "Failed to authenticate with Discord.", 400

    token_data = token_response.json()

    access_token = token_data.get("access_token")

    if not access_token:
        return "Discord did not provide an access token.", 400

    # =========================
    # GET DISCORD USER
    # =========================

    try:
        user_response = requests.get(
            f"{DISCORD_API}/users/@me",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            timeout=10
        )
    except requests.RequestException:
        return "Failed to connect to Discord.", 500

    if user_response.status_code != 200:
        return "Failed to get Discord user.", 400

    user = user_response.json()

    # =========================
    # SAVE LOGIN
    # =========================

    session["user"] = user
    session["access_token"] = access_token

    # Clear any previous server selection.
    session.pop("selected_guild_id", None)

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

    if not user:
        return redirect("/login")

    access_token = session.get("access_token")

    if not access_token:
        session.clear()
        return redirect("/login")

    guilds = get_manageable_guilds(access_token)

    selected_guild_id = session.get("selected_guild_id")

    selected_guild = None

    for guild in guilds:
        if str(guild.get("id")) == str(selected_guild_id):
            selected_guild = guild
            break

    return render_template(
        "moderation.html",
        user=user,
        guilds=guilds,
        selected_guild=selected_guild
    )


# =========================
# TICKETS
# =========================

@app.route("/tickets")
def tickets():

    user = session.get("user")

    if not user:
        return redirect("/login")

    access_token = session.get("access_token")

    if not access_token:
        session.clear()
        return redirect("/login")

    guilds = get_manageable_guilds(access_token)

    selected_guild_id = session.get("selected_guild_id")

    selected_guild = None

    for guild in guilds:
        if str(guild.get("id")) == str(selected_guild_id):
            selected_guild = guild
            break

    return render_template(
        "tickets.html",
        user=user,
        guilds=guilds,
        selected_guild=selected_guild
    )


# =========================
# GIVEAWAYS
# =========================

@app.route("/giveaways")
def giveaways():

    user = session.get("user")

    if not user:
        return redirect("/login")

    access_token = session.get("access_token")

    if not access_token:
        session.clear()
        return redirect("/login")

    guilds = get_manageable_guilds(access_token)

    selected_guild_id = session.get("selected_guild_id")

    selected_guild = None

    for guild in guilds:
        if str(guild.get("id")) == str(selected_guild_id):
            selected_guild = guild
            break

    return render_template(
        "giveaways.html",
        user=user,
        guilds=guilds,
        selected_guild=selected_guild
    )


# =========================
# SETTINGS
# =========================

@app.route("/settings")
def settings():

    user = session.get("user")

    if not user:
        return redirect("/login")

    access_token = session.get("access_token")

    if not access_token:
        session.clear()
        return redirect("/login")

    guilds = get_manageable_guilds(access_token)

    selected_guild_id = session.get("selected_guild_id")

    selected_guild = None

    for guild in guilds:
        if str(guild.get("id")) == str(selected_guild_id):
            selected_guild = guild
            break

    return render_template(
        "settings.html",
        user=user,
        guilds=guilds,
        selected_guild=selected_guild
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