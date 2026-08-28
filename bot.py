import asyncio
from datetime import datetime, timezone, timedelta
import os
import random
import sqlite3
import time

import discord
from discord import app_commands
from discord.ext import commands

# ==========================================
# CONFIG & CONSTANTS
# ==========================================
TOKEN = os.getenv("TOKEN") or "CODE"  # Replace with actual token or set TOKEN env var
PREFIX = ","
OWNER_IDS = {1159048734559195156, 1413144538268303393}
BOT_OWNER_ID = 1159048734559195156
OWNER_ID = BOT_OWNER_ID

# Cache for server custom prefixes & ping emojis
prefix_cache = {}
ping_emoji_cache = {}  # (guild_id, user_id) -> emoji

# ==========================================
# DYNAMIC PREFIX FUNCTION (PER-SERVER & PREFIXLESS)
# ==========================================
def get_prefix(bot, message):
    """
    ⚡ Dynamic prefix handler:
    - Custom prefix per server (stored in database & cached).
    - Default prefix: ','
    - Bot Owners (IDs: 1159048734559195156, 1413144538268303393) can use prefixless commands everywhere.
    - Server Owners can use prefixless commands in their own server!
    """
    current_prefix = PREFIX
    if message.guild:
        guild_id = message.guild.id
        if guild_id in prefix_cache:
            current_prefix = prefix_cache[guild_id]
        else:
            cursor.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (guild_id,))
            row = cursor.fetchone()
            if row and row[0]:
                current_prefix = row[0]
                prefix_cache[guild_id] = current_prefix
            else:
                prefix_cache[guild_id] = PREFIX

    prefixes = [current_prefix]
    if message.author:
        if message.author.id in OWNER_IDS:
            prefixes.append("")  # Allow no prefix for bot owners everywhere
        elif message.guild and message.author.id == message.guild.owner_id:
            prefixes.append("")  # Allow no prefix for server owner in their server
    return prefixes

# ==========================================
# FUN COMMAND GIF COLLECTIONS
# ==========================================
KISS_GIFS = [
    "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
    "https://media.giphy.com/media/FqVM4892PmMw/giphy.gif",
    "https://media.giphy.com/media/11r19vfEPqYBfW/giphy.gif",
    "https://media.giphy.com/media/mq5y2jHRCAqMo/giphy.gif"
]

HUG_GIFS = [
    "https://media.giphy.com/media/PHZ7v9tfQu0o0/giphy.gif",
    "https://media.giphy.com/media/u9BxFE6544aKe/giphy.gif",
    "https://media.giphy.com/media/lrr91vhGUPFqc/giphy.gif",
    "https://media.giphy.com/media/3znE83v3G2xkk/giphy.gif"
]

SLAP_GIFS = [
    "https://media.giphy.com/media/j3iGKfXRKlLqw/giphy.gif",
    "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
    "https://media.giphy.com/media/Zau0yRL15t84w/giphy.gif",
    "https://media.giphy.com/media/m6aEQwdbHFtEA/giphy.gif"
]

HIGHFIVE_GIFS = [
    "https://media.giphy.com/media/ocZcT6i0fM1qM/giphy.gif",
    "https://media.giphy.com/media/10gLW3UxzKYSxa/giphy.gif",
    "https://media.giphy.com/media/l1Jycb782jS9tqTzW/giphy.gif"
]

PAT_GIFS = [
    "https://media.giphy.com/media/5tmRHwWbvgwG4/giphy.gif",
    "https://media.giphy.com/media/L2z7dnOduqEow/giphy.gif",
    "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif"
]

WAVE_GIFS = [
    "https://media.giphy.com/media/xT9IgG50Fb7Mi0prBC/giphy.gif",
    "https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif",
    "https://media.giphy.com/media/dzaUX7CAG0Ihi/giphy.gif"
]

DANCE_GIFS = [
    "https://media.giphy.com/media/131v0W5mFCOyQ0/giphy.gif",
    "https://media.giphy.com/media/blSTtZehjAZ8I/giphy.gif",
    "https://media.giphy.com/media/lu38au6Za04Bq/giphy.gif"
]

LAUGH_GIFS = [
    "https://media.giphy.com/media/wW95fQu21PFyU/giphy.gif",
    "https://media.giphy.com/media/c8bJDVz7i9KRW/giphy.gif",
    "https://media.giphy.com/media/10JhviFuU2gWD6/giphy.gif"
]

CRY_GIFS = [
    "https://media.giphy.com/media/ROF8OQvDmxytW/giphy.gif",
    "https://media.giphy.com/media/8YutMat52dW8g/giphy.gif",
    "https://media.giphy.com/media/L95W4wv8nnb9K/giphy.gif"
]

HANDSHAKE_GIFS = [
    "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
    "https://media.giphy.com/media/3oKIPm3B83XCE3WaHM/giphy.gif"
]

CLAP_GIFS = [
    "https://media.giphy.com/media/6nG553sM3y1y/giphy.gif",
    "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif",
    "https://media.giphy.com/media/1garWn2S3m7zR73Z9O/giphy.gif"
]

PUNCH_GIFS = [
    "https://media.giphy.com/media/11tTNkKOScnWmI/giphy.gif",
    "https://media.giphy.com/media/one23Mcv8yOZgYzxVT/giphy.gif"
]

CUDDLE_GIFS = [
    "https://media.giphy.com/media/lRRJLuXwdtfJsK4RNN/giphy.gif",
    "https://media.giphy.com/media/480hWZg++Zkt2/giphy.gif"
]

POKE_GIFS = [
    "https://media.giphy.com/media/108M7gCS1JSoO4/giphy.gif",
    "https://media.giphy.com/media/WjR522g3eXfA4/giphy.gif"
]

BITE_GIFS = [
    "https://media.giphy.com/media/oXG0y621Z2c9A4wUfF/giphy.gif",
    "https://media.giphy.com/media/l3vR5S33x7nny4gco/giphy.gif"
]

TICKLE_GIFS = [
    "https://media.giphy.com/media/12m3HGobvhthni/giphy.gif",
    "https://media.giphy.com/media/l4FGpP4lxGGgK5CBW/giphy.gif"
]

# ==========================================
# INTENTS & BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None,
    case_insensitive=True,
    owner_ids=OWNER_IDS
)
tree = bot.tree

# ==========================================
# DATABASES INITIALIZATION
# ==========================================

db = sqlite3.connect("botdata.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prefixes (
    guild_id INTEGER PRIMARY KEY,
    prefix TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS economy (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    last_daily TEXT,
    last_work TEXT
)
""")

# Safe migration check for last_work column
cursor.execute("PRAGMA table_info(economy)")
columns = [col[1] for col in cursor.fetchall()]
if "last_work" not in columns:
    cursor.execute("ALTER TABLE economy ADD COLUMN last_work TEXT")

# Custom Ping Emoji Reactions Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ping_emojis (
    guild_id INTEGER,
    user_id INTEGER,
    emoji TEXT,
    PRIMARY KEY(guild_id, user_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER,
    user_id INTEGER,
    channel_id INTEGER,
    status TEXT DEFAULT 'open',
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS modlog_settings (
    guild_id INTEGER PRIMARY KEY,
    log_channel INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    guild_id INTEGER,
    moderator_id INTEGER,
    reason TEXT,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    guild_id INTEGER,
    moderator_id INTEGER,
    action TEXT,
    reason TEXT,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff_stats (
    moderator_id INTEGER PRIMARY KEY,
    warns INTEGER DEFAULT 0,
    mutes INTEGER DEFAULT 0,
    jails INTEGER DEFAULT 0,
    kicks INTEGER DEFAULT 0,
    bans INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS antinuke_settings (
    guild_id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 0,
    action TEXT DEFAULT 'ban',
    log_channel INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS antiraid_settings (
    guild_id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 0,
    join_limit INTEGER DEFAULT 5,
    time_window INTEGER DEFAULT 10,
    action TEXT DEFAULT 'lockdown',
    log_channel INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff_tickets (
    guild_id INTEGER,
    user_id INTEGER,
    tickets INTEGER DEFAULT 0,
    PRIMARY KEY(guild_id, user_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff_history (
    guild_id INTEGER,
    user_id INTEGER,
    action TEXT,
    reason TEXT,
    moderator_id INTEGER,
    timestamp TEXT
)
""")
db.commit()

premium_db = sqlite3.connect("premium.db")
premium_cursor = premium_db.cursor()

premium_cursor.execute("""
CREATE TABLE IF NOT EXISTS premium_servers (
    guild_id INTEGER PRIMARY KEY,
    plan TEXT DEFAULT 'premium',
    expires TEXT
)
""")

premium_cursor.execute("""
CREATE TABLE IF NOT EXISTS server_settings (
    guild_id INTEGER PRIMARY KEY,
    welcome TEXT,
    leave TEXT,
    branding TEXT
)
""")
premium_db.commit()

welcome_db = sqlite3.connect("welcome_leave.db")
welcome_cursor = welcome_db.cursor()

welcome_cursor.execute("""
CREATE TABLE IF NOT EXISTS welcome_leave (
    guild_id INTEGER PRIMARY KEY,
    welcome_channel INTEGER,
    leave_channel INTEGER
)
""")
welcome_db.commit()

# ==========================================
# IN-MEMORY STATE & TRACKERS
# ==========================================
jailed_users = {}
blacklisted_users = set()
raid_mode = {}
join_tracker = {}
anti_nuke = {}
spam_tracker = {}
ticket_stats = {}
staff_stats_mem = {}
applications_open = False

# SNIPE, EDIT SNIPE & AFK TRACKERS
sniped_messages = {}
editsniped_messages = {}
afk_users = {}

# DM Anti-Spam State
dm_spam_tracker = {}
dm_anti_spam_enabled = True
DM_SPAM_LIMIT = 4
DM_SPAM_WINDOW = 5

SPAM_LIMIT = 5
SPAM_WINDOW = 5
STAFF_ROLES = ["Trial Moderator", "Staff", "Moderator"]

# ==========================================
# HELPER & UTILITY FUNCTIONS
# ==========================================

def parse_time(time_str: str) -> int:
    """Parses time strings like '10s', '5m', '2h', '1d' into seconds."""
    unit = time_str[-1].lower()
    if unit not in ['s', 'm', 'h', 'd']:
        return int(time_str)
    val = int(time_str[:-1])
    if unit == 's':
        return val
    elif unit == 'm':
        return val * 60
    elif unit == 'h':
        return val * 3600
    elif unit == 'd':
        return val * 86400
    return val


async def get_mod_log_channel(guild: discord.Guild):
    if not guild:
        return None

    cursor.execute("SELECT log_channel FROM modlog_settings WHERE guild_id = ?", (guild.id,))
    row = cursor.fetchone()
    if row and row[0]:
        channel = guild.get_channel(row[0])
        if channel:
            return channel

    channel = discord.utils.get(guild.text_channels, name="mod-logs")
    return channel


async def is_premium(guild_id: int) -> bool:
    if not guild_id:
        return False
    premium_cursor.execute("SELECT guild_id FROM premium_servers WHERE guild_id = ?", (guild_id,))
    return premium_cursor.fetchone() is not None


