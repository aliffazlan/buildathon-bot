import discord
from discord.ext import commands
import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

LOG_FOLDER = "logs"
JOIN_DATE_CUTOFF = datetime.datetime(2024, 12, 12, tzinfo=datetime.timezone.utc)

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

LOG_FILENAME = os.path.join(LOG_FOLDER, f"{int(time.time())}.log")

def log(msg: str):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(msg)
    with open(LOG_FILENAME, "a", encoding="utf-8") as log_file:
        log_file.write(f"{now} {msg}\n")
try:
    ROLE_2024_ID = int(os.environ["ROLE_2024_ID"])
    ROLE_2025_ID = int(os.environ["ROLE_2025_ID"])
    SERVER_ID = int(os.environ["SERVER_ID"])
    WALNUTT_ID = int(os.environ["WALNUTT_ID"])
    BOT_TOKEN = os.environ["BOT_TOKEN"]
except KeyError as e:
    raise KeyError(f"Missing environment variable: {e}")


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="pog ", intents=intents)

@bot.event
async def on_ready():
    log("Bot starting")
    await bot.tree.sync()
    log("Bot started")
    log(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    new_role = member.guild.get_role(ROLE_2025_ID)
    if new_role is None:
        log(f"ERROR: Server '{member.guild.name}' does not have a role with ID {ROLE_2025_ID}.")
        return
    try:
        await member.add_roles(new_role)
        log(f"Assigned ROLE_2025_ID to new member {member.display_name} in guild '{member.guild.name}'.")
    except Exception as e:
        log(f"ERROR: assigning ROLE_2025_ID to {member.display_name} in guild '{member.guild.name}': {e}")

async def update_role(member: discord.Member, role_2024: discord.Role, role_2025: discord.Role):    
    result = False
    if member.joined_at and member.joined_at < JOIN_DATE_CUTOFF:
        if role_2024 not in member.roles:
            result = True
            log(f"Added 2024 role to {member.name}")
            await member.add_roles(role_2024)
            
    if role_2025 not in member.roles:
        result = True
        log(f"Added 2025 role to {member.name}")
        await member.add_roles(role_2025)
    return result
        



@bot.tree.command(name="update", description="Update your roles")
async def update(interaction: discord.Interaction):
    try:
        log(f"{interaction.user.name} executed update")
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        role_2024 = interaction.guild.get_role(ROLE_2024_ID)
        role_2025 = interaction.guild.get_role(ROLE_2025_ID)

        if role_2024 is None or role_2025 is None:
            log("ERROR: cannot find role ID")
            await send_error(interaction)
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            log(f"ERROR: could not determine {interaction.user.name} member data")
            await send_error(interaction)
            return

        if member.joined_at is None:
            log(f"ERROR: could not determine {interaction.user.name} join date")
            await send_error(interaction)
            return

        await update_role(member, role_2024, role_2025)
            
        await interaction.response.send_message("Roles updated!", ephemeral=True)
    except Exception as e:
        log(f"ERROR while executing update: {e}")
        if not interaction.response.is_done():
            await send_error(interaction)

@bot.tree.command(
    name="update-all", 
    description="Update all users roles",
)
@discord.app_commands.checks.has_permissions(administrator=True)
async def update_all(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        log(f"{interaction.user.name} executed update-all")
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        role_2024 = interaction.guild.get_role(ROLE_2024_ID)
        role_2025 = interaction.guild.get_role(ROLE_2025_ID)
        if role_2024 is None or role_2025 is None:
            log(f"ERROR: role ID not found")
            await send_error(interaction)
            return
        
        count = 0

        for member in interaction.guild.members:
            result = await update_role(member, role_2024, role_2025)
            count += result
        await interaction.followup.send(f"Updated {count} members roles.")
    except Exception as e:
        log(f"ERROR while executing update-all: {e}")
        if not interaction.response.is_done():
            await send_error(interaction)

async def send_error(interaction: discord.Interaction):
    interaction.response.send_message(f"There was a problem executing that command. Please ask <@{WALNUTT_ID}> for assistance.", ephemeral=True)

bot.run(BOT_TOKEN)