import discord
from discord.ext import commands
from discord import Intents

import gspread
from google.auth import credentials
from google.oauth2 import service_account
from discord import Activity, ActivityType

import subprocess
import os
import random
from datetime import datetime, timedelta

# Define intents
intents = Intents.default()
intents.messages = True  # Enable message events

# Initialize the bot with intents
bot = commands.Bot(command_prefix="&", intents=intents)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file("src/scanner-minigame-bot-a33f53b05aa2.json", scopes=scope)
client = gspread.authorize(creds)
sheet_name = 'Member Lab Points Tracker'

# Constants for file paths and reset timing
counter_file = 'src/counter.txt'
timestamp_file = 'src/timestamp.txt'
reset_hour = 0  # Set this to the hour you want to reset the counter (0-23)

# List of genomes for scanning
genomes = [
    'eeEE', 'eeAA', 'EEaa', 'ggH', 'XXyy', 'ee', 'EE', 'aa', 'AA', 'YY', 'nH', 'Nh', 'gg', 'GG', 'gG', 'Gg', 'xyz', 'yy'
]

# Function to get the current counter value
def get_counter():
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as file:
            return int(file.read())
    return 0

# Function to save the counter value to file
def save_counter(counter):
    with open(counter_file, 'w') as file:
        file.write(str(counter))

# Function to get the last reset time from file or current time
def get_last_reset_time():
    if os.path.exists(timestamp_file):
        with open(timestamp_file, 'r') as file:
            content = file.read().strip()
            if content:
                return datetime.fromisoformat(content)
    
    now = datetime.now()
    save_last_reset_time(now)
    save_counter(0)
    return now

# Function to save the last reset time to file
def save_last_reset_time(timestamp):
    with open(timestamp_file, 'w') as file:
        file.write(timestamp.isoformat())

# Function to determine if the counter should reset based on the time
def should_reset_counter():
    now = datetime.now()
    last_reset_time = get_last_reset_time()
    next_reset_time = last_reset_time.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
    if last_reset_time.hour >= reset_hour:
        next_reset_time += timedelta(days=1)
    return now >= next_reset_time

# Function to reset the counter and timestamp file
def reset_counter():
    save_counter(0)
    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)

# Function to pick two random genomes
def pick_two_genomes():
    pick1 = random.choice(genomes)
    pick2 = random.choice(genomes)
    return pick1, pick2

# Function to evaluate the genomes and return a message
def evaluate(pick1, pick2):
    if pick1 == pick2:
        return 'Match found! You got **50 Lab Points**!'
    elif pick1 == "xyz" or pick2 == "xyz":
        return 'Anomaly detected. You got **10 Lab Points**!'
    else:
        letter_match = any(pick1[i:i+2] in pick2 for i in range(len(pick1) - 1))
        if letter_match:
            return "Recessive duplicates spotted. Let's clean that up! You got **20 Lab Points**!"
        else:
            return 'No duplicates were detected. Dr. Laymar gave you **2 Lab Points**.'


# Function to update Google Sheet with user's points
def update_google_sheet(user_id, points, username):
    sheet = client.open(sheet_name).sheet1
    cell = sheet.find(str(user_id))
    
    if cell:
        row = cell.row
    else:
        # If user_id is not found, find the next empty cell in column A
        row = len(sheet.col_values(1)) + 1  # Get the next available row
        
        # Update both user_id and username in the next available row
        sheet.update_cell(row, 1, str(user_id))
        sheet.update_cell(row, 2, username)  # Assuming username is stored in column B
    
    # Check if the cell in column A is empty; if so, insert user_id
    if not sheet.cell(row, 1).value:
        sheet.update_cell(row, 1, str(user_id))
    
    current_points = int(sheet.cell(row, 3).value) if sheet.cell(row, 3).value else 0  # Assuming Lab Points are in column C
    new_points = current_points + points
    sheet.update_cell(row, 3, new_points)  # Update cell in column C

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Command to scan the genomes and evaluate points
@bot.command(name='scan')
async def scan(ctx):
    if should_reset_counter():
        save_counter(0)
        save_last_reset_time(datetime.now())

    counter = get_counter()
    counter += 1
    save_counter(counter)

    if counter <= 5:
        pick1, pick2 = pick_two_genomes()
        points_earned = calculate_points(pick1, pick2)
        update_google_sheet(ctx.author.id, points_earned, ctx.author.name)
        result_message = evaluate(pick1, pick2)
        await ctx.send(f"You initiated a scan. Result:\n```{pick1}, {pick2}```\n{result_message}")
    else:
        await ctx.send('You are out of scans for today. Come back tomorrow.')


# Command: !secret_admin_reset
@bot.command(name='secret_admin_reset')
async def secret_admin_reset(ctx):
    reset_counter()
    await ctx.send('Counter reset to 0 and timestamp file cleared.')

# Function to calculate points based on result message
def calculate_points(pick1, pick2):
    # Example logic: calculate points based on genomes
    points = 0
    if pick1 == pick2:
        points = 50
    elif pick1 == "xyz" or pick2 == "xyz":
        points = 10f
    else:
        letter_match = any(pick1[i:i+2] in pick2 for i in range(len(pick1) - 1))
        if letter_match:
            points = 20
        else:
            points = 2
    return points


bot.run('BOT_TOKEN')

#python bot.py TO EXECUTE


