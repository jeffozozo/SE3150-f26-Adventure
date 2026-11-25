from object import Object
from player import Player
import sys  # For exiting the game


# Ingredients for Chef Gustav's sandwich: bread, cheese and tomato.
# They all work the same way, so one class handles all of them.
# use_message is what prints when the player uses the ingredient.
class Ingredient(Object):

    def __init__(self, name, description, can_be_gotten, state, visible, use_message):
        super().__init__(name, description, can_be_gotten, state, visible)
        self.use_message = use_message

    def use(self):
        print(self.use_message)


# The jar of pickles. It starts closed (state = "closed").
# Using it opens it. The pickles can only be stacked once it's open.
class Jar(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        if self.state == "closed":
            self.state = "open"
            print("You twist the lid. POP! The jar of pickles is open.")
        else:
            print("The jar is already open. It smells like vinegar.")


# The fridge. It can't be picked up. It starts closed.
# contents is the list of objects hidden inside it.
# Opening it makes everything inside visible, so the player can take them.
class Fridge(Object):

    def __init__(self, name, description, can_be_gotten, state, visible, contents):
        super().__init__(name, description, can_be_gotten, state, visible)
        self.contents = contents

    def use(self):
        if self.state == "closed":
            self.state = "open"
            print("You pull the fridge door open. A cold light flickers on.")
            for item in self.contents:
                item.visible = True
                print(f"Inside you see: {item.name}")
        else:
            print("The fridge is already open.")


# The recipe note on the table. It can't be taken.
# Using it reads the recipe out loud.
class Note(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print(self.description)


# The plate on the table. It can't be taken.
# stack is the list of ingredient names placed on it, bottom to top.
class Plate(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)
        self.stack = []

    def use(self):
        if len(self.stack) == 0:
            print("The plate is empty.")
        else:
            print("On the plate (bottom to top): " + ", ".join(self.stack))


# The prize. Chef Gustav gives it to the player when they serve the right sandwich.
# It remembers which player it belongs to, so it can heal them in any room.
# Eating it adds 25 health and removes it from the inventory.
class Sandwich(Object):

    def __init__(self, name, description, can_be_gotten, state, visible, player):
        super().__init__(name, description, can_be_gotten, state, visible)
        self.player = player

    def use(self):
        self.player.health += 25
        if self in self.player.inventory:
            self.player.inventory.remove(self)
        print("You eat Chef Gustav's masterpiece. It's delicious! You gain 25 health.")


class Room:

    def __init__(self):
        self.objects = []
        self.room_num = 9
        self.description = (
            "You step into an old, dusty kitchen. The air is cold, and it feels haunted.\n"
            "A table sits in the middle of the room, with a plate and a handwritten note on it.\n"
            "Against the wall are a fridge and some cabinets.\n"
            "As you look around, Chef Gustav floats up out of a chair pulled up to the table.\n"
            "There is a doorway to the north, stairs leading up, and a trapdoor in the floor leading down.\n"
        )
        # Ingredients. The bread starts on the counter (visible).
        # The cheese and tomato start hidden in the fridge (visible = False).
        self.bread = Ingredient("Loaf of bread", "A crusty loaf of bread.", True, None, True,
                                "It's bread. It wants to be a sandwich.")
        self.cheese = Ingredient("Block of cheese", "A block of yellow cheese.", True, None, False,
                                 "Smells fine. Probably.")
        self.tomato = Ingredient("Tomato", "A bright red tomato.", True, None, False,
                                 "A perfectly round tomato.")
        self.objects.append(self.bread)
        self.objects.append(self.cheese)
        self.objects.append(self.tomato)

        # The jar of pickles starts closed and hidden in the fridge.
        self.jar = Jar("Jar of pickles", "A glass jar full of pickles.", True, "closed", False)
        self.objects.append(self.jar)

        # The fridge holds the cheese, tomato and jar until it's opened.
        self.fridge = Fridge("Fridge", "An old humming fridge.", False, "closed", True,
                             [self.cheese, self.tomato, self.jar])
        self.objects.append(self.fridge)

        # The recipe note and the plate sit on the table.
        self.note = Note("Recipe note",
                         "In shaky handwriting, the note reads:\n"
                         "  Chef Gustav's Masterpiece (bottom to top)\n"
                         "  1. bread  2. cheese  3. tomato  4. pickles  5. cheese  6. bread",
                         False, None, True)
        self.plate = Plate("Plate", "A chipped white plate. Perfect for a sandwich.", False, None, True)
        self.objects.append(self.note)
        self.objects.append(self.plate)
        
        #this is how you declare your exits. It doesn't matter what room the attach to, I'll worry about that in the global level. 
        self.exits = ["north", "up", "down"]



    def enter(self, player):
        player.current_room = self.room_num

        # step 1 - Print the room description
        self.describe_room()

        # step 2 - make your own command loop - watch carefully about how to parse commands:
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
            else:
                self.unknown_command()

    # Helper functions
    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

    def move(self, direction):
        if direction in ["down", "d", "well"]:
            print("You jump into the well, and your whole body tingles as you slip below the surface of the liquid. > blink <")
            return "down"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return

        if target == "well":
            print("Upon closer inspection, the liquid is not water -- it's pure magic. It seems the well may be a portal to somewhere.")
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
        print("This is the starting room. You probably ought to get the lamp and go down the well.")

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
    