def premium_only():
    async def predicate(ctx):
        if ctx.guild is None:
            await ctx.send("❌ Premium features can only be used in a server.")
            return False

        if await is_premium(ctx.guild.id):
            return True

        await ctx.send("❌ This is a **Baby Seal Premium** feature!")
        return False

    return commands.check(predicate)


async def send_log(guild, title, description, color=discord.Color.blue()):
    if guild is None:
        return
    channel = await get_mod_log_channel(guild)
    if channel is None:
        return

    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now(timezone.utc))
    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"Error sending log in {guild.name}: {e}")


async def add_history(guild, user, moderator, action, reason):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cursor.execute("""
        INSERT INTO history (user_id, guild_id, moderator_id, action, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user.id, guild.id, moderator.id, action, reason, timestamp))
    db.commit()

# ==========================================
# TICKET BUTTON UI COMPONENTS
# ==========================================

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Closing ticket in 5 seconds...", ephemeral=False)
        
        cursor.execute("UPDATE tickets SET status = 'closed' WHERE channel_id = ?", (interaction.channel.id,))
        db.commit()
        
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
        except Exception as e:
            print(f"Error deleting ticket channel: {e}")


class TicketLaunchView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Open Ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket_btn")
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        channel_name = f"ticket-{user.name.lower()}"
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            return await interaction.response.send_message(f"❌ You already have an open ticket in {existing_channel.mention}!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        staff_roles = [role for role in guild.roles if role.name in STAFF_ROLES]
        for s_role in staff_roles:
            overwrites[s_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket opened by {user}"
        )

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        cursor.execute("""
            INSERT INTO tickets (guild_id, user_id, channel_id, status, timestamp)
            VALUES (?, ?, ?, 'open', ?)
        """, (guild.id, user.id, ticket_channel.id, timestamp))
        db.commit()

        staff_pings = " ".join([r.mention for r in staff_roles]) if staff_roles else ""
        ping_msg = f"{user.mention} {staff_pings}".strip()

        welcome_embed = discord.Embed(
            title="📩 Support Ticket Created",
            description=f"Welcome {user.mention}!\n\nPlease state your question or issue below. A staff member will assist you shortly.",
            color=discord.Color.blue()
        )
        welcome_embed.set_footer(text="Click the button below when you are ready to close this ticket.")

        await ticket_channel.send(content=ping_msg, embed=welcome_embed, view=CloseTicketView())
        await interaction.followup.send(f"✅ Ticket created! Please head over to {ticket_channel.mention}", ephemeral=True)

# ==========================================
# INTERACTIVE HELP COMMAND MENU
# ==========================================

class HelpDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderation", description="Jail, Mute, Kick, Ban, Warn, Purge...", emoji="🛡️"),
            discord.SelectOption(label="Server Setup", description="SetPrefix, SetPingEmoji, Setup, SetModLog...", emoji="⚙️"),
            discord.SelectOption(label="Baby Seal Premium", description="Mimic, Custom Messages, Embed Builder...", emoji="⭐"),
            discord.SelectOption(label="Staff & Tickets", description="Ticket Panel, Staff Panel, Accept, Deny...", emoji="👮"),
            discord.SelectOption(label="Economy & Rewards", description="Daily, Work, Gamble, Balance, Pay, Baltop...", emoji="💰"),
            discord.SelectOption(label="Fun & Social", description="Kiss, Hug, Slap, Highfive, Punch, Cuddle...", emoji="🎉"),
            discord.SelectOption(label="Utility & Info", description="Snipe, EditSnipe, AFK, Remind, Ping...", emoji="ℹ️"),
            discord.SelectOption(label="Bot Owner", description="AddPremium, Blacklist, AntiDMSpam, Leave...", emoji="👑"),
        ]
        super().__init__(placeholder="Choose a category to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = discord.Embed(color=discord.Color.dark_red())
        curr_pref = prefix_cache.get(interaction.guild_id, PREFIX) if interaction.guild_id else PREFIX

        if category == "Moderation":
            embed.title = "🛡️ Moderation Commands"
            embed.description = (
                f"`{curr_pref}jail @user [reason]` - Jail a member\n"
                f"`{curr_pref}unjail @user` - Unjail a member\n"
                f"`{curr_pref}mute @user <mins> [reason]` - Timeout a member\n"
                f"`{curr_pref}unmute @user` - Remove timeout\n"
                f"`{curr_pref}kick @user [reason]` - Kick a member\n"
                f"`{curr_pref}ban @user [reason]` - Ban a member\n"
                f"`{curr_pref}unban <user_id>` - Unban a user\n"
                f"`{curr_pref}warn @user [reason]` - Issue a warning\n"
                f"`{curr_pref}history @user` - View moderation history\n"
                f"`{curr_pref}purge <amount>` - Delete messages\n"
                f"`{curr_pref}clean [amount]` - Delete bot messages\n"
                f"`{curr_pref}lock` | `{curr_pref}unlock` - Lock or unlock channel\n"
                f"`{curr_pref}slowmode <seconds>` - Set channel slowmode\n"
                f"`{curr_pref}antinuke <on/off>` - Toggle anti-nuke protection"
            )

        elif category == "Server Setup":
            embed.title = "⚙️ Server Setup Commands"
            embed.description = (
                f"`{curr_pref}setprefix <prefix>` - Change server command prefix\n"
                f"`{curr_pref}prefix` - View current server prefix\n"
                f"`{curr_pref}setpingemoji @user <emoji>` - React with emoji whenever user is pinged\n"
                f"`{curr_pref}delpingemoji @user` - Remove custom ping emoji for user\n"
                f"`{curr_pref}pingemojis` - List all ping emoji reaction setups\n"
                f"`{curr_pref}setup` - Auto-create moderation roles & channels\n"
                f"`{curr_pref}setmodlog #channel` - Set mod-log channel\n"
                f"`{curr_pref}setwelcome #channel` - Set welcome channel\n"
                f"`{curr_pref}setleave #channel` - Set leave channel\n"
                f"`{curr_pref}say <message>` | `{curr_pref}announce <message>`"
            )

        elif category == "Baby Seal Premium":
            embed.title = "⭐ Baby Seal Premium Commands"
            embed.description = (
                f"`{curr_pref}mimic` - Equip server's logo, banner & name for the bot (per server)\n"
                f"`{curr_pref}syncnickname` - Sync bot nickname to server name\n"
                f"`{curr_pref}customwelcome <msg>` - Set custom premium welcome message\n"
                f"`{curr_pref}customleave <msg>` - Set custom premium leave message\n"
                f"`{curr_pref}embedbuilder #chan <title>` - Send custom embed\n"
                f"`{curr_pref}serverbranding <name>` - Set server branding text\n"
                f"`{curr_pref}antiraid` - Enable premium raid protection\n"
                f"`{curr_pref}promotion` - View automatic staff promotion info\n"
                f"`{curr_pref}premiumstatus` - Check server premium status"
            )

        elif category == "Staff & Tickets":
            embed.title = "👮 Staff & Ticket Commands"
            embed.description = (
                f"`{curr_pref}ticketpanel` - Send button ticket creation panel\n"
                f"`{curr_pref}staffpanel` - View staff management panel\n"
                f"`{curr_pref}stafflist` - List all staff members\n"
                f"`{curr_pref}staffstats` - View staff application statistics\n"
                f"`{curr_pref}accept @user` - Accept staff application\n"
                f"`{curr_pref}deny @user` - Deny staff application\n"
                f"`{curr_pref}demote @user` - Demote Staff -> Trial Mod\n"
                f"`{curr_pref}application <open/close>` - Toggle staff applications\n"
                f"`{curr_pref}ticketdone @user` - Record a completed ticket\n"
                f"`{curr_pref}mystats` - View your completed ticket count\n"
                f"`{curr_pref}ticketstats` - View staff ticket leaderboard"
            )

        elif category == "Economy & Rewards":
            embed.title = "💰 Economy & Rewards Commands"
            embed.description = (
                f"`{curr_pref}daily` - Claim daily coin rewards (24h cooldown)\n"
                f"`{curr_pref}work` - Earn money working (1h cooldown)\n"
                f"`{curr_pref}gamble <amount>` | `{curr_pref}slots` - Bet coins on slots\n"
                f"`{curr_pref}balance` | `{curr_pref}bal [@user]` - View wallet balance\n"
                f"`{curr_pref}pay @user <amount>` - Transfer coins to another member\n"
                f"`{curr_pref}baltop` | `{curr_pref}leaderboard` - Top 10 richest members"
            )

        elif category == "Fun & Social":
            embed.title = "🎉 Fun & Social Commands"
            embed.description = (
                f"`{curr_pref}hi` | `{curr_pref}kiss` | `{curr_pref}hug` | `{curr_pref}slap` | `{curr_pref}highfive` | `{curr_pref}pat` | `{curr_pref}wave`\n"
                f"`{curr_pref}dance` | `{curr_pref}laugh` | `{curr_pref}cry` | `{curr_pref}handshake` | `{curr_pref}clap` | `{curr_pref}punch`\n"
                f"`{curr_pref}cuddle` | `{curr_pref}poke` | `{curr_pref}bite` | `{curr_pref}tickle`\n"
                f"`{curr_pref}giveaway <time_sec> <prize>` - Host a giveaway\n"
                f"`{curr_pref}poll <question>` - Create a reaction poll\n"
                f"`{curr_pref}roll` - Roll a random number (1-100)\n"
                f"`{curr_pref}choose <opt1, opt2>` - Choose between options\n"
                f"`{curr_pref}joke` - Tell a random joke"
            )

        elif category == "Utility & Info":
            embed.title = "ℹ️ Utility & Info Commands"
            embed.description = (
                f"`{curr_pref}snipe` - View last deleted message in channel\n"
                f"`{curr_pref}editsnipe` - View last edited message in channel\n"
                f"`{curr_pref}afk [reason]` - Set your AFK status\n"
                f"`{curr_pref}remind <time> <reason>` - Set a reminder (e.g. 10m, 1h)\n"
                f"`{curr_pref}ping` - Check bot latency\n"
                f"`{curr_pref}userinfo [@user]` - View user account info\n"
                f"`{curr_pref}avatar [@user]` - View user avatar\n"
                f"`{curr_pref}serverinfo` - View server details & stats\n"
                f"`{curr_pref}members` - View member count"
            )

        elif category == "Bot Owner":
            embed.title = "👑 Bot Owner Commands"
            embed.description = (
                f"`{curr_pref}addpremium <guild_id>` - Grant premium to a server\n"
                f"`{curr_pref}removepremium <guild_id>` - Revoke server premium\n"
                f"`{curr_pref}blacklist @user` - Blacklist user from bot\n"
                f"`{curr_pref}unblacklist @user` - Remove user from blacklist\n"
                f"`{curr_pref}antidmspam <on/off>` - Toggle DM Anti-Spam protection\n"
                f"`{curr_pref}tuff` - Grant owner Tuff admin role\n"
                f"`{curr_pref}leave` - Make bot leave current server"
            )

        embed.set_footer(text="Baby Seal Help System", icon_url=interaction.client.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown())


@bot.command(name="help")
async def help_command(ctx):
    """Displays the interactive command help menu."""
    curr_prefix = ctx.prefix if ctx.prefix else PREFIX
    embed = discord.Embed(
        title="🦭 Baby Seal - Help Menu",
        description=(
            "Welcome to **Baby Seal**! Select a category from the dropdown menu below to view available commands.\n\n"
            "**Command Categories:**\n"
            "🛡️ `Moderation` - Jail, Mute, Kick, Ban, Warn, Purge\n"
            "⚙️ `Server Setup` - SetPrefix, SetPingEmoji, Setup, SetModLog\n"
            "⭐ `Baby Seal Premium` - Mimic, Custom Messages, Embed Builder\n"
            "👮 `Staff & Tickets` - Ticket Panel, Applications, Staff Panel\n"
            "💰 `Economy & Rewards` - Daily, Work, Gamble, Balance, Pay, Baltop\n"
            "🎉 `Fun & Social` - Roleplay Actions, Giveaways, Polls\n"
            "ℹ️ `Utility & Info` - Snipe, EditSnipe, AFK, Remind, Ping\n"
            "👑 `Bot Owner` - Premium & Blacklist Management"
        ),
        color=discord.Color.dark_red()
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Server Prefix: '{curr_prefix}' (Prefixless enabled for Server Owner & Bot Owners) | Select a category below")

    await ctx.send(embed=embed, view=HelpView())

# ==========================================
# BOT READY EVENT
# ==========================================
@bot.event
async def on_ready():
    await tree.sync()

    # Cache custom prefixes
    cursor.execute("SELECT guild_id, prefix FROM prefixes")
    for gid, pref in cursor.fetchall():
        prefix_cache[gid] = pref

    # Cache custom ping emojis
    cursor.execute("SELECT guild_id, user_id, emoji FROM ping_emojis")
    for gid, uid, em in cursor.fetchall():
        ping_emoji_cache[(gid, uid)] = em

    bot.add_view(TicketLaunchView())
    bot.add_view(CloseTicketView())

    print("--------------------------------------------------")
    print(f" Logged in as {bot.user}")
    print(f" Default Prefix: '{PREFIX}'")
    print(f" Loaded {len(ping_emoji_cache)} ping emoji reaction assignments")
    print(f" Prefixless Mode: ENABLED (Bot Owners: {OWNER_IDS} & Server Owners)")
    print("--------------------------------------------------")

# ==========================================
# UNIFIED EVENT HANDLERS & PING REACTION DETECTOR
# ==========================================
@bot.event
async def on_guild_join(guild):
    try:
        await guild.me.edit(nick=guild.name)
    except Exception:
        pass

    if guild.owner and guild.owner.id in blacklisted_users:
        try:
            await guild.owner.send("🚫 I cannot join your server because you are blacklisted.")
        except Exception:
            pass
        await guild.leave()
        return

    invite_str = "No invite created"
    try:
        channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).create_instant_invite), None)
        if channel:
            invite_obj = await channel.create_invite(max_age=0, max_uses=0, reason="Setup invite")
            invite_str = str(invite_obj)
    except Exception as e:
        print("Invite creation error:", e)

    embed = discord.Embed(title="🤖 Bot Added To A New Server", color=discord.Color.green())
    embed.add_field(name="Server", value=f"{guild.name}\n`{guild.id}`", inline=False)
    embed.add_field(name="Members", value=str(guild.member_count), inline=True)
    embed.add_field(name="Owner", value=f"{guild.owner} (`{guild.owner.id}`)", inline=False)
    embed.add_field(name="Invite", value=invite_str, inline=False)
    embed.set_footer(text="New server setup request")

    try:
        owner_user = await bot.fetch_user(OWNER_ID)
        await owner_user.send(embed=embed)
    except Exception as e:
        print("Couldn't notify owner on guild join:", e)


@bot.event
async def on_member_join(member):
    guild = member.guild

    if raid_mode.get(guild.id):
        current_time = time.time()
        if guild.id not in join_tracker:
            join_tracker[guild.id] = []
        join_tracker[guild.id].append(current_time)

        join_tracker[guild.id] = [t for t in join_tracker[guild.id] if current_time - t <= 10]

        if len(join_tracker[guild.id]) >= 5:
            await send_log(guild, "🚨 RAID DETECTED", f"Members joined: {len(join_tracker[guild.id])} in 10s", discord.Color.red())
            try:
                await member.kick(reason="Anti-Raid Protection")
                return
            except Exception:
                pass

    mod_channel = await get_mod_log_channel(guild)
    if mod_channel:
        now = datetime.now(timezone.utc)
        account_age = now - member.created_at
        embed = discord.Embed(title="🟢 Member Joined", color=discord.Color.green(), timestamp=now)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="User", value=f"{member.mention}\n{member}", inline=False)
        embed.add_field(name="User ID", value=f"`{member.id}`", inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%d %B %Y %I:%M %p UTC"), inline=False)
        embed.add_field(name="Account Age", value=f"{account_age.days} day(s)", inline=False)
        embed.add_field(name="Bot Account", value="Yes" if member.bot else "No", inline=False)
        try:
            await mod_channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending join log to {guild.name}: {e}")

    welcome_cursor.execute("SELECT welcome_channel FROM welcome_leave WHERE guild_id=?", (guild.id,))
    res = welcome_cursor.fetchone()
    if res and res[0]:
        channel = guild.get_channel(res[0])
        if channel:
            premium_cursor.execute("SELECT welcome FROM server_settings WHERE guild_id=?", (guild.id,))
            prem_welcome = premium_cursor.fetchone()
            if prem_welcome and prem_welcome[0]:
                msg = prem_welcome[0].replace("{user}", member.mention).replace("{server}", guild.name)
                await channel.send(msg)
            else:
                await channel.send(f"🦭 Welcome {member.mention} to **{guild.name}**!\nEnjoy your stay!")


@bot.event
async def on_member_remove(member):
    guild = member.guild
    await send_log(guild, "🔴 Member Left", f"User: {member}\nID: `{member.id}`", discord.Color.red())

    welcome_cursor.execute("SELECT leave_channel FROM welcome_leave WHERE guild_id=?", (guild.id,))
    res = welcome_cursor.fetchone()
    if res and res[0]:
        channel = guild.get_channel(res[0])
        if channel:
            premium_cursor.execute("SELECT leave FROM server_settings WHERE guild_id=?", (guild.id,))
            prem_leave = premium_cursor.fetchone()
            if prem_leave and prem_leave[0]:
                msg = prem_leave[0].replace("{user}", member.name).replace("{server}", guild.name)
                await channel.send(msg)
            else:
                await channel.send(f"👋 **{member.name}** has left **{guild.name}**.\nWe hope to see you again!")


@bot.event
async def on_message_delete(message):
    if message.guild is None or message.author.bot:
        return

    sniped_messages[message.channel.id] = {
        "author": message.author,
        "content": message.content,
        "created_at": message.created_at,
        "attachment": message.attachments[0].url if message.attachments else None
    }

    await send_log(message.guild, "🗑 Message Deleted", f"Author: {message.author}\nChannel: {message.channel}\nMessage: {message.content[:1000]}", discord.Color.red())


@bot.event
async def on_message_edit(before, after):
    if before.guild is None or before.author.bot or before.content == after.content:
        return

    editsniped_messages[before.channel.id] = {
        "author": before.author,
        "before": before.content,
        "after": after.content,
        "created_at": before.created_at
    }

    await send_log(before.guild, "✏ Message Edited", f"User: {before.author}\nChannel: {before.channel}\nBefore: {before.content[:500]}\nAfter: {after.content[:500]}", discord.Color.orange())


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check Blacklisted Users
    if message.author.id in blacklisted_users:
        return

    # DM SPAM DETECTION SYSTEM
    if message.guild is None:
        if dm_anti_spam_enabled and message.author.id not in OWNER_IDS:
            user_id = message.author.id
            now = time.time()

            if user_id not in dm_spam_tracker:
                dm_spam_tracker[user_id] = []
            dm_spam_tracker[user_id].append(now)
            dm_spam_tracker[user_id] = [t for t in dm_spam_tracker[user_id] if now - t < DM_SPAM_WINDOW]

            if len(dm_spam_tracker[user_id]) >= DM_SPAM_LIMIT:
                dm_spam_tracker[user_id].clear()
                blacklisted_users.add(user_id)

                try:
                    await message.author.send("⚠️ **Anti-Spam Warning**: You have been flagged for DM spamming and blacklisted from using this bot.")
                except Exception:
                    pass

                # Notify Bot Owners
                try:
                    for oid in OWNER_IDS:
                        owner = await bot.fetch_user(oid)
                        if owner:
                            embed = discord.Embed(
                                title="🚨 DM Spam Detected",
                                description=(
                                    f"**User:** {message.author} (`{message.author.id}`)\n"
                                    f"**Spam Content:** `{message.content[:500]}`\n\n"
                                    f"✅ User has been automatically blacklisted."
                                ),
                                color=discord.Color.red(),
                                timestamp=datetime.now(timezone.utc)
                            )
                            await owner.send(embed=embed)
                except Exception as e:
                    print("Failed to notify owners of DM spam:", e)

                return

        await bot.process_commands(message)
        return

    # 🆕 CUSTOM PING EMOJI REACTION DETECTOR
    if message.guild and message.mentions:
        for mentioned in message.mentions:
            if (message.guild.id, mentioned.id) in ping_emoji_cache:
                assigned_emoji = ping_emoji_cache[(message.guild.id, mentioned.id)]
                try:
                    await message.add_reaction(assigned_emoji)
                except Exception as e:
                    print(f"Error reacting with custom ping emoji: {e}")

    # Check AFK return
    if message.author.id in afk_users:
        afk_info = afk_users.pop(message.author.id)
        duration = datetime.now(timezone.utc) - afk_info["time"]
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours}h {minutes}m {seconds}s" if hours else (f"{minutes}m {seconds}s" if minutes else f"{seconds}s")

        try:
            if message.author.display_name.startswith("[AFK] "):
                await message.author.edit(nick=message.author.display_name.replace("[AFK] ", ""))
        except Exception:
            pass

        await message.channel.send(f"Welcome back {message.author.mention}! I removed your AFK status. (You were AFK for **{time_str}**)")

    # Check AFK mentions
    if message.mentions:
        for mentioned in message.mentions:
            if mentioned.id in afk_users and mentioned.id != message.author.id:
                afk_info = afk_users[mentioned.id]
                duration = datetime.now(timezone.utc) - afk_info["time"]
                hours, remainder = divmod(int(duration.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours}h {minutes}m {seconds}s" if hours else (f"{minutes}m {seconds}s" if minutes else f"{seconds}s")
                await message.channel.send(f"ℹ️ **{mentioned.display_name}** is currently AFK: **{afk_info['reason']}** (since {time_str} ago)")

    # Guild Spam Detection
    user_id = message.author.id
    now = time.time()

    if user_id not in spam_tracker:
        spam_tracker[user_id] = []
    spam_tracker[user_id].append(now)
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if now - t < SPAM_WINDOW]

    if len(spam_tracker[user_id]) >= SPAM_LIMIT:
        spam_tracker[user_id].clear()
        try:
            await message.delete()
        except Exception:
            pass
        ctx = await bot.get_context(message)
        await ctx.invoke(jail, member=message.author, reason="Automatic spam protection")
        return

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You do not have permission to run this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found.")
    else:
        print(f"Command Error in {ctx.command}: {error}")


@bot.listen("on_command")
async def command_logger(ctx):
    if ctx.guild is None:
        return
    try:
        owner = await bot.fetch_user(OWNER_ID)
        command_name = ctx.command.qualified_name if ctx.command else "Unknown"
        message = (
            f"📢 **Command Used**\n\n"
            f"**Command:** {ctx.prefix}{command_name}\n"
            f"**Executor:** {ctx.author} ({ctx.author.id})\n"
            f"**Server:** {ctx.guild.name}\n"
            f"**Server ID:** {ctx.guild.id}\n"
            f"**Channel:** #{ctx.channel.name}\n"
            f"**Time:** <t:{int(ctx.message.created_at.timestamp())}:F>"
        )
        await owner.send(message)
    except Exception:
        pass

# ==========================================
# 🆕 CUSTOM PING EMOJI SETUP COMMANDS
# ==========================================

@bot.command(name="setpingemoji")
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def setpingemoji(ctx, member: discord.Member, emoji: str):
    """Assigns an emoji reaction whenever a member is pinged/mentioned in the server."""
    # Test if valid emoji by adding and removing reaction
    try:
        await ctx.message.add_reaction(emoji)
    except Exception:
        return await ctx.send("❌ Invalid emoji! Please use a valid Unicode emoji or custom server emoji.")

    cursor.execute("""
        INSERT INTO ping_emojis (guild_id, user_id, emoji) VALUES (?, ?, ?)
        ON CONFLICT(guild_id, user_id) DO UPDATE SET emoji = excluded.emoji
    """, (ctx.guild.id, member.id, emoji))
    db.commit()

    ping_emoji_cache[(ctx.guild.id, member.id)] = emoji

    embed = discord.Embed(
        title="🎯 Custom Ping Emoji Assigned!",
        description=f"Whenever {member.mention} is pinged in this server, I will automatically react with {emoji}!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command(name="delpingemoji", aliases=["removepingemoji"])
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def delpingemoji(ctx, member: discord.Member):
    """Removes a custom ping reaction emoji for a member."""
    cursor.execute("DELETE FROM ping_emojis WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id))
    db.commit()

    if (ctx.guild.id, member.id) in ping_emoji_cache:
        del ping_emoji_cache[(ctx.guild.id, member.id)]

    await ctx.send(f"✅ Removed custom ping reaction emoji for {member.mention}.")


@bot.command(name="pingemojis")
@commands.guild_only()
async def pingemojis(ctx):
    """Lists all active custom ping emoji assignments in this server."""
    cursor.execute("SELECT user_id, emoji FROM ping_emojis WHERE guild_id = ?", (ctx.guild.id,))
    rows = cursor.fetchall()
    if not rows:
        return await ctx.send("❌ No custom ping emojis have been set in this server.")

    embed = discord.Embed(title=f"🎯 Custom Ping Reaction Emojis - {ctx.guild.name}", color=discord.Color.blue())
    for uid, em in rows:
        m = ctx.guild.get_member(uid)
        name = m.mention if m else f"User ID `{uid}`"
        embed.add_field(name=f"Member: {name}", value=f"Reaction: {em}", inline=False)

    await ctx.send(embed=embed)

# ==========================================
# SNIPE, EDIT SNIPE, AFK & REMINDER COMMANDS
# ==========================================

@bot.command(name="snipe")
async def snipe(ctx):
    """View the last deleted message in this channel."""
    data = sniped_messages.get(ctx.channel.id)
    if not data:
        return await ctx.send("❌ There's nothing to snipe in this channel!")

    embed = discord.Embed(
        description=data["content"] or "*No text content*",
        color=discord.Color.red(),
        timestamp=data["created_at"]
    )
    embed.set_author(name=str(data["author"]), icon_url=data["author"].display_avatar.url)
    if data["attachment"]:
        embed.set_image(url=data["attachment"])
    embed.set_footer(text=f"Sniped in #{ctx.channel.name}")
    await ctx.send(embed=embed)


@bot.command(name="editsnipe")
async def editsnipe(ctx):
    """View the last edited message in this channel."""
    data = editsniped_messages.get(ctx.channel.id)
    if not data:
        return await ctx.send("❌ There's no edited message to snipe in this channel!")

    embed = discord.Embed(
        title="✏️ Edited Message Snipe",
        color=discord.Color.orange(),
        timestamp=data["created_at"]
    )
    embed.set_author(name=str(data["author"]), icon_url=data["author"].display_avatar.url)
    embed.add_field(name="Before", value=data["before"] or "*Empty*", inline=False)
    embed.add_field(name="After", value=data["after"] or "*Empty*", inline=False)
    embed.set_footer(text=f"Sniped in #{ctx.channel.name}")
    await ctx.send(embed=embed)


@bot.command(name="afk")
async def afk(ctx, *, reason: str = "AFK"):
    """Set your status to AFK."""
    afk_users[ctx.author.id] = {
        "reason": reason,
        "time": datetime.now(timezone.utc)
    }

    try:
        if not ctx.author.display_name.startswith("[AFK]"):
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}"[:32])
    except Exception:
        pass

    embed = discord.Embed(
        title="💤 AFK Status Set",
        description=f"{ctx.author.mention} is now AFK: **{reason}**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)


@bot.command(name="remind", aliases=["reminder"])
async def remind(ctx, time_str: str, *, reminder: str):
    """Set a reminder. Example: remind 10m Do homework"""
    try:
        seconds = parse_time(time_str)
    except Exception:
        return await ctx.send("❌ Invalid time format! Use numbers followed by `s`, `m`, `h`, or `d`. Example: `10m`, `2h`")

    if seconds <= 0 or seconds > 86400 * 30:
        return await ctx.send("❌ Reminder time must be between 1 second and 30 days.")

    end_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    embed = discord.Embed(
        title="⏰ Reminder Set!",
        description=f"I will remind you about: **{reminder}** in **{time_str}** (<t:{int(end_time.timestamp())}:R>).",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

    async def reminder_task():
        await asyncio.sleep(seconds)
        rem_embed = discord.Embed(
            title="⏰ Reminder!",
            description=f"{ctx.author.mention}, you asked me to remind you:\n\n📝 **{reminder}**",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        try:
            await ctx.send(content=ctx.author.mention, embed=rem_embed)
        except Exception:
            try:
                await ctx.author.send(embed=rem_embed)
            except Exception:
                pass

    asyncio.create_task(reminder_task())

# ==========================================
# 🆕 ECONOMY EXPANSION & DAILY REWARDS
# ==========================================

@bot.command(name="daily")
async def daily(ctx):
    """Claim your daily coin reward (24-hour cooldown)."""
    user_id = ctx.author.id
    now = datetime.now(timezone.utc)

    cursor.execute("SELECT balance, last_daily FROM economy WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[1]:
        try:
            last_daily_time = datetime.fromisoformat(row[1])
            if now - last_daily_time < timedelta(hours=24):
                remaining = timedelta(hours=24) - (now - last_daily_time)
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                return await ctx.send(f"⏳ You already claimed your daily reward! Cooldown remaining: **{hours}h {minutes}m {seconds}s**")
        except Exception:
            pass

    reward = random.randint(300, 700)
    current_bal = row[0] if row else 0
    new_bal = current_bal + reward

    cursor.execute("""
        INSERT INTO economy (user_id, balance, last_daily) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = balance + excluded.balance, last_daily = excluded.last_daily
    """, (user_id, reward, now.isoformat()))
    db.commit()

    embed = discord.Embed(
        title="🎁 Daily Reward Claimed!",
        description=f"{ctx.author.mention}, you received **${reward:,}** coins!\n💰 Total Balance: **${new_bal:,}**",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="work")
async def work(ctx):
    """Work to earn coins (1-hour cooldown)."""
    user_id = ctx.author.id
    now = datetime.now(timezone.utc)

    cursor.execute("SELECT balance, last_work FROM economy WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[1]:
        try:
            last_work_time = datetime.fromisoformat(row[1])
            if now - last_work_time < timedelta(hours=1):
                remaining = timedelta(hours=1) - (now - last_work_time)
                minutes, seconds = divmod(int(remaining.total_seconds()), 60)
                return await ctx.send(f"⏳ You are tired! Rest for **{minutes}m {seconds}s** before working again.")
        except Exception:
            pass

    jobs = [
        ("worked as a Discord Mod", random.randint(150, 350)),
        ("developed a Python bot", random.randint(200, 400)),
        ("served coffee at a café", random.randint(100, 250)),
        ("fixed bugs in code", random.randint(180, 320)),
        ("designed server banners", random.randint(120, 280))
    ]
    job_name, reward = random.choice(jobs)

    cursor.execute("""
        INSERT INTO economy (user_id, balance, last_work) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = balance + excluded.balance, last_work = excluded.last_work
    """, (user_id, reward, now.isoformat()))
    db.commit()

    current_bal = (row[0] if row else 0) + reward

    embed = discord.Embed(
        title="💼 Work Completed!",
        description=f"{ctx.author.mention}, you {job_name} and earned **${reward:,}** coins!\n💰 Balance: **${current_bal:,}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command(name="gamble", aliases=["slots"])
async def gamble(ctx, amount: int):
    """Bet your coins on the slot machine!"""
    if amount <= 0:
        return await ctx.send("❌ Bet amount must be greater than 0.")

    cursor.execute("SELECT balance FROM economy WHERE user_id = ?", (ctx.author.id,))
    row = cursor.fetchone()
    author_bal = row[0] if row else 0

    if author_bal < amount:
        return await ctx.send(f"❌ You don't have enough coins! Balance: **${author_bal:,}**")

    slots = ["7️⃣", "💎", "🔔", "🍎", "🍋", "🍇"]
    reel1, reel2, reel3 = random.choice(slots), random.choice(slots), random.choice(slots)

    slot_display = f"[ {reel1} | {reel2} | {reel3} ]"

    if reel1 == reel2 == reel3:
        winnings = amount * 3
        cursor.execute("UPDATE economy SET balance = balance + ? WHERE user_id = ?", (winnings, ctx.author.id))
        db.commit()
        desc = f"{slot_display}\n\n🎉 **JACKPOT!** You matched 3 symbols and won **${winnings:,}** coins!"
        color = discord.Color.gold()
    elif reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
        winnings = int(amount * 1.5)
        cursor.execute("UPDATE economy SET balance = balance + ? WHERE user_id = ?", (winnings, ctx.author.id))
        db.commit()
        desc = f"{slot_display}\n\n✨ **WIN!** You matched 2 symbols and won **${winnings:,}** coins!"
        color = discord.Color.green()
    else:
        cursor.execute("UPDATE economy SET balance = balance - ? WHERE user_id = ?", (amount, ctx.author.id))
        db.commit()
        desc = f"{slot_display}\n\n❌ **LOSS!** You lost **${amount:,}** coins. Better luck next time!"
        color = discord.Color.red()

    new_bal = author_bal + (winnings if 'winnings' in locals() else -amount)

    embed = discord.Embed(title="🎰 Slot Machine", description=desc, color=color)
    embed.set_footer(text=f"New Balance: ${new_bal:,}")
    await ctx.send(embed=embed)


@bot.command(name="balance", aliases=["bal"])
async def balance(ctx, member: discord.Member = None):
    """View your or another member's coin balance."""
    target = member or ctx.author
    cursor.execute("SELECT balance FROM economy WHERE user_id = ?", (target.id,))
    row = cursor.fetchone()
    bal = row[0] if row else 0

    embed = discord.Embed(
        title=f"💰 {target.display_name}'s Balance",
        description=f"Wallet Balance: **${bal:,}**",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="baltop", aliases=["leaderboard"])
async def baltop(ctx):
    """Displays the top 10 richest members in the server."""
    cursor.execute("SELECT user_id, balance FROM economy ORDER BY balance DESC LIMIT 50")
    rows = cursor.fetchall()

    leaderboard = []
    rank = 1
    for uid, bal in rows:
        m = ctx.guild.get_member(uid)
        if m:
            leaderboard.append(f"**#{rank}** {m.mention} - **${bal:,}**")
            rank += 1
            if rank > 10:
                break

    if not leaderboard:
        return await ctx.send("❌ No economy data found for members in this server.")

    embed = discord.Embed(
        title=f"🏆 Top 10 Economy Leaderboard - {ctx.guild.name}",
        description="\n".join(leaderboard),
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)


@bot.command(name="pay")
async def pay(ctx, member: discord.Member, amount: int):
    """Transfer coins to another server member."""
    if member == ctx.author:
        return await ctx.send("❌ You cannot pay yourself.")
    if amount <= 0:
        return await ctx.send("❌ Amount must be greater than 0.")

    cursor.execute("SELECT balance FROM economy WHERE user_id = ?", (ctx.author.id,))
    row = cursor.fetchone()
    author_bal = row[0] if row else 0

    if author_bal < amount:
        return await ctx.send(f"❌ You don't have enough coins! Your balance: **${author_bal:,}**")

    cursor.execute("UPDATE economy SET balance = balance - ? WHERE user_id = ?", (amount, ctx.author.id))
    cursor.execute("""
        INSERT INTO economy (user_id, balance) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = balance + excluded.balance
    """, (member.id, amount))
    db.commit()

    await ctx.send(f"💸 {ctx.author.mention} transferred **${amount:,}** coins to {member.mention}!")

# ==========================================
# TICKET PANEL COMMAND
# ==========================================

@bot.command(name="ticketpanel")
@commands.has_permissions(manage_channels=True)
async def ticketpanel(ctx):
    """Sends the interactive support ticket panel."""
    embed = discord.Embed(
        title="📩 Support Tickets",
        description="Need assistance or have a question for staff?\n\nClick the **📩 Open Ticket** button below to create a private support channel.",
        color=discord.Color.dark_red()
    )
    embed.set_footer(text="Baby Seal Support System")
    await ctx.send(embed=embed, view=TicketLaunchView())

# ==========================================
# SERVER MIMIC & BRANDING COMMANDS (PREMIUM ONLY)
# ==========================================

@bot.command(name="mimic")
@commands.guild_only()
@premium_only()
@commands.has_permissions(manage_guild=True)
async def mimic(ctx):
    """
    🎭 [⭐ Premium] Mimics the server's identity (nickname, server avatar, and banner if available)
    for the bot in the current server ONLY (per-server profile).
    """
    guild = ctx.guild
    status_msg = await ctx.send("🔄 **Fetching server assets and updating bot profile for this server...**")

    nickname = guild.name
    icon_bytes = None
    banner_bytes = None

    avatar_status = "❌ None (No Server Icon)"
    banner_status = "❌ None (No Server Banner)"

    if guild.icon:
        try:
            icon_bytes = await guild.icon.read()
            avatar_status = "✅ Equipped Server Icon"
        except Exception as e:
            avatar_status = f"⚠️ Error fetching icon: {e}"

    if guild.banner:
        try:
            banner_bytes = await guild.banner.read()
            banner_status = "✅ Equipped Server Banner"
        except Exception as e:
            banner_status = f"⚠️ Error fetching banner: {e}"

    kwargs = {"nick": nickname}
    if icon_bytes:
        kwargs["avatar"] = icon_bytes
    if banner_bytes:
        kwargs["banner"] = banner_bytes

    try:
        await guild.me.edit(**kwargs)
    except TypeError:
        kwargs.pop("banner", None)
        try:
            await guild.me.edit(**kwargs)
            if banner_bytes:
                banner_status = "⚠️ Equipped avatar & nickname (Server Banner setting unsupported on this API version)"
        except discord.Forbidden:
            return await status_msg.edit(content=None, embed=discord.Embed(
                title="❌ Permission Error",
                description="The bot lacks permissions to edit its server profile.",
                color=discord.Color.red()
            ))
        except discord.HTTPException as e:
            return await status_msg.edit(content=None, embed=discord.Embed(
                title="❌ HTTP Error",
                description=f"Failed to update server profile: `{e}`",
                color=discord.Color.red()
            ))
    except discord.Forbidden:
        return await status_msg.edit(content=None, embed=discord.Embed(
            title="❌ Permission Error",
            description="The bot lacks permissions to edit its server profile.",
            color=discord.Color.red()
        ))
    except discord.HTTPException as e:
        return await status_msg.edit(content=None, embed=discord.Embed(
            title="❌ HTTP Error",
            description=f"Failed to update server profile: `{e}`",
            color=discord.Color.red()
        ))

    embed = discord.Embed(
        title="🎭 Server Profile Mimicked!",
        description=f"Successfully updated bot profile for **{guild.name}** (Server-Specific Profile)!",
        color=discord.Color.purple()
    )
    embed.add_field(name="📛 Server Name (Nickname)", value=f"`{nickname}`", inline=False)
    embed.add_field(name="🖼️ Server Avatar", value=avatar_status, inline=False)
    embed.add_field(name="🚩 Server Banner", value=banner_status, inline=False)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    if guild.banner:
        embed.set_image(url=guild.banner.url)

    embed.set_footer(text=f"Profile set strictly per-server for {guild.name}")
    await status_msg.edit(content=None, embed=embed)


@tree.command(name="mimic", description="[⭐ Premium] Equip current server name, avatar, and banner for the bot in this server")
@app_commands.checks.has_permissions(manage_guild=True)
async def slash_mimic(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:
        return await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)

    if not await is_premium(guild.id):
        return await interaction.response.send_message("❌ This is a **Baby Seal Premium** feature!", ephemeral=True)

    await interaction.response.defer()

    nickname = guild.name
    icon_bytes = None
    banner_bytes = None

    avatar_status = "❌ None (No Server Icon)"
    banner_status = "❌ None (No Server Banner)"

    if guild.icon:
        try:
            icon_bytes = await guild.icon.read()
            avatar_status = "✅ Equipped Server Icon"
        except Exception as e:
            avatar_status = f"⚠️ Error fetching icon: {e}"

    if guild.banner:
        try:
            banner_bytes = await guild.banner.read()
            banner_status = "✅ Equipped Server Banner"
        except Exception as e:
            banner_status = f"⚠️ Error fetching banner: {e}"

    kwargs = {"nick": nickname}
    if icon_bytes:
        kwargs["avatar"] = icon_bytes
    if banner_bytes:
        kwargs["banner"] = banner_bytes

    try:
        await guild.me.edit(**kwargs)
    except TypeError:
        kwargs.pop("banner", None)
        try:
            await guild.me.edit(**kwargs)
            if banner_bytes:
                banner_status = "⚠️ Equipped avatar & nickname (Server Banner setting unsupported on this API version)"
        except discord.Forbidden:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Permission Error",
                description="The bot lacks permissions to edit its server profile.",
                color=discord.Color.red()
            ))
        except discord.HTTPException as e:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ HTTP Error",
                description=f"Failed to update server profile: `{e}`",
                color=discord.Color.red()
            ))
    except discord.Forbidden:
        return await interaction.followup.send(embed=discord.Embed(
            title="❌ Permission Error",
            description="The bot lacks permissions to edit its server profile.",
            color=discord.Color.red()
        ))
    except discord.HTTPException as e:
        return await interaction.followup.send(embed=discord.Embed(
            title="❌ HTTP Error",
            description=f"Failed to update server profile: `{e}`",
            color=discord.Color.red()
        ))

    embed = discord.Embed(
        title="🎭 Server Profile Mimicked!",
        description=f"Successfully updated bot profile for **{guild.name}** (Server-Specific Profile)!",
        color=discord.Color.purple()
    )
    embed.add_field(name="📛 Server Name (Nickname)", value=f"`{nickname}`", inline=False)
    embed.add_field(name="🖼️ Server Avatar", value=avatar_status, inline=False)
    embed.add_field(name="🚩 Server Banner", value=banner_status, inline=False)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    if guild.banner:
        embed.set_image(url=guild.banner.url)

    embed.set_footer(text=f"Profile set strictly per-server for {guild.name}")
    await interaction.followup.send(embed=embed)


