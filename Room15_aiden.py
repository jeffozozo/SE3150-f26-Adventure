from object import Object
from player import Player
import sys  # For exiting the game


# this is how you create a new object. You inherit from class Object and override the 'use' function. 
class Gem(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        # Call the superclass constructor
        super().__init__(name, description, can_be_gotten, state, visible)
        self.state = "glowing"

    def use(self, player):
        if self.state == "dull":
            print("The gem has gone dull.")
        else:
            player.score += 10
            self.state = "dull"
            print("The Gem slowly flares until dying out into a dull green, + 10 score")
        


class Room:

    def __init__(self):
        self.room_num = 15
        self.exits = ["east", "down"]
        self.objects = []
        self.lights = [True, False, True, False, True, False, True, False, True]
        self.solved = False
        self.description = (
            "As you enter you see the exits to the east and stairs that go down.\n"
            "As you cross the threshold of the door you realize it shuts behind you as does the other exit.\n"
            "On the wall you notice there is a panel of lights numbered 1-9.\n"
            "Each light on the panel looks as through you can press each one."
        )



    def enter(self, player):
        player.current_room = self.room_num

        self.describe_room()

        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            if command_base in ["move", "go"]:
                next = self.move(other_part)
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

            elif command_base == "press":
                if other_part in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    self.press(int(other_part))
                else:
                    print("Press which light? Choose a number from 1 to 9, like 'press 5'.")

            else:
                self.unknown_command()

    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

    def move(self, direction):
        if not self.solved:
            print("The exits are sealed.")
            return None
        if direction in ["east", "e"]:
            print("You move east.")
            return "east"
        elif direction in ["down", "d"]:
            print("You move down.")
            return "down"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return

        if target == "panel":
            print("Upon closer inspection, you see that each light is a button. The lights are lit up in this pattern ")
            self.show_pattern()
            return
        
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
    
    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            item = self.get_item_from_object_list(item_name)
        
        if(item == None):
            print("you can't use that.")
            return
        
        item.use(player)
        

    def get(self, item_name, player):

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

        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name} and add it to your inventory.")
        return
    
    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            print(f"You don't have the {item_name}.")
            return
        
        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")
        return 

    def show_inventory(self, player):
        player.show_inventory()

    def show_stats(self, player):
        player.print_stats()

    def press(self, n):
        if n not in range(1, 10):
            print("Invalid light. Choose a number from 1 to 9.")
            return

        if self.solved:
            print("The puzzle is already solved.")
            return

        row, col = divmod(n - 1, 3)

        # Selected light and its four neighbors
        positions = [
            (row, col),
            (row - 1, col),  # Above
            (row + 1, col),  # Below
            (row, col - 1),  # Left
            (row, col + 1)   # Right
        ]

        for r, c in positions:
            if 0 <= r < 3 and 0 <= c < 3:
                index = r * 3 + c
                self.lights[index] = not self.lights[index]

        if self.all_on():
            self.solved = True
            print("You solved the puzzle! The exits unlock!")

            # Update the room description now that the exits are open
            self.description = (
                "All nine lights on the panel glow steadily.\n"
                "The door to the east stands open, and the stairs leading down are clear.\n"
            )

            self.objects.append(
                Gem("Gem", "A mysterious glowing gem.", True, "glowing", True)
            )

        self.show_pattern()

    def show_pattern(self):
        for i in range(0, 9, 3):
            row = []

            for j in range(i, i + 3):
                if self.lights[j]:
                    row.append("+")
                else:
                    row.append("-")

            print(" ".join(row))


    def all_on(self):
        return all(self.lights)

    def quit_game(self, player):
        if input("Are you sure? (y/n) ").lower().startswith('y'):
            player.print_stats()
            return "quit"

    def show_help(self):
        print("Available commands: move, go, look, get, take, drop, inventory, stats, hint, use, press, quit, help")

    def show_hint(self):
        print("Pressing a light twice undoes it. Try pressing the lights that are off.")

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
    
