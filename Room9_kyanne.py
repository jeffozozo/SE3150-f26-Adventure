from object import Object
from player import Player
import sys  # For exiting the game
import random  # For Gustav's random lines


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

    # The correct sandwich, bottom to top.
    RECIPE = ["bread", "cheese", "tomato", "pickles", "cheese", "bread"]

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
        
        # The exits from map_class.txt. North is always open.
        # Up and down are blocked by Chef Gustav until the room is solved.
        self.exits = ["north", "up", "down"]

        # Room state
        self.solved = False   # True once the correct sandwich is served. Stays True.
        self.anger = 0        # Goes up on each wrong serve. On the 3rd, Gustav throws a pan.



    def enter(self, player):
        player.current_room = self.room_num

        # Print the room description and have Gustav greet the player.
        self.describe_room()
        if self.solved:
            print('Gustav: "My friend! Welcome back. The way is open for you."')
        else:
            print('Gustav: "Ah! A guest! Finally, someone to finish my masterpiece!"')

        # The command loop. It keeps going until the player leaves or quits.
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
                if next != None:
                    return next

            elif command_base == "use":
                self.use(other_part, player)

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
                if self.quit_game(player) == "quit":
                    return "quit"

            elif command_base in ["help", "?"]:
                self.show_help()

            elif command_base == "hint":
                self.show_hint()

            # Room 9's own commands
            elif command_base == "stack":
                self.stack(other_part, player)

            elif command_base == "serve":
                self.serve(player)

            elif command_base == "open":
                self.open(other_part, player)

            elif command_base == "eat":
                self.eat(other_part, player)

            elif command_base == "talk":
                self.talk(other_part)

            else:
                self.unknown_command()

    # Helper functions
    # Prints the room description, then any items the player could pick up.
    # Hidden items (visible = False) are skipped. Things that are part of the
    # room, like the fridge and plate, are already in the description.
    def describe_room(self):
        print(self.description)
        for obj in self.objects:
            if obj.visible and obj.can_be_gotten:
                print(f"There is a {obj.name} here.")

    # Returns the direction if the player is allowed to leave that way.
    # Returns None if they can't, so enter() keeps them in the room.
    def move(self, direction):
        # North is always open.
        if direction in ["north", "n"]:
            print("You head out through the doorway to the north.")
            return "north"

        # Up and down are blocked by Chef Gustav until the sandwich is served.
        if direction in ["up", "u", "down", "d"]:
            if not self.solved:
                print("Chef Gustav floats in your way.")
                print('Gustav: "No one leaves my kitchen until the sandwich is perfect!"')
                return None
            if direction in ["up", "u"]:
                print("You climb the stairs. Gustav waves goodbye with a ghostly spatula.")
                return "up"
            print("You lift the trapdoor and climb down into the dark.")
            return "down"

        print("You can't go that way.")
        return None

    def look(self, target, player):
        if target == None or target == "":
            self.describe_room()
            return

        # Things in the room that aren't objects
        if target in ["gustav", "chef", "chef gustav", "ghost"]:
            print("Chef Gustav is a pale, see-through ghost in a tall chef's hat.")
            print("He hovers between you and the stairs, glaring at the empty plate.")
            return
        if target in ["cabinets", "cabinet"]:
            print("The cabinets are full of dusty pots and pans. Gustav keeps glancing at them.")
            return
        if target == "table":
            print("An old wooden table with a plate and a handwritten note on it.")
            return

        # Look for the item in the inventory first, then in the room.
        item = self.get_item_from_inventory(target, player)
        if item == None:
            item = self.get_item_from_object_list(target)
        if item == None:
            print("You don't see that here.")
            return

        print(item.description)
        if item.state != None:
            print(f"The {item.name} is {item.state}.")
        # Looking at the plate also shows what's stacked on it.
        if item == self.plate:
            self.plate.use()

    # Puts an ingredient from the player's inventory on the plate.
    # The ingredient stays in the inventory, so bread and cheese can go on twice.
    def stack(self, item_name, player):
        if item_name == "":
            print("Stack what?")
            return

        item = self.get_item_from_inventory(item_name, player)
        if item == None:
            print(f"You don't have any {item_name}.")
            return

        # What goes on the plate is the ingredient's short name, so the
        # plate's list can be compared straight to the RECIPE.
        if item == self.bread:
            ingredient = "bread"
        elif item == self.cheese:
            ingredient = "cheese"
        elif item == self.tomato:
            ingredient = "tomato"
        elif item == self.jar:
            if self.jar.state != "open":
                print("The jar is closed. You can't get the pickles out.")
                return
            ingredient = "pickles"
        else:
            print(f"Chef Gustav gasps. \"You cannot put a {item.name} in a sandwich!\"")
            return

        self.plate.stack.append(ingredient)
        print(f"You put the {ingredient} on the plate.")
        self.plate.use()

    # Gustav checks the sandwich on the plate against the RECIPE.
    def serve(self, player):
        # Once solved, there are no more sandwiches (or points) to earn.
        if self.solved:
            print("Gustav is already at peace. He doesn't need another sandwich.")
            return

        if len(self.plate.stack) == 0:
            print("There's nothing to serve. The plate is empty.")
            return

        # The right sandwich: the room is solved and the exits open.
        if self.plate.stack == self.RECIPE:
            self.solved = True
            self.plate.stack = []
            player.score += 25
            sandwich = Sandwich("Sandwich",
                                "Chef Gustav's masterpiece. Eating it would restore your health.",
                                True, None, True, player)
            player.inventory.append(sandwich)
            print("Chef Gustav takes one ghostly bite and closes his eyes.")
            print('Gustav: "Magnifique! At last, I can rest... but first, you may pass."')
            print("He wraps the sandwich in paper and hands it to you. You gain 25 points.")
            print("Gustav drifts aside. The stairs up and the trapdoor down are open.")
            return

        # The wrong sandwich: clear the plate and Gustav gets angrier.
        self.plate.stack = []
        self.anger += 1
        print("Gustav stares at the sandwich. It falls apart on the plate.")
        if self.anger == 1:
            print('Gustav: "Non, non, NON! That is not my sandwich!"')
        elif self.anger == 2:
            print('Gustav: "You insult my memory! Read. The. Recipe."')
        else:
            print('Gustav: "ENOUGH!"')
            print("He grabs a frying pan from the cabinets and flings it at you. CLANG!")
            print("You lose 5 health.")
            player.health -= 5
            self.anger = 0

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
        held = self.get_item_from_inventory(item_name, player)
        if held != None:
            print(f"You already have the {held.name}.")
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
        print("Available commands:")
        print("  go / move <direction>, look [item], get / take <item>, drop <item>, use <item>")
        print("  open <item>, stack <ingredient>, serve, eat <item>, talk gustav")
        print("  inventory, stats, hint, help / ?, quit")
        if self.solved:
            print("Exits: north, up, down")
        else:
            print("Exits: north (Gustav is blocking up and down)")

    # The hint changes depending on how far the player has gotten.
    def show_hint(self):
        print('Gustav whispers: "The recipe never lies..."')
        if self.fridge.state == "closed":
            print("Maybe there's something useful in the fridge.")
        elif self.jar.state == "closed":
            print("Those pickles won't get out of that jar by themselves.")
        else:
            print("Read the recipe, take the ingredients, stack them in order, then serve.")

    # "open fridge" and "open jar" work the same as using them.
    def open(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item == None:
            item = self.get_item_from_object_list(item_name)
        if item == self.fridge or item == self.jar:
            item.use()
        else:
            print("You can't open that.")

    # "eat sandwich" works the same as "use sandwich".
    def eat(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item != None and isinstance(item, Sandwich):
            item.use()
        elif item != None:
            print('Gustav: "Do not eat the ingredients! They are for the sandwich!"')
        else:
            print("You don't have anything like that to eat.")

    # Gustav says something random.
    def talk(self, target):
        if target not in ["gustav", "chef", "chef gustav", "ghost"]:
            print("There's no one here by that name. Just Gustav.")
            return
        lines = [
            'Gustav: "I died the night before the grand opening. The sandwich was never finished."',
            'Gustav: "Bread on the bottom. Always bread on the bottom. Even a ghost knows this."',
            'Gustav: "I have haunted this kitchen for 87 years. The cheese is from year 3."',
            'Gustav: "Cooking is love. Also, if you get it wrong, I throw pans."',
        ]
        print(random.choice(lines))

    def unknown_command(self):
        print("You can't do that here. Try something else or type 'help' for options or 'hint' for a clue.")

    # Returns True if what the player typed matches this item's name.
    # The player can type the full name ("loaf of bread") or any one word
    # of it ("bread", "loaf"). The word "of" doesn't count on its own.
    def name_matches(self, item, typed):
        typed = typed.lower().strip()
        full_name = item.name.lower()
        words = full_name.split()
        if typed == full_name:
            return True
        return typed in words and typed != "of"

    def get_item_from_inventory(self, item_name, player):
        for item in player.inventory:
            if self.name_matches(item, item_name):
                return item
        return None

    # Only finds items the player can see. Hidden items (like the
    # cheese before the fridge is opened) are skipped.
    def get_item_from_object_list(self, item_name):
        for item in self.objects:
            if item.visible and self.name_matches(item, item_name):
                return item
        return None
