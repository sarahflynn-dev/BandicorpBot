import discord
from discord.ext import commands, tasks
from discord import Intents
import gspread
from google.oauth2 import service_account
import random
import logging
from datetime import datetime, timedelta, timezone
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define intents
intents = Intents.default()
intents.messages = True  # Enable message events
intents.message_content = True  # Required to read message content
intents = discord.Intents.all()
intents.members = True  # Enable the privileged members intent if needed

# Initialize the bot with intents
bot = commands.Bot(command_prefix="&", intents=intents)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file("src/scanner-minigame-bot-a33f53b05aa2.json", scopes=scope)
client = gspread.authorize(creds)
sheet_name = 'Member Lab Points Tracker'
sheet = client.open(sheet_name).sheet1

reset_hour = 0  # Set this to the hour you want to reset the counter (0-23)

# List of genomes for scanning
genomes = [
    'eeEE', 'eeAA', 'EEaa', 'ggH', 'XXyy', 'ee', 'EE', 'aa', 'AA', 'YY', 'nH', 'Nh', 'gg', 'GG', 'gG', 'Gg', 'xyz', 'yy'
]

# Function to pick two random genomes
def pick_two_genomes():
    pick1 = random.choice(genomes)
    pick2 = random.choice(genomes)
    return pick1, pick2

# Function to evaluate the genomes and return a message
def evaluate(pick1, pick2):
    if pick1 == pick2:
        return 'Match found! You got **50<:labpoints:1259438959105413160> Lab Points**!'
    elif pick1 == "xyz" or pick2 == "xyz":
        return 'Anomaly detected. You got **10<:labpoints:1259438959105413160> Lab Points**!'
    else:
        letter_match = any(pick1[i:i+2] in pick2 for i in range(len(pick1) - 1))
        if letter_match:
            return "Recessive duplicates spotted. Let's clean that up! You got **20<:labpoints:1259438959105413160> Lab Points**!"
        else:
            return 'No duplicates were detected. Dr. Laymar gave you **2<:labpoints:1259438959105413160> Lab Points**.'

