import random
import os
from datetime import datetime, timedelta

# this python version of the script resets every day at 12:00 to allow new rolls.

genomes = [
    'eeEE', 'eeAA', 'EEaa', 'ggH', 'XXyy', 'ee', 'EE', 'aa', 'AA', 'YY', 'nH', 'Nh', 'gg', 'GG', 'gG', 'Gg', 'xyz', 'yy'
]

counter_file = 'counter.txt'
timestamp_file = 'timestamp.txt'
reset_hour = 0  # Set this to the hour you want to reset the counter (0-23)

def get_counter():
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as file:
            return int(file.read())
    return 0

def save_counter(counter):
    with open(counter_file, 'w') as file:
        file.write(str(counter))

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

def save_last_reset_time(timestamp):
    with open(timestamp_file, 'w') as file:
        file.write(timestamp.isoformat())

def should_reset_counter():
    now = datetime.now()
    last_reset_time = get_last_reset_time()
    next_reset_time = last_reset_time.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
    if last_reset_time.hour >= reset_hour:
        next_reset_time += timedelta(days=1)
    return now >= next_reset_time

def pick_two_genomes():
    pick1 = random.choice(genomes)
    pick2 = random.choice(genomes)
    return pick1, pick2

def evaluate(pick1, pick2):
    if pick1 == pick2:
        print(pick1, pick2)
        print('Match found! You got 50 Lab Points!')
    elif pick1 == "xyz" or pick2 == "xyz":
        print(pick1, pick2)
        print('Anomaly detected. You got 10 Lab Points!')
    else:
        # Check for two consecutive matching letters
        letter_match = False
        for i in range(len(pick1) - 1):
            if pick1[i:i+2] in pick2:
                letter_match = True
                break
        if letter_match:
            print(pick1, pick2)
            print("Recessive duplicates spotted. Let's clean that up! You got 20 Lab Points!")
        else:
            print(pick1, pick2)
            print('No duplicates were detected. Dr. Laymar gave you 2 Lab Points.')

def match_roll():
    if should_reset_counter():
        save_counter(0)
        save_last_reset_time(datetime.now())
    
    counter = get_counter()
    counter += 1
    save_counter(counter)
    
    if counter <= 5:
        pick1, pick2 = pick_two_genomes()
        evaluate(pick1, pick2)
    else:
        print('You are out of rolls for today. Come back tomorrow.')

match_roll()