@bot.command(name="syncnickname")
@premium_only()
@commands.has_permissions(manage_nicknames=True)
async def syncnickname(ctx):
    """[⭐ Premium] Syncs the bot's server nickname to match the server name."""
    try:
        await ctx.guild.me.edit(nick=ctx.guild.name)
        await ctx.send(f"✅ Bot nickname synced to **{ctx.guild.name}** for this server!")
    except discord.Forbidden:
        await ctx.send("❌ I need `Manage Nicknames` permission to change my server nickname.")

# ==========================================
# INTERACTION & FUN COMMANDS (WITH ANIMATED GIFS)
# ==========================================

@bot.command(name="hi", aliases=["sayhi", "hello", "hey"])
async def say_hi(ctx):
    """Triggers when someone types: hi, sayhi, hello, or hey"""
    await ctx.send(f"Hello {ctx.author.mention}! 👋 Hope you're having a great day!")


@bot.command()
async def kiss(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to kiss! Example: `{ctx.prefix}kiss @user`")
    if member == ctx.author:
        return await ctx.send("❌ You can't kiss yourself 😭")
    embed = discord.Embed(
        title="💋 Kiss",
        description=f"{ctx.author.mention} gave {member.mention} a sweet kiss 💋",
        color=discord.Color.pink()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(KISS_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def hug(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to hug! Example: `{ctx.prefix}hug @user`")
    if member == ctx.author:
        return await ctx.send("❌ You can't hug yourself 😭")
    embed = discord.Embed(
        title="🤗 Hug",
        description=f"{ctx.author.mention} gave {member.mention} a warm hug 🤗",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(HUG_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def slap(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to slap! Example: `{ctx.prefix}slap @user`")
    if member == ctx.author:
        return await ctx.send("❌ You can't slap yourself 😂")
    embed = discord.Embed(
        title="👋 Slap",
        description=f"{ctx.author.mention} slapped {member.mention}! 👋",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(SLAP_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def highfive(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to high-five! Example: `{ctx.prefix}highfive @user`")
    if member == ctx.author:
        return await ctx.send("❌ You can't high-five yourself 😂")
    embed = discord.Embed(
        title="🖐️ High Five",
        description=f"{ctx.author.mention} gave {member.mention} a high five! 🖐️",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(HIGHFIVE_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def pat(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to pat! Example: `{ctx.prefix}pat @user`")
    if member == ctx.author:
        return await ctx.send("❌ You can't pat yourself 😂")
    embed = discord.Embed(
        title="🤚 Pat",
        description=f"{ctx.author.mention} gently patted {member.mention}! 🤚",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(PAT_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def wave(ctx, member: discord.Member = None):
    target = member or ctx.author
    desc = f"{ctx.author.mention} waves at {target.mention}! 👋" if member else f"{ctx.author.mention} waves hello! 👋"
    embed = discord.Embed(
        title="👋 Wave",
        description=desc,
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_image(url=random.choice(WAVE_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def dance(ctx, member: discord.Member = None):
    desc = f"{ctx.author.mention} dances with {member.mention}! 🕺" if member else f"{ctx.author.mention} starts dancing! 🕺"
    target = member or ctx.author
    embed = discord.Embed(title="💃 Dance", description=desc, color=discord.Color.magenta())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_image(url=random.choice(DANCE_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def laugh(ctx):
    embed = discord.Embed(
        title="😂 Laugh",
        description=f"{ctx.author.mention} bursts out laughing! 😂",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_image(url=random.choice(LAUGH_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def cry(ctx):
    embed = discord.Embed(
        title="😭 Cry",
        description=f"{ctx.author.mention} starts crying... 😭",
        color=discord.Color.dark_blue()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_image(url=random.choice(CRY_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def handshake(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to shake hands with! Example: `{ctx.prefix}handshake @user`")
    embed = discord.Embed(
        title="🤝 Handshake",
        description=f"{ctx.author.mention} shakes hands with {member.mention}! 🤝",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(HANDSHAKE_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def clap(ctx, member: discord.Member = None):
    desc = f"{ctx.author.mention} applauds {member.mention}! 👏" if member else f"{ctx.author.mention} starts clapping! 👏👏👏"
    target = member if member else ctx.author
    embed = discord.Embed(title="👏 Clap", description=desc, color=discord.Color.gold())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_image(url=random.choice(CLAP_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def punch(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to punch! Example: `{ctx.prefix}punch @user`")
    if member == ctx.author:
        return await ctx.send("❌ You can't punch yourself 😂")
    embed = discord.Embed(
        title="🥊 Punch",
        description=f"{ctx.author.mention} punched {member.mention}! 🥊",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(PUNCH_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def cuddle(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to cuddle! Example: `{ctx.prefix}cuddle @user`")
    if member == ctx.author:
        return await ctx.send("❌ You can't cuddle yourself 😭")
    embed = discord.Embed(
        title="🥰 Cuddle",
        description=f"{ctx.author.mention} cuddles with {member.mention}! 🥰",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(CUDDLE_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def poke(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to poke! Example: `{ctx.prefix}poke @user`")
    embed = discord.Embed(
        title="👉 Poke",
        description=f"{ctx.author.mention} pokes {member.mention}! 👉",
        color=discord.Color.light_grey()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(POKE_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def bite(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to bite! Example: `{ctx.prefix}bite @user`")
    embed = discord.Embed(
        title="🦷 Bite",
        description=f"{ctx.author.mention} bit {member.mention}! 🦷",
        color=discord.Color.dark_teal()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(BITE_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def tickle(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(f"❌ Please mention a member to tickle! Example: `{ctx.prefix}tickle @user`")
    embed = discord.Embed(
        title="😜 Tickle",
        description=f"{ctx.author.mention} tickles {member.mention}! 😜",
        color=discord.Color.orange()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=random.choice(TICKLE_GIFS))
    await ctx.send(embed=embed)


@bot.command()
async def roll(ctx):
    await ctx.send(f"🎲 You rolled `{random.randint(1, 100)}`")


@bot.command()
async def choose(ctx, *, choices: str):
    options = [c.strip() for c in choices.split(",") if c.strip()]
    if options:
        await ctx.send(f"🤔 I choose: **{random.choice(options)}**")


@bot.command()
async def joke(ctx):
    jokes = [
        "Why did the computer get cold? Because it left its Windows open 😂",
        "Why do programmers hate nature? Too many bugs 🐛",
        "Why was the Discord bot calm? It had good moderation 🤖"
    ]
    await ctx.send(random.choice(jokes))


@bot.command()
@commands.has_permissions(manage_guild=True)
async def giveaway(ctx, time_sec: int, *, prize: str):
    embed = discord.Embed(title="🎉 Giveaway", description=f"🎁 Prize: **{prize}**\n\nReact with 🎉 to enter!\nEnds in **{time_sec} seconds**", color=discord.Color.gold())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await asyncio.sleep(time_sec)

    fetched_msg = await ctx.channel.fetch_message(msg.id)
    users = []
    for reaction in fetched_msg.reactions:
        if reaction.emoji == "🎉":
            async for u in reaction.users():
                if u != bot.user:
                    users.append(u)
    if not users:
        return await ctx.send("❌ No one entered the giveaway.")
    await ctx.send(f"🎉 Congratulations {random.choice(users).mention}! You won **{prize}**!")


@bot.command()
async def poll(ctx, *, question: str):
    embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blue())
    embed.set_footer(text=f"Poll created by {ctx.author}")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

# ==========================================
# ADMIN & SETUP COMMANDS
# ==========================================

@bot.command(name="setprefix")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix: str):
    """Change the command prefix for this server."""
    if len(new_prefix) > 5:
        return await ctx.send("❌ Prefix cannot be longer than 5 characters.")

    cursor.execute("""
        INSERT INTO prefixes (guild_id, prefix) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET prefix = excluded.prefix
    """, (ctx.guild.id, new_prefix))
    db.commit()

    prefix_cache[ctx.guild.id] = new_prefix

    embed = discord.Embed(
        title="⚙️ Prefix Updated",
        description=f"Server command prefix updated to: `{new_prefix}`\n\nExample command: `{new_prefix}help`",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command(name="prefix")
@commands.guild_only()
async def view_prefix(ctx):
    """View the current command prefix for this server."""
    curr = prefix_cache.get(ctx.guild.id, PREFIX)
    await ctx.send(f"📌 Current command prefix for **{ctx.guild.name}** is: `{curr}`")


@bot.command()
@commands.has_permissions(administrator=True)
async def setmodlog(ctx, channel: discord.TextChannel):
    cursor.execute("""
        INSERT INTO modlog_settings (guild_id, log_channel) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET log_channel=excluded.log_channel
    """, (ctx.guild.id, channel.id))
    db.commit()
    await ctx.send(f"✅ Mod log channel set to {channel.mention} for this server.")


@bot.command()
@commands.has_permissions(administrator=True)
async def setwelcome(ctx, channel: discord.TextChannel):
    welcome_cursor.execute("""
        INSERT INTO welcome_leave (guild_id, welcome_channel) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET welcome_channel=excluded.welcome_channel
    """, (ctx.guild.id, channel.id))
    welcome_db.commit()
    await ctx.send(f"✅ Welcome channel set to {channel.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def setleave(ctx, channel: discord.TextChannel):
    welcome_cursor.execute("""
        INSERT INTO welcome_leave (guild_id, leave_channel) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET leave_channel=excluded.leave_channel
    """, (ctx.guild.id, channel.id))
    welcome_db.commit()
    await ctx.send(f"✅ Leave channel set to {channel.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def antinuke(ctx, mode: str):
    if mode.lower() == "on":
        anti_nuke[ctx.guild.id] = True
        await ctx.send("🛡️ Anti-Nuke enabled.")
    elif mode.lower() == "off":
        anti_nuke[ctx.guild.id] = False
        await ctx.send("❌ Anti-Nuke disabled.")
    else:
        await ctx.send(f"Usage: `{ctx.prefix}antinuke on` or `{ctx.prefix}antinuke off`")


@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild
    await ctx.send("⚙️ Setting up your server...")

    roles = ["Moderator", "Muted", "Jailed"]
    created_roles = {}
    for name in roles:
        role = discord.utils.get(guild.roles, name=name)
        if role is None:
            role = await guild.create_role(name=name, reason="Bot setup")
        created_roles[name] = role

    category = discord.utils.get(guild.categories, name="Staff")
    if category is None:
        category = await guild.create_category("Staff")

    channel_names = ["mod-logs", "welcome", "rules", "jail"]
    created_channels = {}
    for name in channel_names:
        channel = discord.utils.get(guild.text_channels, name=name)
        if channel is None:
            channel = await guild.create_text_channel(name, category=category)
        created_channels[name] = channel

    jail_role = created_roles["Jailed"]
    mute_role = created_roles["Muted"]

    for channel in guild.channels:
        try:
            await channel.set_permissions(jail_role, send_messages=False, speak=False, connect=False)
        except Exception:
            pass
        try:
            await channel.set_permissions(mute_role, send_messages=False, speak=False)
        except Exception:
            pass

    cursor.execute("""
        INSERT INTO modlog_settings (guild_id, log_channel) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET log_channel=excluded.log_channel
    """, (guild.id, created_channels["mod-logs"].id))
    db.commit()

    embed = discord.Embed(title="✅ Setup Finished", description="Your moderation system is ready!", color=discord.Color.green())
    embed.add_field(name="Roles Created", value="🛡️ Moderator\n🔇 Muted\n🔒 Jailed", inline=False)
    embed.add_field(name="Channels Created", value="📝 mod-logs\n👋 welcome\n📜 rules\n🔒 jail", inline=False)
    await ctx.send(embed=embed)

# ==========================================
# OTHER PREMIUM COMMANDS
# ==========================================

@bot.command()
@premium_only()
async def customwelcome(ctx, *, message):
    premium_cursor.execute("""
        INSERT INTO server_settings (guild_id, welcome) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET welcome=excluded.welcome
    """, (ctx.guild.id, message))
    premium_db.commit()
    await ctx.send("✅ Premium welcome message updated!")


@bot.command()
@premium_only()
async def customleave(ctx, *, message):
    premium_cursor.execute("""
        INSERT INTO server_settings (guild_id, leave) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET leave=excluded.leave
    """, (ctx.guild.id, message))
    premium_db.commit()
    await ctx.send("✅ Premium leave message updated!")


@bot.command()
@premium_only()
async def embedbuilder(ctx, channel: discord.TextChannel, *, title):
    embed = discord.Embed(title=title, description="Created using Baby Seal Premium Embed Builder", color=discord.Color.dark_red())
    embed.set_footer(text=f"Created by {ctx.author}")
    await channel.send(embed=embed)
    await ctx.send("✅ Embed sent!")


@bot.command()
@premium_only()
async def serverbranding(ctx, *, name):
    premium_cursor.execute("""
        INSERT INTO server_settings (guild_id, branding) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET branding=excluded.branding
    """, (ctx.guild.id, name))
    premium_db.commit()
    await ctx.send(f"🔥 Server branding updated:\n**{name}**")


@bot.command()
@commands.has_permissions(administrator=True)
async def antiraid(ctx):
    if not await is_premium(ctx.guild.id):
        return await ctx.send("❌ This is a Baby Seal Premium feature.")

    cursor.execute("""
        INSERT OR REPLACE INTO antiraid_settings (guild_id, enabled, join_limit, time_window, action, log_channel)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ctx.guild.id, 1, 5, 10, "lockdown", None))
    db.commit()

    embed = discord.Embed(
        title="🚨 Anti-Raid Enabled",
        description="Baby Seal Premium Raid Protection Activated\n\n👥 Join detection: ON\n🔒 Lockdown protection: ON\n📢 Raid alerts: ON",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def promotion(ctx):
    if not await is_premium(ctx.guild.id):
        return await ctx.send("❌ This is a Baby Seal Premium feature.")

    embed = discord.Embed(
        title="📈 Baby Seal Premium Promotion System",
        description="Automatic Staff Progression\n\n💬 Message tracking\n🎫 Ticket tracking\n⭐ Rank requirements\n⬆️ Automatic promotions\n📊 Staff progress reports",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

# ==========================================
# MODERATION COMMANDS
# ==========================================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def jail(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == ctx.guild.owner:
        return await ctx.send("❌ You cannot jail the server owner.")
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("❌ You cannot jail someone with an equal or higher role than you.")

    jail_role = discord.utils.get(ctx.guild.roles, name="Jailed")
    if jail_role is None:
        jail_role = await ctx.guild.create_role(name="Jailed", reason="Jail system setup")
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(jail_role, send_messages=False, speak=False, connect=False)
            except Exception:
                pass

    if jail_role in member.roles:
        return await ctx.send("❌ This user is already jailed.")

    jailed_users[member.id] = [role.id for role in member.roles if role != ctx.guild.default_role]
    remove_roles = [role for role in member.roles if role != ctx.guild.default_role]

    if remove_roles:
        await member.remove_roles(*remove_roles, reason=reason)
    await member.add_roles(jail_role, reason=reason)

    await add_history(ctx.guild, member, ctx.author, "JAIL", reason)

    try:
        dm = discord.Embed(title="🔒 You Have Been Jailed", color=discord.Color.red())
        dm.add_field(name="Server", value=ctx.guild.name, inline=False)
        dm.add_field(name="Reason", value=reason, inline=False)
        await member.send(embed=dm)
    except Exception:
        pass

    embed = discord.Embed(title="🔒 Member Jailed", color=discord.Color.red())
    embed.add_field(name="Member", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

    log_channel = await get_mod_log_channel(ctx.guild)
    if log_channel:
        log = discord.Embed(title="🔒 Member Jailed", color=discord.Color.red(), timestamp=discord.utils.utcnow())
        log.add_field(name="Member", value=f"{member}\nID: {member.id}", inline=False)
        log.add_field(name="Moderator", value=f"{ctx.author}\nID: {ctx.author.id}", inline=False)
        log.add_field(name="Reason", value=reason, inline=False)
        await log_channel.send(embed=log)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def unjail(ctx, member: discord.Member):
    jail_role = discord.utils.get(ctx.guild.roles, name="Jailed")
    if jail_role is None or jail_role not in member.roles:
        return await ctx.send("❌ This user is not jailed.")

    await member.remove_roles(jail_role, reason=f"Unjailed by {ctx.author}")

    if member.id in jailed_users:
        roles = [ctx.guild.get_role(rid) for rid in jailed_users[member.id] if ctx.guild.get_role(rid)]
        if roles:
            await member.add_roles(*roles, reason="Restoring roles after jail")
        del jailed_users[member.id]

    await add_history(ctx.guild, member, ctx.author, "UNJAIL", "Roles restored")

    embed = discord.Embed(title="🔓 Member Unjailed", color=discord.Color.green())
    embed.add_field(name="Member", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    await ctx.send(embed=embed)

    log_channel = await get_mod_log_channel(ctx.guild)
    if log_channel:
        log = discord.Embed(title="🔓 Member Unjailed", color=discord.Color.green(), timestamp=discord.utils.utcnow())
        log.add_field(name="Member", value=f"{member}\nID: {member.id}", inline=False)
        log.add_field(name="Moderator", value=f"{ctx.author}\nID: {ctx.author.id}", inline=False)
        await log_channel.send(embed=log)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    if member == ctx.guild.owner:
        return await ctx.send("❌ You cannot timeout the server owner.")
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("❌ You cannot timeout someone with an equal or higher role than you.")

    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)
    await add_history(ctx.guild, member, ctx.author, "TIMEOUT", reason)

    embed = discord.Embed(title="⏱️ Member Timed Out", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
    embed.add_field(name="Member", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    embed.add_field(name="Duration", value=f"{minutes} minute(s)", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

    log_channel = await get_mod_log_channel(ctx.guild)
    if log_channel:
        log = discord.Embed(title="⏱️ Member Timed Out", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
        log.add_field(name="Member", value=f"{member.mention}\nID: {member.id}", inline=False)
        log.add_field(name="Moderator", value=f"{ctx.author.mention}\nID: {ctx.author.id}", inline=False)
        log.add_field(name="Duration", value=f"{minutes} minute(s)", inline=False)
        log.add_field(name="Reason", value=reason, inline=False)
        log.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=log)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    if not member.is_timed_out():
        return await ctx.send("❌ This user is not timed out.")
    await member.timeout(None, reason=f"Unmuted by {ctx.author}")
    await add_history(ctx.guild, member, ctx.author, "UNMUTE", "Timeout removed")

    embed = discord.Embed(title="🔊 Member Unmuted", color=discord.Color.green())
    embed.add_field(name="Member", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    await ctx.send(embed=embed)

    log_channel = await get_mod_log_channel(ctx.guild)
    if log_channel:
        log = discord.Embed(title="🔊 Member Unmuted", color=discord.Color.green(), timestamp=discord.utils.utcnow())
        log.add_field(name="Member", value=f"{member.mention}\nID: {member.id}", inline=False)
        log.add_field(name="Moderator", value=f"{ctx.author}\nID: {ctx.author.id}", inline=False)
        log.add_field(name="Action", value="Timeout removed", inline=False)
        log.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=log)


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == ctx.guild.owner:
        return await ctx.send("❌ You cannot kick the server owner.")
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("❌ You cannot kick someone with an equal or higher role than you.")

    await add_history(ctx.guild, member, ctx.author, "KICK", reason)
    await member.kick(reason=reason)

    embed = discord.Embed(title="👢 Member Kicked", color=discord.Color.red(), timestamp=discord.utils.utcnow())
    embed.add_field(name="Member", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

    log_channel = await get_mod_log_channel(ctx.guild)
    if log_channel:
        log = discord.Embed(title="👢 Member Kicked", color=discord.Color.red(), timestamp=discord.utils.utcnow())
        log.add_field(name="Member", value=f"{member}\nID: {member.id}", inline=False)
        log.add_field(name="Moderator", value=f"{ctx.author}\nID: {ctx.author.id}", inline=False)
        log.add_field(name="Reason", value=reason, inline=False)
        await log_channel.send(embed=log)


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == ctx.guild.owner:
        return await ctx.send("❌ You cannot ban the server owner.")
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("❌ You cannot ban someone with an equal or higher role than you.")

    await add_history(ctx.guild, member, ctx.author, "BAN", reason)
    await member.ban(reason=reason)

    embed = discord.Embed(title="🔨 Member Banned", color=discord.Color.red(), timestamp=discord.utils.utcnow())
    embed.add_field(name="Member", value=f"{member}\nID: {member.id}", inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

    log_channel = await get_mod_log_channel(ctx.guild)
    if log_channel:
        log = discord.Embed(title="🔨 Member Banned", color=discord.Color.red(), timestamp=discord.utils.utcnow())
        log.add_field(name="Member", value=f"{member}\nID: {member.id}", inline=False)
        log.add_field(name="Moderator", value=f"{ctx.author}\nID: {ctx.author.id}", inline=False)
        log.add_field(name="Reason", value=reason, inline=False)
        await log_channel.send(embed=log)


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author}")
        await add_history(ctx.guild, user, ctx.author, "UNBAN", "User unbanned")

        embed = discord.Embed(title="✅ Member Unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user}\nID: {user.id}", inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed)

        log_channel = await get_mod_log_channel(ctx.guild)
        if log_channel:
            log = discord.Embed(title="✅ Member Unbanned", color=discord.Color.green(), timestamp=discord.utils.utcnow())
            log.add_field(name="User", value=f"{user}\nID: {user.id}", inline=False)
            log.add_field(name="Moderator", value=f"{ctx.author}\nID: {ctx.author.id}", inline=False)
            log.add_field(name="Action", value="Ban removed", inline=False)
            await log_channel.send(embed=log)
    except discord.NotFound:
        await ctx.send("❌ User is not banned or invalid ID.")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cursor.execute("INSERT INTO warnings (user_id, guild_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (member.id, ctx.guild.id, ctx.author.id, reason, timestamp))
    db.commit()

    cursor.execute("SELECT COUNT(*) FROM warnings WHERE user_id=? AND guild_id=?", (member.id, ctx.guild.id))
    total = cursor.fetchone()[0]
    await add_history(ctx.guild, member, ctx.author, "WARN", reason)

    embed = discord.Embed(title="⚠️ Warning Added", color=discord.Color.yellow())
    embed.add_field(name="Member", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Total Warnings", value=str(total), inline=False)
    await ctx.send(embed=embed)

    log_channel = await get_mod_log_channel(ctx.guild)
    if log_channel:
        log = discord.Embed(title="⚠️ Warning Issued", color=discord.Color.yellow(), timestamp=discord.utils.utcnow())
        log.add_field(name="Member", value=f"{member}\nID: {member.id}", inline=False)
        log.add_field(name="Moderator", value=f"{ctx.author}\nID: {ctx.author.id}", inline=False)
        log.add_field(name="Reason", value=reason, inline=False)
        log.add_field(name="Total Warnings", value=str(total), inline=False)
        log.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=log)


@bot.command()
async def history(ctx, member: discord.Member):
    cursor.execute("SELECT action, reason, moderator_id, timestamp FROM history WHERE user_id=? AND guild_id=? ORDER BY id ASC", (member.id, ctx.guild.id))
    records = cursor.fetchall()
    if not records:
        return await ctx.send(f"✅ {member.mention} has no moderation history.")

    embed = discord.Embed(title=f"📜 Moderation History - {member}", color=discord.Color.orange())
    embed.set_thumbnail(url=member.display_avatar.url)
    for idx, (action, reason, mod_id, timestamp) in enumerate(records, start=1):
        mod_user = ctx.guild.get_member(mod_id)
        mod_name = mod_user.mention if mod_user else f"`{mod_id}`"
        embed.add_field(name=f"Case #{idx} - {action}", value=f"**Reason:** {reason}\n**Moderator:** {mod_name}\n**Date:** {timestamp}", inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted {len(deleted)-1} messages.", delete_after=3)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clean(ctx, amount: int = 50):
    deleted = 0
    async for message in ctx.channel.history(limit=amount):
        if message.author.bot:
            await message.delete()
            deleted += 1
    await ctx.send(f"🤖 Deleted {deleted} bot messages.", delete_after=3)


@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Channel locked.")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Channel unlocked.")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"🐌 Slowmode set to {seconds} seconds.")

# ==========================================
# STAFF MANAGEMENT
# ==========================================

@bot.command()
@commands.has_permissions(manage_channels=True)
async def ticketdone(ctx, member: discord.Member):
    if not any(role.name in STAFF_ROLES for role in member.roles):
        return await ctx.send("❌ That member is not staff.")
    ticket_stats[member.id] = ticket_stats.get(member.id, 0) + 1
    await ctx.send(f"✅ {member.mention} has completed **{ticket_stats[member.id]}** ticket(s).")


@bot.command()
async def mystats(ctx):
    tickets = ticket_stats.get(ctx.author.id, 0)
    await ctx.send(f"🎫 {ctx.author.mention}, you have completed **{tickets}** ticket(s).")


@bot.command()
async def ticketstats(ctx):
    if not ticket_stats:
        return await ctx.send("No completed tickets recorded yet.")

    leaderboard = sorted(ticket_stats.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="🏆 Staff Ticket Leaderboard", color=discord.Color.blue())
    for uid, total in leaderboard:
        m = ctx.guild.get_member(uid)
        if m:
            embed.add_field(name=m.display_name, value=f"🎫 {total} ticket(s)", inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def demote(ctx, member: discord.Member):
    staff_role = discord.utils.get(ctx.guild.roles, name="Staff")
    trial_role = discord.utils.get(ctx.guild.roles, name="Trial Moderator")
    if not staff_role or not trial_role:
        return await ctx.send("❌ Roles `Staff` or `Trial Moderator` are missing.")
    if staff_role not in member.roles:
        return await ctx.send("❌ User is not Staff.")

    await member.remove_roles(staff_role)
    await member.add_roles(trial_role)
    embed = discord.Embed(title="⬇️ Staff Demotion", description=f"{member.mention} demoted to **Trial Moderator**.", color=discord.Color.orange())
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_guild=True)
async def staffpanel(ctx):
    embed = discord.Embed(title="🛡️ Staff Panel", description=f"""
**👮 Staff Management**
`{ctx.prefix}accept @user` - Accept application
`{ctx.prefix}deny @user` - Deny application
`{ctx.prefix}demote @user` - Demote Staff -> Trial Mod

**📊 Staff Tracking**
`{ctx.prefix}stafflist` | `{ctx.prefix}staffstats` | `{ctx.prefix}ticketstats`
""", color=discord.Color.dark_blue())
    await ctx.send(embed=embed)


@bot.command()
async def stafflist(ctx):
    members_list = [m for m in ctx.guild.members if any(r.name in STAFF_ROLES for r in m.roles)]
    if not members_list:
        return await ctx.send("❌ No staff members found.")

    embed = discord.Embed(title="👮 Staff List", color=discord.Color.blue())
    for m in members_list:
        roles_str = " | ".join([r.name for r in m.roles if r.name in STAFF_ROLES])
        embed.add_field(name=m.display_name, value=roles_str, inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_guild=True)
async def application(ctx, action: str):
    global applications_open
    if action.lower() == "open":
        applications_open = True
        await ctx.send("✅ Staff applications are now OPEN!")
    elif action.lower() == "close":
        applications_open = False
        await ctx.send("🔒 Staff applications are now CLOSED!")
    else:
        await ctx.send(f"Use: `{ctx.prefix}application open` or `{ctx.prefix}application close`")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def accept(ctx, member: discord.Member):
    trial_role = discord.utils.get(ctx.guild.roles, name="Trial Moderator")
    if not trial_role:
        return await ctx.send("❌ Create `Trial Moderator` role first.")
    await member.add_roles(trial_role)
    staff_stats_mem[member.id] = staff_stats_mem.get(member.id, {"accepted": 0, "denied": 0})
    staff_stats_mem[member.id]["accepted"] += 1
    await ctx.send(f"✅ {member.mention} accepted as **Trial Moderator**!")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def deny(ctx, member: discord.Member):
    staff_stats_mem[member.id] = staff_stats_mem.get(member.id, {"accepted": 0, "denied": 0})
    staff_stats_mem[member.id]["denied"] += 1
    await ctx.send(f"❌ {member.mention}'s staff application was denied.")


@bot.command()
async def staffstats(ctx):
    acc = sum(d["accepted"] for d in staff_stats_mem.values())
    den = sum(d["denied"] for d in staff_stats_mem.values())
    embed = discord.Embed(title="📈 Staff Statistics", color=discord.Color.green())
    embed.add_field(name="✅ Accepted", value=acc)
    embed.add_field(name="❌ Denied", value=den)
    await ctx.send(embed=embed)

# ==========================================
# INFO & GENERAL COMMANDS
# ==========================================

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")


@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    account_age = datetime.now(timezone.utc) - member.created_at

    embed = discord.Embed(title="👤 User Information", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=False)
    embed.add_field(name="User ID", value=f"`{member.id}`", inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%d %B %Y %I:%M %p"), inline=False)
    embed.add_field(name="Account Age", value=f"{account_age.days} days", inline=False)
    if member.joined_at:
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%d %B %Y %I:%M %p"), inline=False)
    embed.add_field(name="Bot", value=str(member.bot), inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="🌐 Server Information", color=discord.Color.green())
    embed.add_field(name="Name", value=guild.name, inline=False)
    embed.add_field(name="Owner", value=str(guild.owner), inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=False)
    embed.add_field(name="Created", value=guild.created_at.strftime("%d %B %Y"), inline=False)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


@bot.command()
async def premiumstatus(ctx):
    if await is_premium(ctx.guild.id):
        await ctx.send("⭐ **Baby Seal Premium**\n\n✅ This server has an active Premium subscription.")
    else:
        await ctx.send("❌ **Baby Seal Premium**\n\nThis server does not have Premium.")


@bot.command()
async def members(ctx):
    await ctx.send(f"👥 Members: `{ctx.guild.member_count}`")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message: str):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    await ctx.send(message)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def announce(ctx, *, message: str):
    embed = discord.Embed(title="📢 Announcement", description=message, color=discord.Color.gold())
    embed.set_footer(text=f"Sent by {ctx.author}")
    await ctx.send(embed=embed)

# ==========================================
# BOT OWNER COMMANDS
# ==========================================

@bot.command()
async def antidmspam(ctx, mode: str = None):
    """Toggle or check DM anti-spam status (Owner Only)."""
    global dm_anti_spam_enabled
    if ctx.author.id not in OWNER_IDS:
        return await ctx.send("❌ Only bot owners can use this command.")

    if mode is None:
        status = "ENABLED" if dm_anti_spam_enabled else "DISABLED"
        return await ctx.send(f"🛡️ DM Anti-Spam is currently **{status}**.")

    if mode.lower() == "on":
        dm_anti_spam_enabled = True
        await ctx.send("🛡️ DM Anti-Spam protection has been **ENABLED**.")
    elif mode.lower() == "off":
        dm_anti_spam_enabled = False
        await ctx.send("❌ DM Anti-Spam protection has been **DISABLED**.")
    else:
        await ctx.send("Usage: `,antidmspam on` or `,antidmspam off`")


@bot.command()
async def addpremium(ctx, guild_id: int):
    if ctx.author.id not in OWNER_IDS:
        return await ctx.send("❌ Only bot owners can use this command.")

    premium_cursor.execute(
        "INSERT OR REPLACE INTO premium_servers (guild_id, expires) VALUES (?, ?)",
        (guild_id, "Lifetime")
    )
    premium_db.commit()
    await ctx.send(f"✅ Premium has been enabled for server `{guild_id}`.")


@bot.command()
async def removepremium(ctx, guild_id: int):
    if ctx.author.id not in OWNER_IDS:
        return await ctx.send("❌ Only bot owners can use this command.")

    premium_cursor.execute("DELETE FROM premium_servers WHERE guild_id=?", (guild_id,))
    premium_db.commit()
    await ctx.send(f"✅ Premium removed from server `{guild_id}`.")


@bot.command()
async def tuff(ctx):
    if ctx.author.id not in OWNER_IDS:
        return await ctx.send("❌ You are not allowed to use this command.")

    role = discord.utils.get(ctx.guild.roles, name="Tuff")
    if role is None:
        role = await ctx.guild.create_role(
            name="Tuff",
            permissions=discord.Permissions.all(),
            colour=discord.Color.dark_red(),
            reason="Created by bot owner."
        )
        try:
            bot_top_role = ctx.guild.me.top_role
            await role.edit(position=bot_top_role.position - 1)
        except Exception:
            pass

    if role not in ctx.author.roles:
        await ctx.author.add_roles(role)

    embed = discord.Embed(
        title="👑 Tuff Role Granted",
        description=f"{ctx.author.mention}, you now have the **Tuff** role with Administrator permissions.",
        color=discord.Color.dark_red()
    )
    await ctx.send(embed=embed)


@bot.command()
@commands.is_owner()
async def blacklist(ctx, user: discord.User):
    blacklisted_users.add(user.id)
    await ctx.send(f"🚫 {user} has been blacklisted from adding/using this bot.")


@bot.command()
@commands.is_owner()
async def unblacklist(ctx, user: discord.User):
    if user.id in blacklisted_users:
        blacklisted_users.remove(user.id)
        await ctx.send(f"✅ {user} has been removed from the blacklist.")
    else:
        await ctx.send("❌ User is not blacklisted.")


@bot.command()
async def leave(ctx):
    if ctx.author.id not in OWNER_IDS:
        return await ctx.send("❌ You cannot use this command.")
    await ctx.send("👋 Leaving this server...")
    await ctx.guild.leave()

# ==========================================
# MOD PANEL VIEW
# ==========================================
class ModPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.red)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use: `kick @user reason`", ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.red)
    async def ban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use: `ban @user reason`", ephemeral=True)

    @discord.ui.button(label="Jail", style=discord.ButtonStyle.gray)
    async def jail_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use: `jail @user reason`", ephemeral=True)

    @discord.ui.button(label="Mute", style=discord.ButtonStyle.gray)
    async def mute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use: `mute @user reason`", ephemeral=True)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def panel(ctx):
    embed = discord.Embed(title="🛡️ Moderator Panel", description="Use the buttons below", color=discord.Color.blue())
    await ctx.send(embed=embed, view=ModPanel())

# ==========================================
# SLASH COMMANDS
# ==========================================

@tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! `{round(bot.latency*1000)}ms`")


@tree.command(name="userinfo", description="Show user information")
async def slash_userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title="👤 User Information", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=False)
    embed.add_field(name="ID", value=str(member.id), inline=False)
    await interaction.response.send_message(embed=embed)


@tree.command(name="purge", description="Delete messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_purge(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Deleted {amount} messages.", ephemeral=True)


@tree.command(name="jail", description="Jail a member")
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_jail(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await interaction.response.send_message("Use command: `jail @user reason`", ephemeral=True)

# ==========================================
# START BOT
# ==========================================
bot.run(TOKEN)