# Function to check if the counter should be reset
def should_reset_counter(last_reset):
    last_reset_datetime = datetime.strptime(last_reset, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    reset_time_today = datetime(now.year, now.month, now.day, reset_hour)
    
    # Check if last reset was before today
    return last_reset_datetime < reset_time_today

# Function to update Google Sheet with user's points and manage counters
def update_google_sheet(user_id, points_earned, username, increment_colorwaiver_count=False, increment_prizewaiver_count=False, increment_stemcell_count=False,
                        increment_common_myo_count=False, increment_legendary_myo_count=False, decrement_counter=False):
    try:
        cell = sheet.find(str(user_id))
        if cell:
            row = cell.row
            cell_counter = int(sheet.cell(row, 6).value)  # Get current counter value from column F
            last_reset = sheet.cell(row, 5).value  # Get last reset timestamp from column E
        else:
            # Find the next available row starting from row 3
            row = max(len(sheet.col_values(1)) + 1, 3)  # Get the next available row, ensuring it starts at least from row 3
            
            # Update both user_id and username in the next available row
            sheet.update_cell(row, 1, str(user_id))
            sheet.update_cell(row, 2, username)  # Assuming username is stored in column B
        
            # Initialize counter to 0 in column F and set current timestamp in column E
            cell_counter = 0
            last_reset = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sheet.update_cell(row, 6, cell_counter)
            sheet.update_cell(row, 5, last_reset)
        
        # Check if the cell in column A is empty; if so, insert user_id
        if not sheet.cell(row, 1).value:
            sheet.update_cell(row, 1, str(user_id))
        
        current_points = int(sheet.cell(row, 3).value if sheet.cell(row, 3).value else 0)  # Assuming Lab Points are in column C
        new_points = current_points + points_earned
        sheet.update_cell(row, 3, new_points)  # Update points in column C
        
        # Increment or decrement the counter
        if decrement_counter:
            new_cell_counter = cell_counter - 1
        else:
            new_cell_counter = cell_counter + 0
        sheet.update_cell(row, 6, new_cell_counter)  # Update counter in column F
        
        # Update counts for specific items
        if increment_colorwaiver_count:
            current_count = int(sheet.cell(row, 12).value if sheet.cell(row, 12).value else 0)  # Column L for color waiver
            sheet.update_cell(row, 12, current_count + 1)
            print(f"Updated Google Sheet: Incremented color waiver count for {username}")
        elif increment_prizewaiver_count:
            current_count = int(sheet.cell(row, 13).value if sheet.cell(row, 13).value else 0)  # Column M for prize waiver
            sheet.update_cell(row, 13, current_count + 1)
            print(f"Updated Google Sheet: Incremented prize waiver count for {username}")
        elif increment_stemcell_count:
            current_count = int(sheet.cell(row, 7).value if sheet.cell(row, 7).value else 0)  # Column G for stemcell
            sheet.update_cell(row, 7, current_count + 1)
            print(f"Updated Google Sheet: Incremented stemcell count for {username}")
        elif increment_common_myo_count:
            current_count = int(sheet.cell(row, 8).value if sheet.cell(row, 8).value else 0)  # Column H for common MYO
            sheet.update_cell(row, 8, current_count + 1)
            print(f"Updated Google Sheet: Incremented common MYO count for {username}")
        elif increment_legendary_myo_count:
            current_count = int(sheet.cell(row, 9).value if sheet.cell(row, 9).value else 0)  # Column I for legendary MYO
            sheet.update_cell(row, 9, current_count + 1)
            print(f"Updated Google Sheet: Incremented legendary MYO count for {username}")
        else:
            print(f"Updated Google Sheet: Added {points_earned} Lab Points for {username}")

        return last_reset, row  # Return the last reset timestamp and row for informational purposes
    
    except gspread.exceptions.CellNotFound:
        logging.error(f"User ID {user_id} not found in Google Sheet.")
        raise RuntimeError("User ID not found in Google Sheet.")
    except Exception as e:
        logging.error(f"Error updating Google Sheet: {e}")
        raise RuntimeError(f"Error updating Google Sheet: {e}")


    
# Dictionary to keep track of when a user last used the command
user_last_called = {}

# Channel ID where the command is allowed
ALLOWED_CHANNEL_ID = 1260789195522310225


# Event: Bot is ready
@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')

@tasks.loop(hours=24)
async def reset_daily_cooldown():
    global user_last_called
    user_last_called = {}
    print("Cooldown reset!")

@reset_daily_cooldown.before_loop
async def before_reset_daily_cooldown():
    now = datetime.now(timezone.utc)
    next_reset = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    await asyncio.sleep((next_reset - now).total_seconds())

@bot.command()
async def daily(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send(f"Sorry {ctx.author.mention}, this command can only be used in the specified channel.")
        return

    points_earned = 0

    class DailyPicker:
        def __init__(self, items, probabilities):
            self.items = items
            self.probabilities = probabilities
            self.last_picked_date = None
            self.picked_item = None

        def pick_item(self):
            current_date = datetime.now(timezone.utc).date()
            if self.last_picked_date != current_date:
                self.picked_item = random.choices(self.items, weights=self.probabilities)[0]
                self.last_picked_date = current_date
            return self.picked_item

    items = [
        '**1 Color Waiver**',
        '**1 Prize Waiver**',
        '**1 Super Stemcell**',
        '**1 Common MYO**',
        '**1 Legendary MYO**',
        '**1 GenomeX Editor**',
        '**5**<:labpoints:1259438959105413160>',
        '**10**<:labpoints:1259438959105413160>',
        '**20**<:labpoints:1259438959105413160>',
        '**50**<:labpoints:1259438959105413160>',
        '**80**<:labpoints:1259438959105413160>',
        '**200**<:labpoints:1259438959105413160>',
        '**1000**<:labpoints:1259438959105413160>'
    ]
    
    # Define probabilities for each item
    probabilities = [
        0.005,   # Color Waiver
        0.001,   # Prize Waiver
        0.0005,  # Super Stemcell
        0.003,   # Common MYO
        0.0001,  # Legendary MYO
        0.0003,  # GenomeX Editor
        0.5,     # 5 Lab Points
        0.3,     # 10 Lab Points
        0.2,     # 20 Lab Points
        0.1,     # 50 Lab Points
        0.1,     # 80 Lab Points
        0.03,    # 200 Lab Points
        0.002    # 1000 Lab Points
    ]
    
    user_id = ctx.author.id
    now = datetime.now(timezone.utc)

    if user_id in user_last_called and user_last_called[user_id].date() == now.date():
        await ctx.send(f"Sorry {ctx.author.mention}, you've already gotten a prize today. Try again tomorrow.")
    else:
        user_last_called[user_id] = now

        picker = DailyPicker(items, probabilities)
        print(picker) #log check
        picked_item = picker.pick_item()
        print(picked_item) #list item

        if ":labpoints:" in picked_item:
            try:
                # Extract the integer part and strip out non-numeric characters
                points_str = picked_item.split("<")[0].strip('*')  # Remove '*' characters
                points_earned = int(points_str)  # Convert to integer
                update_google_sheet(ctx.author.id, points_earned, ctx.author.name)
                await ctx.send(f"{ctx.author.mention} initiated the randomizer. They got {points_earned}<:labpoints:1259438959105413160>!")
            except ValueError as e:
                print(f"Error extracting points: {e}")
                await ctx.send("An error occurred while processing Lab Points. Please try again later.")
            except Exception as e:
                print(f"Error updating Google Sheet: {e}")
                await ctx.send("An error occurred while updating Lab Points. Please try again later.")
        elif "Color Waiver" in picked_item:
            try:
                update_google_sheet(ctx.author.id, 0, ctx.author.name, increment_colorwaiver_count=True)
                await ctx.send(f"{ctx.author.mention} initiated the randomizer. They got {picked_item}!")
            except Exception as e:
                print(f"Error updating Google Sheet: {e}")
                await ctx.send("An error occurred while updating Lab Points. Please try again later.")
        elif "Prize Waiver" in picked_item:
            try:
                update_google_sheet(ctx.author.id, 0, ctx.author.name, increment_prizewaiver_count=True,)
                await ctx.send(f"{ctx.author.mention} initiated the randomizer. They got {picked_item}!")
            except Exception as e:
                print(f"Error updating Google Sheet: {e}")
                await ctx.send("An error occurred while updating Lab Points. Please try again later.")
        elif "Stemcell" in picked_item:
            try:
                update_google_sheet(ctx.author.id, 0, ctx.author.name, increment_stemcell_count=True)
                await ctx.send(f"{ctx.author.mention} initiated the randomizer. They got {picked_item}!")
            except Exception as e:
                print(f"Error updating Google Sheet: {e}")
                await ctx.send("An error occurred while updating Lab Points. Please try again later.")
        elif "Common MYO" in picked_item:
            try:
                update_google_sheet(ctx.author.id, 0, ctx.author.name, increment_common_myo_count=True)
                await ctx.send(f"{ctx.author.mention} initiated the randomizer. They got {picked_item}!")
            except Exception as e:
                print(f"Error updating Google Sheet: {e}")
                await ctx.send("An error occurred while updating Lab Points. Please try again later.")
        elif "Legendary MYO" in picked_item:
            try:
                update_google_sheet(ctx.author.id, 0, ctx.author.name, increment_legendary_myo_count=True)
                await ctx.send(f"{ctx.author.mention} initiated the randomizer. They got {picked_item}!")
            except Exception as e:
                print(f"Error updating Google Sheet: {e}")
                await ctx.send("An error occurred while updating Lab Points. Please try again later.")


@bot.command()
@commands.has_permissions(administrator=True)
async def random_reset(ctx):
    global user_last_called
    user_last_called = {}
    await ctx.send(f"{ctx.author.mention} has manually reset the daily timer for everyone.")

# Error handling for missing permissions
@random_reset.error
async def random_reset_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to use this command.")



# Command: &scan
@bot.command(name='scan')
async def scan(ctx):
    try:
        last_reset, row = update_google_sheet(ctx.author.id, 0, ctx.author.name)
        if should_reset_counter(last_reset):
            cell_counter = 0
            sheet.update_cell(row, 6, cell_counter)
            sheet.update_cell(row, 5, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            cell_counter = int(sheet.cell(row, 6).value) + 1
            sheet.update_cell(row, 6, cell_counter)
        
        if cell_counter <= 5:
            pick1, pick2 = pick_two_genomes()
            points_earned = calculate_points(pick1, pick2)
            update_google_sheet(ctx.author.id, points_earned, ctx.author.name)
            result_message = evaluate(pick1, pick2)
            await ctx.send(f"You initiated a scan. Result:\n```{pick1}, {pick2}```\n{result_message}")
        else:
            await ctx.send('You are out of scans for today. Come back tomorrow.')
            sheet.update_cell(row, 6, 5)

    except Exception as e:
        logging.error(f"An error occurred in the scan command: {e}")
        logging.error(f"An error occurred while processing your command: {e}")
        await ctx.send('You are out of scans for today. Come back tomorrow.')

# Command: &award
@bot.command(name='award')
@commands.has_role('Mod')  # Check if the user has the "Mod" role
async def award(ctx, user: discord.Member, points: int):
    try:
        update_google_sheet(user.id, points, user.name, decrement_counter=True)
        await ctx.send(f"Awarded {points} points to {user.name}.")

    except Exception as e:
        logging.error(f"An error occurred in the award command: {e}")
        await ctx.send(f"An error occurred while awarding points: {e}")

# Error handling example
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Please check again.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please add a number of points to award.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have the required role to use this command.")
    else:
        logging.error(f"An error occurred: {error}")
        await ctx.send(f"An error occurred: {error}")

# Command: &secret_admin_reset
@bot.command(name='secret_admin_reset')
async def secret_admin_reset(ctx):
    reset_counter()
    await ctx.send('Counter reset to 0 and timestamp file cleared.')
    
# Command: &status
@bot.command(name='status')
async def status(ctx):
    await ctx.send('Genome Scanner is ready to play.')

# Function to calculate points based on result message
def calculate_points(pick1, pick2):
    # Example logic: calculate points based on genomes
    points = 0
    if pick1 == pick2:
        points = 50
    elif pick1 == "xyz" or pick2 == "xyz":
        points = 10
    else:
        letter_match = any(pick1[i:i+2] in pick2 for i in range(len(pick1) - 1))
        if letter_match:
            points = 20
        else:
            points = 2
    return points

# Replace 'your_bot_token' with your actual bot token
bot.run('TOKEN')

#TO EXECUTE python bot.py


