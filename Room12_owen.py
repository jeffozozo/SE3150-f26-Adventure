from object import Object
from player import Player
import sys

#column, holds a list of letters. Use changes active letter.
class column(Object):

    def __init__(self, name, description, can_be_gotten, state, visible,letter_list):
        super().__init__(name, description, can_be_gotten, state, visible)
        self.wheelAR = letter_list
        self.wheeli = 0
        self.letter = letter_list[0]

    def use(self):
        self.wheeli += 1
        if self.wheeli >= len(self.wheelAR):
            self.wheeli = 0
        self.letter = self.wheelAR[self.wheeli]
        self.state = "spun to '" +self.letter+"'"
        print(f"'{self.letter}', the wheel is now spun to {self.letter}")

#magic circle. Used to either provide hints, or solve puzzle, or do nothing if already solved.
class circle(Object):
    def __init__(self, name, description, can_be_gotten, state, visible, columns):
        super().__init__(name, description, can_be_gotten, state, visible)
        self.columns = columns

    def use(self, player):
        # solved beforehand
        if self.state == "solved":
            print("You stepped onto the pressure plate, its sigil is dormant.\nYou step back off.")
            return

        leftLetter = self.columns[0].letter
        midLetter = self.columns[1].letter
        rightLetter = self.columns[2].letter

        solved = (leftLetter == "M") and (midLetter == "A") and (rightLetter == "N")

        if not solved: #puzzle is not solved
            print("You stepped onto the pressure plate, causing its sigil to glow a faint blue and whispers to fill your head:")
            print("'What walks on four legs in the morning, two at noon and three in the evening?'\n")

            if (leftLetter != "M") and (midLetter != "A") and (rightLetter != "N"):#nothing is correct
                print("Nothing else seems to be happening, so you step off. The glow and whispers both fade.")
            else: #1 or 2 are correct
                corrects = []
                if (leftLetter == "M"):
                    corrects.append("the 'M' on the column to your left")
                if (midLetter == "A"):
                    corrects.append("the 'A' on the column to your front")
                if (rightLetter == "N"):
                    corrects.append("the 'N' on the column to your right")

                if len(corrects) == 1: #1 correct
                    print(f"You also spotted {corrects[0]} glowing blue\n")
                if len(corrects) == 2: #2 correct
                    print(f"You also spotted both {corrects[0]} and {corrects[1]} glowing blue\n")

                print("But nothing else seems to be happening, so you step off.")

        if solved: #puzzle has just been solved
            print("You stepped onto the pressure plate, causing its sigil to glow brightly!")
            startHealth = player.health
            player.health = min(player.health + 50, 110) #Heal 50 HP, 10 overhealth
            player.score += 1
            if player.health < 100:
                print("The light seeps into your body as it fades, you feel a bit healthier.")
            elif player.health == 100:
                print("The light seeps into your body as it fades, you feel like new.")
            else:
                print("The light seeps into your body as it fades, you feel better than ever!")
            print(f"With the familiar sound of sliding stone, the exit door opens itself once more.\n +1 Score. +{(player.health-startHealth)} Health.")
            self.state = "solved"
            self.description = "A circular stone pressure plate, inlaid with a dormant arcane sigil. Seems to be out of magic."

