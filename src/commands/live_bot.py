import os
from urllib.parse import urlparse

import discord
from discord import app_commands
from discord.ext import commands

# ============================================================
# DISCORD LIVE ANNOUNCEMENT BOT
# ============================================================
# 1. Install:  pip install -U discord.py
# 2. Set your bot token as an environment variable named DISCORD_TOKEN
# 3. Optional: set DISCORD_GUILD_ID to your server ID for instant slash-command sync
# 4. Run: python live_bot.py
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")  # Optional, but recommended for testing

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is not set. Set it to your Discord bot token before starting the bot."
    )

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def platform_info(link: str):
    host = urlparse(link).netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]

    if "twitch.tv" in host:
        return "Twitch", "🟣"
    if "youtube.com" in host or "youtu.be" in host:
        return "YouTube", "🔴"
    if "kick.com" in host:
        return "Kick", "🟢"
    if "tiktok.com" in host:
        return "TikTok", "⚫"
    if "facebook.com" in host:
        return "Facebook", "🔵"
    return "Live Stream", "🔴"


class LiveView(discord.ui.View):
    def __init__(self, link: str):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Watch Live",
                emoji="🔴",
                style=discord.ButtonStyle.link,
                url=link,
            )
        )


@bot.event
async def on_ready():
    # Sync slash commands. If GUILD_ID is set, sync immediately to that server.
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Logged in as {bot.user} ({bot.user.id})")
            print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}.")
        else:
            synced = await bot.tree.sync()
            print(f"Logged in as {bot.user} ({bot.user.id})")
            print(f"Synced {len(synced)} global command(s). Global commands can take time to appear.")
    except Exception as exc:
        print(f"Slash-command sync failed: {exc}")


@bot.tree.command(name="live", description="Announce that you are live and share your stream.")
@app_commands.describe(link="The full URL of your live stream")
@app_commands.checks.has_permissions(administrator=True)
async def live(interaction: discord.Interaction, link: str):
    link = link.strip()

    if not valid_url(link):
        await interaction.response.send_message(
            "❌ Please provide a valid link starting with `https://` or `http://`.",
            ephemeral=True,
        )
        return

    platform, icon = platform_info(link)
    server_name = interaction.guild.name if interaction.guild else "Our Server"

    embed = discord.Embed(
        title=f"{icon} WE ARE LIVE!",
        description=(
            "# 🔴 The stream is LIVE!\n\n"
            "🔥 **Come hang out and watch the stream!**\n"
            "Don't miss the action — everyone is welcome! 🎉\n\n"
            f"**🎥 Platform:** {platform}\n"
            f"**🎙️ Live by:** {interaction.user.mention}\n\n"
            "👇 **Click the button below to join the live stream!**"
        ),
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow(),
    )
    embed.set_footer(text=f"Live announcement • {server_name}")

    await interaction.response.send_message(embed=embed, view=LiveView(link))


@live.error
async def live_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        message = "🚫 You need **Administrator** permission to use `/live`."
    else:
        print(f"/live error: {repr(error)}")
        message = "❌ I couldn't run `/live`. Check the bot permissions and console for the error."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


bot.run(TOKEN)
