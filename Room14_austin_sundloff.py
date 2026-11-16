from object import Object
from player import Player

class Pebble(Object):
    def __init__(self):
        super().__init__("pebble", "A small, round, and smooth pebble.", True, None, True)

    def use(self):
        print("You toss the pebble from one hand to another, then back. Looks fun.")

class Room:

    NARRATOR_LINES = [
        "A hole. Just a hole. You can't really see the bottom, but there probably is one. Best to ignore it and move on to another room.",
        "It's just a hole. Nothing has really changed about it, so why pay it more interest?",
        "Don't lean over the ledge like that, you might fall in.",
        "It's a hole, it can't be that interesting. Trust me, I'm trying to find a way to make it sound cooler, but it's just a hole.",
        "...",
        "...",
        "Last chance...",
        "Alright fine. WOWIE ZOWIE! You found the super secret bonus room easter egg where you jump in the hole, find out that it does in fact have a bottom and you break every bone in your body and die instantly. NICE!!!"
    ]

    def __init__(self):
        self.room_num = 14
        self.exits = ["south", "west", "up", "down"]
        self.objects = [Pebble()] #per-room list (not shared between rooms)
        self.hole_attempts = 0 #how many times have you tried to enter the hole?


    def enter(self, player):
        player.current_room = self.room_num
        self.describe_room()

        while True:
            command = input("> ")
            result = self.process_command(command, player)
            if result is not None:
                return result

    def process_command(self, command, player):
        """Handle one command. Returns a direction, "quit", or None to stay in the room."""
        parts = command.lower().strip().split(maxsplit=1)
        if not parts:
            return None
        verb = parts[0]
        target = parts[1] if len(parts) > 1 else ""

        if verb in ["enter", "jump", "climb", "go", "move"] and "hole" in target:
            return self.try_hole(player)
        if verb in ["go", "move"]:
            return self.move(target)
        elif verb == "look":
            self.look(target, player)
        elif verb in ["get", "take"]:
            self.get(target, player)
        elif verb == "drop":
            self.drop(target, player)
        elif verb == "use":
            self.use(target, player)
        elif verb == "inventory":
            player.show_inventory()
        elif verb == "stats":
            player.print_stats()
        elif verb in ["help", "?"]:
            self.show_help()
        elif verb == "hint":
            print("Hint: don't go in the hole.")
        elif verb == "quit":
            return self.quit_game(player)
        else:
            print("You can't do that here. Type 'help' for commands.")
        return None

    def try_hole(self, player):
        # print the line for this attempt, then count it
        print(self.NARRATOR_LINES[self.hole_attempts])
        self.hole_attempts += 1

        # every line except the last one is just a warning
        if self.hole_attempts < len(self.NARRATOR_LINES):
            return None

        # the last line was the death message
        player.health = 0
        player.condition.append("broke every bone")
        # Adventure.py checks player.is_alive() right after we return,
        # so returning any valid exit ends the game
        return "down"

    def describe_room(self):
        print("You are in a plain stone room. In the center of the floor is a big, dark hole.")
        print("An archway leads WEST, a corridor runs SOUTH, a ladder climbs UP,")
        print("and a stone staircase in the corner spirals DOWN.")
        for obj in self.objects:
            print(f"You see a {obj.name} here.")

    def move(self, direction):
        moves = {
            "south": "You walk down the corridor to the south.",
            "west": "You step through the archway to the west.",
            "up": "You climb the ladder.",
            "down": "You take the staircase down. (Not the hole. Good choice.)",
        }
        short = {"s": "south", "w": "west", "u": "up", "d": "down"}
        direction = short.get(direction, direction)

        if direction in moves:
            print(moves[direction])
            return direction
        print("You can't go that way.")
        return None

    def look(self, target, player):
        if target == "":
            self.describe_room()
        elif target == "hole":
            print("It's a hole. It's dark. Stop looking at it.")
        else:
            item = player.get_item(target) or self.find_in_room(target)
            if item is None:
                print(f"There is nothing like {target} to look at.")
            else:
                print(item.description)

    def get(self, target, player):
        item = self.find_in_room(target)
        if item is None:
            print(f"There is no {target} here.")
        elif not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
        else:
            self.objects.remove(item)
            player.inventory.append(item)
            print(f"You take the {item.name}.")

    def drop(self, target, player):
        item = player.get_item(target)
        if item is None:
            print(f"You don't have a {target}.")
        else:
            player.inventory.remove(item)
            self.objects.append(item)
            print(f"You drop the {item.name}.")

    def use(self, target, player):
        item = player.get_item(target) or self.find_in_room(target)
        if item is None:
            print("You can't use that.")
        else:
            item.use()

    def find_in_room(self, name):
        for obj in self.objects:
            if obj.name.lower() == name.lower():
                return obj
        return None

    def show_help(self):
        print("Commands: go/move <direction>, look [thing], get/take, drop, use,")
        print("          inventory, stats, hint, help/?, quit")
        print("Exits: " + ", ".join(self.exits))

    def quit_game(self, player):
        if input("Are you sure? (y/n) ").lower().startswith("y"):
            player.print_stats()
            return "quit"
        return None
