import discord
from discord import app_commands
from discord.ext import commands
from urllib.parse import urlparse


class LiveView(discord.ui.View):
    def __init__(self, link: str):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="🔴 Watch Live",
                style=discord.ButtonStyle.link,
                url=link,
            )
        )


def valid_url(link: str) -> bool:
    try:
        parsed = urlparse(link.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


class Live(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="live",
        description="Announce your live stream to the server."
    )
    @app_commands.describe(link="The link to your live stream")
    @app_commands.checks.has_permissions(administrator=True)
    async def live(self, interaction: discord.Interaction, link: str):
        link = link.strip()

        if not valid_url(link):
            await interaction.response.send_message(
                "❌ Please enter a valid link starting with `https://` or `http://`.",
                ephemeral=True,
            )
            return

        host = urlparse(link).netloc.lower().removeprefix("www.")

        if "twitch.tv" in host:
            platform = "Twitch 🟣"
        elif "youtube.com" in host or "youtu.be" in host:
            platform = "YouTube 🔴"
        elif "kick.com" in host:
            platform = "Kick 💚"
        elif "tiktok.com" in host:
            platform = "TikTok ⚫"
        else:
            platform = "Live Stream 🔴"

        embed = discord.Embed(
            title="🔴 WE ARE LIVE!",
            description=(
                "# 🔥 The stream is LIVE!\n\n"
                "Come hang out, watch the action, and show some support! 🎉\n\n"
                f"**🎥 Platform:** {platform}\n"
                f"**🎙️ Streamer:** {interaction.user.mention}\n\n"
                "### 👇 Click the button below to join the stream!\n"
                "Don't miss out! 🚀"
            ),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )

        embed.set_footer(text="Live announcement")

        await interaction.response.send_message(
            embed=embed,
            view=LiveView(link),
        )

    @live.error
    async def live_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        if isinstance(error, app_commands.MissingPermissions):
            message = "🚫 Only server administrators can use `/live`."
        else:
            message = "❌ Something went wrong while running `/live`."

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Live(bot))
