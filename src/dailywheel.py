import random
import datetime


class DailyPicker:
    def __init__(self, items):
        self.items = items
        self.last_picked_date = None
        self.picked_item = None

    def pick_item(self):
        current_date = datetime.date.today()
        if self.last_picked_date != current_date:
            self.picked_item = random.choice(self.items)
            self.last_picked_date = current_date
        return self.picked_item

# Example usage
items = [
    '(1)Color Waiver',
    '(1)Newbie Waiver',
    '(1)Prize Waiver',
    '(1)Super Stemcell',
    '(1)Common MYO',
    '(1)Common MYO',
    '(1)Common MYO',
    '(1)Common MYO',
    '(1)Common MYO',
    '(1)Legendary MYO',
    '(1)GenomeX Editor',
    '(1)GenomeX Editor',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '5<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '20<:labpoints:1259438959105413160>',
    '80<:labpoints:1259438959105413160>',
    '80<:labpoints:1259438959105413160>',
    '80<:labpoints:1259438959105413160>',
    '80<:labpoints:1259438959105413160>',
    '80<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '50<:labpoints:1259438959105413160>',
    '50<:labpoints:1259438959105413160>',
    '50<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '10<:labpoints:1259438959105413160>',
    '200<:labpoints:1259438959105413160>',
    '200<:labpoints:1259438959105413160>',
    '1000<:labpoints:1259438959105413160>'
]

picker = DailyPicker(items)

# Call the function to get the daily item
picked_item = picker.pick_item()
print(f"You initated the randomizer. You got {picked_item}!")