class Room:

    def __init__(self):
        self.objects = []
        self.room_num = 12
        self.description = ("You are in a cramped, semicircular room.")

        colleft = column("left column", "A column supporting the left side of the room, there's a wheel embedded in its center.", False, "spun to 'Y'", True,["Y","M","S"])
        colmid = column("middle column", "A column supporting the far side of the room, there's a wheel embedded in its center.", False, "spun to 'C'", True,["C","A","T"])
        colright = column("right column", "A column supporting the right side of the room, there's a wheel embedded in its center.", False, "spun to 'M'", True,["M","X","N"])

        magCirc = circle("pressure plate", "A circular stone pressure plate, inlaid with an arcane sigil. It seems magical. Can be used or moved to.", False, "unsolved?", True, [colleft, colmid, colright])

        self.objects.append(magCirc)
        self.objects.append(colleft)
        self.objects.append(colmid)
        self.objects.append(colright)

        #this is how you declare your exits. It doesn't matter what room the attach to, I'll worry about that in the global level. 
        self.exits = ["east"]



    def enter(self, player):
        player.current_room = self.room_num

        if self.objects[0].state != "solved":
            print("The door you just entered through slams shut behind you! Again...\n")

        self.describe_room()


        # base command loop
        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            #Do the command - You should make helper functions for each of these in your room as well.
            if command_base in ["move", "go"]:
                next = self.move(other_part, player) #modified from base to allow moving to plate to give score
                if(next != None):
                    return next

            elif command_base == "use":
                self.use(other_part,player)

            elif command_base == "look":
                self.look(other_part, player)

            elif command_base in ["get", "take"]:
                self.get(other_part, player)

            elif command_base in ["drop", "put"]:
                self.drop(other_part, player)

            elif command_base == "inventory":
                self.show_inventory(player)

            elif command_base == "stats":
                self.show_stats(player)

            elif command_base == "quit":
                if(self.quit_game(player) == "quit"):
                    return "quit"


            elif command_base in ["help", "?"]:
                self.show_help()

            elif command_base == "hint":
                self.show_hint()
            else:
                self.unknown_command()

    # Helper functions
    def describe_room(self):
        print(self.description)
        solved = (self.objects[0].state == "solved")

        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

        if not solved:
            print("There is a door to the east, currently closed.")
        else: 
            print("There is a open door to the east.")

        leftLetter = self.objects[1].letter
        midLetter = self.objects[2].letter
        rightLetter = self.objects[3].letter

        print("The three columns each have a carved window to a rotatable wheel in their centers. The wheels are inscribed with letters.")
        print(f"From left to right, the wheels on the columns spell out: '{leftLetter+midLetter+rightLetter}'")

    def move(self, direction, player):
        if direction == "east":
            if self.objects[0].state == "solved":
                print("You walk east through the open doorway.")
                return "east"
            else:
                print("You walk into the solid stone door. >bonk<\nIt didn't budge.")
                return None
        elif direction == "pressure plate":
            self.use("pressure plate", player)
            return None
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return

        # Check if the object is in the room or in the player's inventory and print it description and status. You can use this code exactly.
        item = self.get_item_from_inventory(target,player)
        if item == None:
            item = self.get_item_from_object_list(target)
            if item == None:
                print("There is nothing like " + target + " to look at.")
                return

        if target == item.name.lower().strip():
            print(item.description) 
            if(item.state != None): 
                print(f"The {item.name} is {item.state}")                   
            return

            print("looking at", target, "reveals nothing.")
            return

    # you can use this as well. haha get it? use this...
    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            item = self.get_item_from_object_list(item_name)

        #this room only allows you to use the objects in the list or inventory. That is not a global constraint however and you can add whatever use functions you like.
        if(item == None):
            print("you can't use that.")
            return

        if isinstance(item, circle):#pass in player to allow for score and healing
            item.use(player)
        else:
            item.use()


    # this code could also probably be used verbatim
    def get(self, item_name, player):

        # Check if the player already has the item in their inventory
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return

        item = self.get_item_from_object_list(item_name)
        if(item == None):
            print(f"{item_name} is not here.")
            return

        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return

        # Add the object to the player's inventory and remove it from the room
        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name} and add it to your inventory.")
        return

    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            print(f"You don't have the {item_name}.")
            return

        # remove the item from the inventory and put it in the object list
        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")
        return 

    def show_inventory(self, player):
        player.show_inventory()

    def show_stats(self, player):
        player.print_stats()

    def quit_game(self, player):
        if input("Are you sure? (y/n) ").lower().startswith('y'):
            player.print_stats()
            return "quit"

    def show_help(self):
        print("Available commands: move, go, look, get, take, drop, inventory, stats, quit, help")

    def show_hint(self):
        print("The pressure plate does more than just whisper its riddle. It also causes some of the letters to glow... sometimes. Probably a good thing?")

    def unknown_command(self):
        print("You can't do that here. Try something else or type 'help' for options or 'hint' for a clue.")

    def get_item_from_inventory(self, item_name, player):
        for item in player.inventory:
            if item.name.lower() == item_name.lower():  
                return item
        return None    

    def get_item_from_object_list(self, item_name):
        for item in self.objects:
            if item.name.lower() == item_name.lower():
                return item
        return None
