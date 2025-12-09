import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, Colour
import json
import os

# ---- Persistent config file ----
CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

config = load_config()

# ---- Bot ----
intents = nextcord.Intents.default()
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ===========================
# Utility: Log errors globally
# ===========================
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"[ERROR] event={event}", args, kwargs)

@bot.event
async def on_application_command_error(interaction: Interaction, error):
    print(f"[SLASH ERROR] {error}")
    try:
        await interaction.response.send_message(
            "Internal error occurred.", ephemeral=True
        )
    except:
        pass

# ===========================
# /setup-channel
# ===========================
@bot.slash_command(name="setup-channel", description="Set the verification channel.")
async def setup_channel(interaction: Interaction):
    guild_id = str(interaction.guild.id)
    config[guild_id] = config.get(guild_id, {})
    config[guild_id]["verify_channel"] = interaction.channel.id
    save_config(config)

    await interaction.response.send_message(
        f"Verification channel set to: <#{interaction.channel.id}>",
        ephemeral=True
    )

# ===========================
# /setup-role
# ===========================
@bot.slash_command(name="setup-role", description="Select the role given to verified members.")
async def setup_role(
    interaction: Interaction,
    role: nextcord.Role = SlashOption(
        name="role",
        description="Role to give after verification",
        required=True
    )
):
    guild_id = str(interaction.guild.id)
    config[guild_id] = config.get(guild_id, {})
    config[guild_id]["verify_role"] = role.id
    save_config(config)

    await interaction.response.send_message(
        f"Verification role set to: **{role.name}**",
        ephemeral=True
    )

# ===========================
# Verification Button
# ===========================
class VerifyButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Verify",
        style=nextcord.ButtonStyle.primary,
        emoji="✔️"
    )
    async def verify(self, button, interaction: Interaction):
        await interaction.response.send_message(
            "Well done.",
            ephemeral=True
        )

# ===========================
# /setup-verify
# ===========================
@bot.slash_command(name="setup-verify", description="Deploy the verification message.")
async def setup_verify(interaction: Interaction):

    guild_id = str(interaction.guild.id)

    # check config
    if guild_id not in config:
        await interaction.response.send_message(
            "Missing setup: channel and role must be configured.",
            ephemeral=True
        )
        return

    if "verify_channel" not in config[guild_id]:
        await interaction.response.send_message(
            "Missing setup: /setup-channel has not been run.",
            ephemeral=True
        )
        return

    channel_id = config[guild_id]["verify_channel"]
    channel = interaction.guild.get_channel(channel_id)

    if not channel:
        await interaction.response.send_message(
            "Channel missing or invalid.",
            ephemeral=True
        )
        return

    embed = nextcord.Embed(
        title="Alterra Verification",
        description=(
            "Please complete the verification process to access the server. "
            "This procedure ensures compliance with Alterra protocols."
        ),
        colour=Colour.orange()
    )

    view = VerifyButton()

    await channel.send(embed=embed, view=view)

    await interaction.response.send_message(
        f"Verification message deployed in <#{channel.id}>.",
        ephemeral=True
    )

# ===========================
# Ready event
# ===========================
@bot.event
async def on_ready():
    print(f"[ONLINE] Bot logged in as {bot.user}")


# ===========================
# Run
# ===========================
bot.run(os.getenv("TOKEN"))
